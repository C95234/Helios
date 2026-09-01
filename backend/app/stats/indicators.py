"""Indicateurs precurseurs temporels (ralentissement critique) -- cahier des charges Helios §5.1.

Variance glissante et autocorrelation a lag-1 sur une fenetre glissante, calculees
avec pandas pour correspondre exactement (a 1e-6 pres) aux valeurs de reference
pandas/statsmodels -- cf. criteres d'acceptation §11.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from statsmodels.tsa.stattools import acf


def rolling_variance(values: pd.Series, window: int) -> pd.Series:
    if window < 2:
        raise ValueError("La fenetre glissante doit contenir au moins 2 points")
    return values.rolling(window=window, min_periods=window).var(ddof=1)


def _lag1_autocorr(window_values: np.ndarray) -> float:
    """Autocorrelation a lag-1, calculee via statsmodels.tsa.stattools.acf.

    Utilise directement la fonction de reference statsmodels (plutot qu'une
    correlation de Pearson maison) pour garantir la conformite exacte avec
    les valeurs statsmodels exigee au §11 du cahier des charges.
    """
    if len(window_values) < 3 or np.std(window_values) == 0:
        return np.nan
    return float(acf(window_values, nlags=1, fft=False)[1])


def rolling_ac1(values: pd.Series, window: int) -> pd.Series:
    if window < 3:
        raise ValueError("La fenetre glissante doit contenir au moins 3 points pour l'AC1")
    return values.rolling(window=window, min_periods=window).apply(_lag1_autocorr, raw=True)


def kendall_trend(indicator: pd.Series) -> tuple[float, int]:
    """Tau de Kendall entre l'indicateur et le temps (index de position).

    Renvoie (tau, n_points_valides). La significativite de ce tau doit etre
    evaluee contre une distribution nulle de donnees de substitution (§5.4),
    jamais contre la loi asymptotique du tau -- voir stats/surrogates.py.
    """
    from scipy.stats import kendalltau

    clean = indicator.dropna()
    if len(clean) < 4:
        return float("nan"), len(clean)
    tau, _ = kendalltau(np.arange(len(clean)), clean.to_numpy())
    return float(tau), len(clean)


def compute_temporal_indicators(values: pd.Series, window: int) -> dict:
    variance = rolling_variance(values, window)
    ac1 = rolling_ac1(values, window)
    var_tau, var_n = kendall_trend(variance)
    ac1_tau, ac1_n = kendall_trend(ac1)
    return {
        "window": window,
        "variance": variance,
        "ac1": ac1,
        "variance_tau": var_tau,
        "variance_n": var_n,
        "ac1_tau": ac1_tau,
        "ac1_n": ac1_n,
    }
