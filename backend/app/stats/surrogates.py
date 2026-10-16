"""Test de significativite par donnees de substitution -- cahier des charges Helios §5.4.

Methode standard de la litterature EWS (Dakos et al., 2012) : le tau de Kendall
observe entre un indicateur precurseur et le temps est compare a la distribution
du meme tau calcule sur des series de substitution qui detruisent la structure
temporelle (tendance) tout en preservant le spectre de puissance (donc
l'autocorrelation "de base" et la variance globale) de la serie d'origine.

Sans ce test, une hausse de variance ou d'AC1 pourrait etre due au hasard
(cahier des charges §5.4).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .indicators import kendall_trend, rolling_ac1, rolling_variance

MIN_SURROGATES_WARNING = 200


def phase_randomized_surrogate(values: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """Surrogate a phase aleatoire (Theiler et al., 1992).

    Preserve le spectre de puissance (donc la variance et la "couleur" du bruit)
    de la serie d'origine tout en detruisant toute tendance ou structure non
    lineaire -- exactement l'hypothese nulle qu'on veut tester au §5.4.
    """
    n = len(values)
    centered = values - values.mean()
    spectrum = np.fft.rfft(centered)
    amplitudes = np.abs(spectrum)
    phases = rng.uniform(0, 2 * np.pi, size=amplitudes.shape)
    phases[0] = 0.0
    if n % 2 == 0:
        phases[-1] = 0.0
    randomized = amplitudes * np.exp(1j * phases)
    surrogate = np.fft.irfft(randomized, n=n)
    return surrogate + values.mean()


def _permutation_p_value(n_at_least_as_extreme: int, n_surrogates: int) -> float:
    """p-value de Monte-Carlo avec plancher standard (Davison & Hinkley 1997 ; North, Curtis &
    Sham 2002) : (1 + k) / (1 + n). Sans le +1, la p-value peut valoir exactement 0 et est
    biaisee vers le bas de ~1/n -- 0.02 pour les 50 surrogats utilises jusqu'ici par Fusion."""
    return float((1 + n_at_least_as_extreme) / (1 + n_surrogates))


def surrogate_test(
    values: pd.Series,
    window: int,
    indicator: str,
    n_surrogates: int = 1000,
    seed: int | None = None,
    one_sided_increase: bool = True,
) -> dict:
    """p-value de la tendance d'un indicateur precurseur contre H0 (donnees de substitution).

    indicator: "variance" ou "ac1".
    """
    if indicator not in ("variance", "ac1"):
        raise ValueError("indicator doit valoir 'variance' ou 'ac1'")

    rolling_fn = rolling_variance if indicator == "variance" else rolling_ac1
    observed_series = rolling_fn(values, window)
    observed_tau, n_points = kendall_trend(observed_series)

    if np.isnan(observed_tau):
        return {
            "indicator": indicator,
            "observed_tau": None,
            "p_value": None,
            "n_surrogates": 0,
            "n_points": n_points,
            "significant_at_0_05": False,
        }

    rng = np.random.default_rng(seed)
    raw_values = values.to_numpy(dtype=float)
    surrogate_taus = np.empty(n_surrogates)
    for i in range(n_surrogates):
        surrogate = phase_randomized_surrogate(raw_values, rng)
        surrogate_series = rolling_fn(pd.Series(surrogate), window)
        tau, _ = kendall_trend(surrogate_series)
        surrogate_taus[i] = tau

    valid = surrogate_taus[~np.isnan(surrogate_taus)]
    if len(valid) == 0:
        p_value = None
    elif one_sided_increase:
        p_value = _permutation_p_value(int(np.sum(valid >= observed_tau)), len(valid))
    else:
        p_value = _permutation_p_value(int(np.sum(np.abs(valid) >= abs(observed_tau))), len(valid))

    return {
        "indicator": indicator,
        "observed_tau": observed_tau,
        "p_value": p_value,
        "n_surrogates": int(len(valid)),
        "n_points": n_points,
        "significant_at_0_05": bool(p_value is not None and p_value < 0.05),
    }


def surrogate_trend_test(
    indicator_values: np.ndarray,
    n_surrogates: int = 500,
    seed: int | None = None,
    one_sided_increase: bool = True,
) -> dict:
    """Meme principe que surrogate_test, mais appliaue directement a une serie deja
    calculee (ex. l'indice de Moran a chaque periode, §5.2) plutot que de la
    deriver d'une fenetre glissante sur une serie brute -- utile quand l'indicateur
    est deja "un point par periode" (une coupe spatiale par trimestre, ici).
    """
    clean = indicator_values[~np.isnan(indicator_values)]
    observed_tau, n_points = kendall_trend(pd.Series(clean))

    if np.isnan(observed_tau) or n_points < 4:
        return {
            "observed_tau": None, "p_value": None, "n_surrogates": 0, "n_points": n_points,
            "significant_at_0_05": False, "p_value_se": None, "borderline": False,
        }

    rng = np.random.default_rng(seed)
    surrogate_taus = np.empty(n_surrogates)
    for i in range(n_surrogates):
        surrogate = phase_randomized_surrogate(clean, rng)
        tau, _ = kendall_trend(pd.Series(surrogate))
        surrogate_taus[i] = tau

    valid = surrogate_taus[~np.isnan(surrogate_taus)]
    if len(valid) == 0:
        p_value = None
    elif one_sided_increase:
        p_value = _permutation_p_value(int(np.sum(valid >= observed_tau)), len(valid))
    else:
        p_value = _permutation_p_value(int(np.sum(np.abs(valid) >= abs(observed_tau))), len(valid))

    # Erreur-type Monte-Carlo de la p-value (binomiale) : tant que 0.05 est a moins de
    # 2 erreurs-types de p, le cote du seuil ou tombe p depend du tirage aleatoire, pas
    # des donnees -- "a la limite" (voir Journal §15 : la p-value "grille" de H2/logements
    # autorisés vaut 0.052, mais passait sous 0.05 dans 38% des tirages a 500 surrogats).
    p_se = float(np.sqrt(p_value * (1 - p_value) / len(valid))) if p_value is not None and len(valid) else None
    return {
        "observed_tau": observed_tau,
        "p_value": p_value,
        "n_surrogates": int(len(valid)),
        "n_points": n_points,
        "significant_at_0_05": bool(p_value is not None and p_value < 0.05),
        "p_value_se": p_se,
        "borderline": bool(p_se is not None and abs(p_value - 0.05) <= 2 * p_se),
    }
