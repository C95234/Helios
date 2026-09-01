import numpy as np

from app.stats.surrogates import surrogate_trend_test


def test_detects_clear_linear_trend_as_significant():
    rng = np.random.default_rng(7)
    values = np.linspace(0, 1, 60) + rng.normal(scale=0.02, size=60)
    result = surrogate_trend_test(values, n_surrogates=300, seed=1)
    assert result["p_value"] < 0.05
    assert result["significant_at_0_05"] is True


def test_flat_noise_is_not_significant():
    rng = np.random.default_rng(8)
    values = rng.normal(size=60)
    result = surrogate_trend_test(values, n_surrogates=300, seed=2)
    assert result["significant_at_0_05"] is False
