"""Statistique jointe pour H3 -- cahier des charges Helios §5.6.

Calibration par BOOTSTRAP COUPLE PAR PERIODE plutot que par surrogates
synthetiques : pour chaque trimestre historique disponible, on dispose deja
d'une vraie paire (tendance temporelle nationale, indice de Moran spatial)
au meme instant. On compare la paire du phenomene teste a la distribution
empirique de ces paires REELLES -- ce qui preserve automatiquement toute
correlation entre les deux composantes, sans supposer l'independance que
le §5.6 interdit explicitement d'utiliser via le chi carre theorique.

Aucune donnee synthetique n'est fabriquee pour cette etape : la loi nulle
est directement l'historique reel.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .indicators import kendall_trend, rolling_variance


def national_tau_per_window_end(monthly_series: pd.Series, eval_dates: pd.DatetimeIndex, window_months: int, insee_window: int) -> pd.Series:
    """Pour chaque date d'evaluation (typiquement les trimestres ou l'on a
    aussi une valeur spatiale), le tau de Kendall de la variance glissante
    calculee sur les `window_months` mois qui PRECEDENT cette date -- la
    meme mecanique que le test temporel de H1, appliquee glissante sur toute
    l'historique plutot qu'une seule fois sur la fenetre d'un phenomene.

    `monthly_series` garde sa resolution mensuelle complete (pas reechantillonnee
    aux dates d'evaluation) : chaque fenetre glissante a besoin de tous les
    mois intermediaires, pas seulement des points trimestriels.
    """
    monthly_series = monthly_series.sort_index()
    taus = pd.Series(index=eval_dates, dtype=float)

    for end in eval_dates:
        window_values = monthly_series[monthly_series.index <= end].tail(window_months)
        if len(window_values) < window_months or len(window_values) < insee_window + 4:
            continue
        variance_series = rolling_variance(window_values, insee_window)
        tau, n_points = kendall_trend(variance_series)
        if not np.isnan(tau) and n_points >= 4:
            taus.loc[end] = tau
    return taus


def rank_p_value(observed: float, population: np.ndarray, one_sided_increase: bool = True) -> float | None:
    """p-value empirique : proportion de la population au moins aussi extreme
    que la valeur observee. Population = valeurs REELLES historiques, pas
    des substituts generes."""
    valid = population[~np.isnan(population)]
    if len(valid) == 0 or np.isnan(observed):
        return None
    if one_sided_increase:
        return float(np.mean(valid >= observed))
    return float(np.mean(np.abs(valid) >= abs(observed)))


def fisher_combine(p_values: list[float]) -> float:
    """Statistique de Fisher T = -2 * sum(ln(p_i)) -- §5.6 etape 2."""
    clipped = [max(p, 1e-12) for p in p_values]  # evite ln(0)
    return float(-2 * sum(np.log(p) for p in clipped))


def joint_test(
    observed_national_tau: float,
    observed_spatial_i: float,
    historical_national_tau: pd.Series,
    historical_spatial_i: pd.Series,
    exclude_dates: tuple[pd.Timestamp, pd.Timestamp] | None = None,
) -> dict:
    """Calibre T_observe contre la distribution empirique de T calcule sur
    chaque trimestre historique ou les deux composantes sont disponibles.
    """
    aligned = pd.DataFrame({"national_tau": historical_national_tau, "spatial_i": historical_spatial_i}).dropna()

    if exclude_dates is not None:
        start, end = exclude_dates
        aligned = aligned[(aligned.index < start) | (aligned.index > end)]

    if len(aligned) < 10:
        return {
            "p_joint": None,
            "t_observed": None,
            "n_historical_windows": len(aligned),
            "p_temporal_rank": None,
            "p_spatial_rank": None,
        }

    p_temporal_rank = rank_p_value(observed_national_tau, aligned["national_tau"].to_numpy())
    p_spatial_rank = rank_p_value(observed_spatial_i, aligned["spatial_i"].to_numpy())

    if p_temporal_rank is None or p_spatial_rank is None:
        return {
            "p_joint": None,
            "t_observed": None,
            "n_historical_windows": len(aligned),
            "p_temporal_rank": p_temporal_rank,
            "p_spatial_rank": p_spatial_rank,
        }

    t_observed = fisher_combine([p_temporal_rank, p_spatial_rank])

    # Distribution nulle de T : le meme calcul, rang contre rang, pour chaque
    # trimestre historique -- des paires REELLES, pas des tirages synthetiques.
    t_historical = []
    for _, row in aligned.iterrows():
        p_t = rank_p_value(row["national_tau"], aligned["national_tau"].to_numpy())
        p_s = rank_p_value(row["spatial_i"], aligned["spatial_i"].to_numpy())
        if p_t is not None and p_s is not None:
            t_historical.append(fisher_combine([p_t, p_s]))
    t_historical = np.array(t_historical)

    p_joint = float(np.mean(t_historical >= t_observed)) if len(t_historical) else None

    return {
        "p_joint": p_joint,
        "t_observed": t_observed,
        "n_historical_windows": len(aligned),
        "p_temporal_rank": p_temporal_rank,
        "p_spatial_rank": p_spatial_rank,
        "t_historical_mean": float(np.mean(t_historical)) if len(t_historical) else None,
        "t_historical_std": float(np.std(t_historical)) if len(t_historical) else None,
    }
