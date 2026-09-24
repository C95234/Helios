import numpy as np
import pytest

from app.ml_benchmark import (
    SimpleCNN1D,
    _kendall_tau_rows,
    _rolling_ac1_batch,
    _rolling_var_batch,
    build_dataset,
    classical_verdict,
    generate_kuramoto_ramp_series,
    generate_saddle_node_series,
    make_windows,
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


def test_rolling_var_and_ac1_batch_match_reference_implementation():
    # Meme verification que celle faite manuellement avant d'ecrire le module
    # (voir commentaire de _rolling_ac1_batch) : la formule fermee vectorisee
    # doit coincider avec statsmodels.acf / pandas .rolling().var() a la
    # precision machine.
    import pandas as pd
    from app.stats.indicators import rolling_ac1, rolling_variance

    rng = np.random.default_rng(3)
    x = rng.normal(size=60)

    ref_ac1 = rolling_ac1(pd.Series(x), 15).dropna().to_numpy()
    fast_ac1 = _rolling_ac1_batch(x[None, :], 15)[0]
    assert np.max(np.abs(ref_ac1 - fast_ac1)) < 1e-9

    ref_var = rolling_variance(pd.Series(x), 15).dropna().to_numpy()
    fast_var = _rolling_var_batch(x[None, :], 15)[0]
    assert np.max(np.abs(ref_var - fast_var)) < 1e-9


def test_kendall_tau_rows_matches_scipy():
    from scipy.stats import kendalltau

    rng = np.random.default_rng(4)
    batch = rng.normal(size=(10, 46))
    fast = _kendall_tau_rows(batch)
    ref = np.array([kendalltau(np.arange(46), row)[0] for row in batch])
    assert np.max(np.abs(fast - ref)) < 1e-9


def test_classical_verdict_flags_genuine_increasing_trend():
    # Motif construit pour avoir une VRAIE tendance croissante de variance
    # sur la fenetre (pas seulement un niveau eleve, §1.2 : le detecteur
    # teste desormais une tendance, pas un simple seuil) : bruit dont
    # l'amplitude grandit lineairement le long de la fenetre.
    rng = np.random.default_rng(0)
    t = np.linspace(0, 1, 60)
    trend = rng.normal(size=60) * (0.2 + 3 * t)
    assert classical_verdict(trend, n_surrogates=200, seed=0) is True


def test_classical_verdict_rarely_flags_stationary_noise():
    # Bruit stationnaire (pas de vraie tendance) : la grande majorite des
    # fenetres ne doivent pas etre flaguees par le test de significativite
    # (p<0.05 sur variance OU AC1 -- un peu plus que 5% par construction,
    # mais tres loin de systematique).
    n_flagged = 0
    n_total = 30
    for seed in range(n_total):
        rng = np.random.default_rng(1000 + seed)
        window = rng.normal(size=60)
        if classical_verdict(window, n_surrogates=100, seed=seed):
            n_flagged += 1
    assert n_flagged / n_total < 0.3
