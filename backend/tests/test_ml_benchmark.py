import numpy as np
import pytest

from app.ml_benchmark import (
    SimpleCNN1D,
    build_dataset,
    calibrate_variance_threshold,
    classical_verdict,
    generate_kuramoto_ramp_series,
    generate_saddle_node_series,
    make_windows,
    window_tail_variance,
)


def test_saddle_node_tips_true_eventually_escapes():
    for seed in range(5):
        sim = generate_saddle_node_series(seed=seed, tips=True)
        assert sim["t_event"] is not None


def test_saddle_node_tips_false_never_escapes():
    for seed in range(5):
        sim = generate_saddle_node_series(seed=seed, tips=False)
        assert sim["t_event"] is None


def test_kuramoto_tips_true_usually_synchronises():
    n_synced = sum(1 for seed in range(10) if generate_kuramoto_ramp_series(seed=seed, tips=True)["t_event"] is not None)
    assert n_synced >= 8  # majorite, pas 100% -- la synchronisation depend du bruit


def test_kuramoto_tips_false_rarely_synchronises():
    n_synced = sum(1 for seed in range(20) if generate_kuramoto_ramp_series(seed=seed, tips=False)["t_event"] is not None)
    assert n_synced <= 2  # apres rodage (KURAMOTO_BURN_IN) : quasi jamais, contre ~20% avant


def test_kuramoto_tips_false_shows_no_systematic_drift():
    # Avant le rodage, r(t) montait reellement tout au long de la fenetre
    # enregistree meme a couplage fixe (transitoire de relaxation depuis des
    # phases initiales aleatoires) -- verifie que ce n'est plus le cas.
    for seed in range(10):
        sim = generate_kuramoto_ramp_series(seed=seed, tips=False)
        if sim["t_event"] is not None:
            continue
        r = sim["series"]
        early = r[: len(r) // 3].mean()
        late = r[2 * len(r) // 3 :].mean()
        assert abs(late - early) < 0.15  # fluctuation normale, pas une derive systematique


def test_make_windows_labels_match_horizon_fraction():
    # Serie factice, bascule a t_event=100, dt=1 -- fenetre positive seulement
    # dans les derniers 35% de la periode d'approche (horizon_fraction=0.35).
    series = np.arange(120, dtype=float)
    windows = make_windows(series, dt=1.0, t_event=100.0, window_len=10, stride=10, horizon_fraction=0.35)
    for w in windows:
        if w["t_end"] > 100.0:
            pytest.fail("une fenetre apres t_event n'aurait pas du etre incluse")
        expected_positive = 65.0 <= w["t_end"] <= 100.0
        assert w["label"] == (1 if expected_positive else 0)


def test_make_windows_all_negative_when_no_event():
    series = np.arange(120, dtype=float)
    windows = make_windows(series, dt=1.0, t_event=None, window_len=10, stride=10)
    assert all(w["label"] == 0 for w in windows)


def test_build_dataset_shapes_and_balance():
    X, y = build_dataset(n_saddle=6, n_kuramoto=6, seed0=42, window_len=60, stride=5, negative_ratio=4.0)
    assert X.shape[1] == 60
    assert len(X) == len(y)
    n_pos = int(y.sum())
    n_neg = len(y) - n_pos
    assert n_pos > 0
    assert n_neg <= n_pos * 4.0 + 1  # tolerance d'arrondi


def test_cnn_training_reduces_loss():
    X, y = build_dataset(n_saddle=6, n_kuramoto=6, seed0=42, window_len=60, stride=5, negative_ratio=4.0)
    cnn = SimpleCNN1D(window_len=60, seed=0)
    losses = cnn.fit(X, y, epochs=20, seed=0)
    assert losses[-1] < losses[0]


def test_cnn_save_load_round_trip(tmp_path):
    X, y = build_dataset(n_saddle=6, n_kuramoto=6, seed0=42, window_len=60, stride=5, negative_ratio=4.0)
    cnn = SimpleCNN1D(window_len=60, seed=0)
    cnn.fit(X, y, epochs=10, seed=0)
    probs_before = cnn.predict_proba(X[:20])

    checkpoint = tmp_path / "model.pt"
    cnn.save(str(checkpoint))

    reloaded = SimpleCNN1D(window_len=60, seed=1)  # graine differente -- doit quand meme reproduire apres load
    reloaded.load(str(checkpoint))
    probs_after = reloaded.predict_proba(X[:20])

    assert np.allclose(probs_before, probs_after)


def test_cnn_predict_proba_in_bounds():
    X, y = build_dataset(n_saddle=6, n_kuramoto=6, seed0=42, window_len=60, stride=5, negative_ratio=4.0)
    cnn = SimpleCNN1D(window_len=60, seed=0)
    cnn.fit(X, y, epochs=10, seed=0)
    probs = cnn.predict_proba(X[:20])
    assert ((probs >= 0.0) & (probs <= 1.0)).all()


def test_window_tail_variance_matches_hand_computation():
    window = np.concatenate([np.array([1.0, -1.0] * 7 + [0.0]), np.array([5.0, -5.0] * 7 + [0.0])])
    # 15 derniers points : 7x(+5), 7x(-5), 1x0 -- moyenne 0, somme des carres
    # = 14*25 = 350, variance (ddof=1) = 350/14 = 25.0.
    variance = window_tail_variance(window, sub_window=15)
    assert variance == pytest.approx(25.0, rel=1e-6)


def test_classical_verdict_flags_high_tail_variance():
    rng = np.random.default_rng(0)
    window = np.concatenate([rng.normal(scale=0.1, size=30), rng.normal(scale=3.0, size=30)])
    assert classical_verdict(window, dt=1.0, variance_threshold=1.0) is True


def test_classical_verdict_does_not_flag_low_tail_variance():
    rng = np.random.default_rng(1)
    window = rng.normal(scale=0.1, size=60)
    assert classical_verdict(window, dt=1.0, variance_threshold=1.0) is False


def test_calibrate_variance_threshold_rejects_pooled_kind():
    with pytest.raises(ValueError):
        calibrate_variance_threshold(kind="both")


@pytest.mark.parametrize("kind,generator", [("saddle_node", generate_saddle_node_series), ("kuramoto", generate_kuramoto_ramp_series)])
def test_calibrated_threshold_gives_low_false_positive_rate_on_fresh_negatives(kind, generator):
    threshold = calibrate_variance_threshold(n_series=60, percentile=95.0, seed=1, kind=kind)
    assert np.isfinite(threshold) and threshold > 0

    n_flagged = 0
    n_checked = 0
    for seed in range(5000, 5030):
        sim = generator(seed=seed, tips=False)
        if sim["t_event"] is not None:
            continue  # bascule reelle par hasard, exclue
        for w in make_windows(sim["series"], sim["dt"], None, window_len=60, stride=5):
            n_checked += 1
            if classical_verdict(w["window"], sim["dt"], variance_threshold=threshold):
                n_flagged += 1
    # Calibre au 95e percentile -- la grande majorite des fenetres
    # individuelles ne doivent pas etre flaguees (le premier essai, un seuil
    # devine a la main, flaguait 100% des trajectoires de controle sur les
    # deux modeles -- voir docstring du module).
    assert n_flagged / n_checked < 0.2
