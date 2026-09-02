import numpy as np
import pandas as pd
import pytest

from app.stats.h3_joint import fisher_combine, joint_test, national_tau_per_window_end, rank_p_value
from app.stats.indicators import kendall_trend, rolling_variance


def test_rank_p_value_matches_hand_computation():
    population = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    # observe = 4 -> 2 valeurs (4, 5) sont >= 4 -> p = 2/5 = 0.4
    assert rank_p_value(4.0, population) == pytest.approx(0.4)


def test_fisher_combine_matches_hand_computation():
    # T = -2 * (ln(0.05) + ln(0.1)) calcule a la main
    expected = -2 * (np.log(0.05) + np.log(0.1))
    assert abs(fisher_combine([0.05, 0.1]) - expected) < 1e-9


def test_joint_test_gives_small_p_when_observed_is_the_historical_extreme():
    rng = np.random.default_rng(0)
    n = 60
    dates = pd.date_range("2000-01-01", periods=n, freq="QS")
    national_tau = pd.Series(rng.normal(size=n), index=dates)
    spatial_i = pd.Series(rng.normal(size=n), index=dates)

    # Place la paire historique la plus extreme sur les deux axes a la fois.
    extreme_idx = 30
    national_tau.iloc[extreme_idx] = 10.0
    spatial_i.iloc[extreme_idx] = 10.0

    result = joint_test(
        observed_national_tau=10.0,
        observed_spatial_i=10.0,
        historical_national_tau=national_tau,
        historical_spatial_i=spatial_i,
    )
    assert result["p_joint"] is not None
    assert result["p_joint"] < 0.05


def test_joint_test_gives_large_p_when_observed_is_typical():
    rng = np.random.default_rng(1)
    n = 60
    dates = pd.date_range("2000-01-01", periods=n, freq="QS")
    national_tau = pd.Series(rng.normal(size=n), index=dates)
    spatial_i = pd.Series(rng.normal(size=n), index=dates)

    result = joint_test(
        observed_national_tau=float(national_tau.median()),
        observed_spatial_i=float(spatial_i.median()),
        historical_national_tau=national_tau,
        historical_spatial_i=spatial_i,
    )
    assert result["p_joint"] is not None
    assert result["p_joint"] > 0.3


def test_national_tau_per_window_end_uses_full_monthly_history_not_just_eval_dates():
    """Regression : la fonction doit utiliser les mois INTERMEDIAIRES d'une fenetre,
    pas seulement les valeurs aux dates d'evaluation (bug trouve et corrige)."""
    rng = np.random.default_rng(3)
    monthly_dates = pd.date_range("2018-01-01", periods=24, freq="MS")
    monthly_series = pd.Series(rng.normal(size=24), index=monthly_dates)

    eval_dates = pd.date_range("2018-09-01", periods=4, freq="QS")  # trimestriel
    window_months = 9
    insee_window = 4

    result = national_tau_per_window_end(monthly_series, eval_dates, window_months, insee_window)

    # Calcul manuel pour la derniere date d'evaluation, en utilisant la SERIE MENSUELLE COMPLETE
    # sur les 9 mois qui precedent -- doit correspondre exactement.
    last_eval = eval_dates[-1]
    expected_window = monthly_series[monthly_series.index <= last_eval].tail(window_months)
    expected_variance = rolling_variance(expected_window, insee_window)
    expected_tau, expected_n = kendall_trend(expected_variance)

    assert result.loc[last_eval] == pytest.approx(expected_tau)
    # Si la fonction se contentait des points trimestriels (le bug), la fenetre
    # n'aurait que 3-4 points au lieu de 9 mois -- verifie que ce n'est pas le cas.
    assert len(expected_window) == window_months


def test_joint_test_excludes_dates_from_null_population():
    rng = np.random.default_rng(2)
    n = 40
    dates = pd.date_range("2000-01-01", periods=n, freq="QS")
    national_tau = pd.Series(rng.normal(size=n), index=dates)
    spatial_i = pd.Series(rng.normal(size=n), index=dates)

    result_all = joint_test(0.0, 0.0, national_tau, spatial_i)
    result_excluded = joint_test(
        0.0, 0.0, national_tau, spatial_i, exclude_dates=(dates[10], dates[15])
    )
    assert result_excluded["n_historical_windows"] == result_all["n_historical_windows"] - 6
