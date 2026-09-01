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
