"""Tests pour la detection de quench (§7ter) -- courants synthetiques
uniquement, aucun appel reseau (meme style que test_kuramoto.py /
test_power_law.py)."""
import numpy as np
import pytest

from app.stats.quench import detect_quench


def _ramp_up_flat_top_ramp_down(t, peak=200.0, t_start=0.0, t_flat=0.3, t_end_ramp=0.35):
    """Tir 'normal' : montee, plateau, descente lente (~10s d'echelle relative
    au pas de temps utilise dans les tests -- pas une disruption)."""
    current = np.zeros_like(t)
    rising = (t >= t_start) & (t < t_flat)
    current[rising] = peak * (t[rising] - t_start) / (t_flat - t_start)
    flat = (t >= t_flat) & (t < t_end_ramp)
    current[flat] = peak
    falling = t >= t_end_ramp
    tail_duration = t[-1] - t_end_ramp
    current[falling] = peak * np.clip(1 - (t[falling] - t_end_ramp) / tail_duration, 0, 1)
    return current


def test_detects_abrupt_quench_after_peak():
    t = np.linspace(0, 0.4, 4000)  # pas ~0.1ms
    current = _ramp_up_flat_top_ramp_down(t, peak=200.0, t_flat=0.3, t_end_ramp=0.32)
    # Force une chute brutale a t=0.32 : courant s'effondre en 1ms au lieu de la descente lente.
    quench_idx = np.searchsorted(t, 0.32)
    current[quench_idx:] = np.where(t[quench_idx:] < 0.321, current[quench_idx:], 5.0)

    result = detect_quench(t, current, drop_fraction=0.5, quench_window_s=0.005)
    assert result["disrupted"] is True
    assert result["t_quench"] is not None
    assert 0.318 < result["t_quench"] < 0.325
    assert result["peak_current"] == pytest.approx(200.0, rel=1e-2)


def test_normal_shot_end_is_not_a_quench():
    # Descente lente sur 5s (t_end_ramp=1 -> queue de 4s) : bien plus lente
    # que la fenetre de detection (5ms) -- ne doit jamais etre classee disruptee.
    t = np.linspace(0, 5, 5000)
    current = _ramp_up_flat_top_ramp_down(t, peak=200.0, t_flat=0.8, t_end_ramp=1.0)
    result = detect_quench(t, current, drop_fraction=0.5, quench_window_s=0.005)
    assert result["disrupted"] is False
    assert result["t_quench"] is None


def test_shot_with_no_real_plasma_current_is_not_disrupted():
    t = np.linspace(0, 1, 1000)
    current = np.full_like(t, 0.5)  # jamais un vrai plasma (bruit/offset)
    result = detect_quench(t, current, min_peak_ka=10.0)
    assert result["disrupted"] is False
    assert result["t_quench"] is None
    assert result["i_peak"] is None


def test_nan_padding_is_ignored():
    t = np.linspace(-1, 1, 2000)
    current = _ramp_up_flat_top_ramp_down(np.clip(t, 0, None), peak=150.0, t_flat=0.5, t_end_ramp=0.55)
    current[t < 0] = np.nan  # padding avant le debut du tir, comme les vraies donnees MAST
    quench_idx = np.searchsorted(t, 0.55)
    current[quench_idx:] = np.where(t[quench_idx:] < 0.552, current[quench_idx:], 3.0)

    result = detect_quench(t, current, drop_fraction=0.5, quench_window_s=0.005)
    assert result["disrupted"] is True
    assert np.all(np.isfinite(result["current"]))  # les NaN doivent avoir ete retires


def test_result_arrays_are_sorted_by_time():
    rng = np.random.default_rng(0)
    t = np.linspace(0, 0.4, 500)
    current = _ramp_up_flat_top_ramp_down(t, peak=100.0, t_flat=0.3, t_end_ramp=0.32)
    shuffle = rng.permutation(len(t))
    result = detect_quench(t[shuffle], current[shuffle])
    assert np.all(np.diff(result["time"]) > 0)
