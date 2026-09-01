import numpy as np
import pandas as pd

from app.stats.surrogates import phase_randomized_surrogate, surrogate_test


def test_phase_surrogate_preserves_variance_but_not_order():
    rng = np.random.default_rng(1)
    values = np.cumsum(rng.normal(size=200))  # serie avec tendance forte
    surrogate = phase_randomized_surrogate(values, np.random.default_rng(2))

    assert surrogate.shape == values.shape
    assert abs(np.var(surrogate) - np.var(values)) / np.var(values) < 0.2
    assert not np.allclose(np.sort(surrogate), np.sort(values))


def test_surrogate_test_detects_strong_trend_as_significant():
    n = 150
    t = np.arange(n)
    # tendance forte et deterministe dans la variance sous-jacente : le bruit
    # croit fortement avec le temps, donc la variance glissante doit aussi croitre.
    rng = np.random.default_rng(3)
    values = pd.Series(rng.normal(scale=1 + t / 30))

    result = surrogate_test(values, window=15, indicator="variance", n_surrogates=200, seed=42)

    assert result["n_surrogates"] == 200
    assert result["p_value"] < 0.05
    assert result["significant_at_0_05"] is True


def test_surrogate_test_on_flat_noise_is_not_significant():
    rng = np.random.default_rng(4)
    values = pd.Series(rng.normal(size=150))  # pas de tendance

    result = surrogate_test(values, window=15, indicator="variance", n_surrogates=200, seed=5)

    assert result["p_value"] > 0.05
    assert result["significant_at_0_05"] is False
