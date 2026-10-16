import numpy as np
import pandas as pd
import pytest
from statsmodels.tsa.stattools import acf

from app.stats.indicators import rolling_ac1, rolling_variance


@pytest.fixture
def sample_series() -> pd.Series:
    rng = np.random.default_rng(0)
    return pd.Series(rng.normal(size=80))


def test_rolling_variance_matches_pandas_reference(sample_series):
    window = 10
    result = rolling_variance(sample_series, window)
    expected = sample_series.rolling(window=window).var(ddof=1)
    pd.testing.assert_series_equal(result, expected, atol=1e-9)


def test_rolling_ac1_matches_statsmodels_reference(sample_series):
    window = 10
    result = rolling_ac1(sample_series, window)
    for end in range(window - 1, len(sample_series)):
        chunk = sample_series.iloc[end - window + 1 : end + 1].to_numpy()
        expected = acf(chunk, nlags=1, fft=False)[1]
        assert abs(result.iloc[end] - expected) < 1e-6


def test_rolling_variance_requires_window_of_2():
    with pytest.raises(ValueError):
        rolling_variance(pd.Series([1.0, 2.0]), window=1)


def test_rolling_ac1_requires_window_of_3():
    with pytest.raises(ValueError):
        rolling_ac1(pd.Series([1.0, 2.0, 3.0]), window=2)


# -- AC1 glissant vectorise : equivalence avec l'implementation de reference (statsmodels
# -- par fenetre, via pandas.rolling.apply) -- l'ancienne etait ~100x plus lente, ce qui
# -- limitait les tests par donnees de substitution a 50-60 surrogats (Journal §15).

from app.stats.indicators import _lag1_autocorr  # noqa: E402


def _reference_rolling_ac1(values, window):
    return values.rolling(window=window, min_periods=window).apply(_lag1_autocorr, raw=True)


@pytest.mark.parametrize("window", [3, 5, 12, 50])
def test_rolling_ac1_matches_statsmodels_reference_on_random_series(window):
    rng = np.random.default_rng(window)
    s = pd.Series(np.cumsum(rng.normal(size=300)) + rng.normal(size=300))
    got, ref = rolling_ac1(s, window), _reference_rolling_ac1(s, window)
    assert got.index.equals(ref.index)
    assert np.array_equal(np.isnan(got), np.isnan(ref))
    assert np.nanmax(np.abs(got.to_numpy() - ref.to_numpy())) < 1e-12


def test_rolling_ac1_handles_constant_windows_and_nan_like_the_reference():
    s = pd.Series([1.0] * 8 + [2.0, 3.0, 5.0, np.nan, 4.0, 6.0, 7.0, 7.0, 7.0, 7.0, 8.0, 1.0, 4.0])
    got, ref = rolling_ac1(s, 4), _reference_rolling_ac1(s, 4)
    assert np.array_equal(np.isnan(got), np.isnan(ref))
    ok = ~np.isnan(ref.to_numpy())
    assert np.allclose(got.to_numpy()[ok], ref.to_numpy()[ok], atol=1e-12)


def test_rolling_ac1_preserves_datetime_index_and_short_series():
    s = pd.Series(np.arange(10.0) ** 1.5, index=pd.date_range("2020-01-01", periods=10))
    assert rolling_ac1(s, 4).index.equals(s.index)
    short = pd.Series([1.0, 2.0])
    assert rolling_ac1(short, 5).isna().all() and len(rolling_ac1(short, 5)) == 2
