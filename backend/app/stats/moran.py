"""Indice de Moran -- cahier des charges Helios §5.2.

I_t = (N / S0) * [ sum_ij w_ij (x_i - xbar)(x_j - xbar) ] / [ sum_i (x_i - xbar)^2 ]

Pas d'implementation de reference dans scipy/statsmodels (contrairement a la
variance et l'AC1, §11) : la formule est verifiee ici contre un exemple
calcule a la main (voir tests/test_moran.py) et par des proprietes connues
(permutation aleatoire -> esperance proche de -1/(N-1), damier parfait ->
autocorrelation negative forte).
"""
from __future__ import annotations

import numpy as np

# Un champ dont toutes les valeurs sont egales a quelques unites de derniere decimale
# pres ne se distingue pas du bruit d'arrondi : l'indice y est indefini. Tolerance
# RELATIVE a l'amplitude du champ, pas a sa variance (la variance d'un champ constant
# n'est pas exactement 0 une fois la moyenne arrondie : np.full(9, 0.23) donnait I = 1.0).
_CONSTANT_FIELD_RTOL = 8 * np.finfo(float).eps

# Permutations dont I egale l'observe a l'arrondi pres = vrais ex-aequo (frequents pour
# des champs binaires ou entiers) : comptees comme "au moins aussi grand".
_TIE_RTOL = 1e-12


def validate_weights(weights: np.ndarray, n: int) -> np.ndarray:
    """Matrice N x N de valeurs finies a diagonale nulle -- sinon l'indice est faux sans
    avertissement (des auto-poids W + I faisaient passer I de -0.11 a +0.19)."""
    w = np.asarray(weights, dtype=float)
    if w.shape != (n, n):
        raise ValueError("La matrice de poids doit etre de taille N x N")
    if not np.all(np.isfinite(w)):
        raise ValueError("La matrice de poids ne doit contenir que des valeurs finies (ni NaN ni inf)")
    if np.any(np.diag(w) != 0):
        raise ValueError("La matrice de poids doit avoir une diagonale nulle (les auto-poids gonflent l'indice)")
    return w


def _morans_i(x: np.ndarray, w: np.ndarray) -> float:
    n = len(x)
    s0 = w.sum()
    if s0 == 0:
        return float("nan")
    if np.ptp(x) <= _CONSTANT_FIELD_RTOL * np.max(np.abs(x)):
        return float("nan")
    deviations = x - x.mean()
    numerator = deviations @ w @ deviations
    denominator = (deviations**2).sum()
    return float((n / s0) * (numerator / denominator))


def morans_i(values: np.ndarray, weights: np.ndarray) -> float:
    """weights : matrice N x N, w_ij = 1 si i et j voisins, 0 sinon (diagonale nulle,
    valeurs finies -- verifie). Renvoie nan si le champ est constant (a la resolution
    flottante pres) ou si les poids sont tous nuls."""
    x = np.asarray(values, dtype=float)
    return _morans_i(x, validate_weights(weights, len(x)))


def permutation_test(
    values: np.ndarray,
    weights: np.ndarray,
    n_permutations: int = 500,
    seed: "int | np.random.Generator | None" = None,
) -> dict:
    """Test de significativite par permutation -- methode standard pour l'indice de Moran
    (equivalent spatial des donnees de substitution du §5.4 : on detruit la structure
    spatiale en re-assignant les valeurs a des noeuds au hasard, en gardant le reseau fixe).

    `seed` peut etre un Generator numpy, utilise tel quel : des appels successifs tirent
    alors des permutations differentes (au lieu de rejouer la meme graine a chaque fois).
    """
    values = np.asarray(values, dtype=float)
    weights = validate_weights(weights, len(values))
    observed = _morans_i(values, weights)
    if np.isnan(observed):
        return {"observed_i": None, "p_value": None, "n_permutations": 0, "null_mean": None, "null_std": None}

    rng = np.random.default_rng(seed)
    null_values = np.empty(n_permutations)
    for i in range(n_permutations):
        null_values[i] = _morans_i(rng.permutation(values), weights)

    # Plancher standard (Davison & Hinkley 1997 ; North, Curtis & Sham 2002) : sans le +1
    # au numerateur et au denominateur, la p-value peut tomber exactement a 0 -- meme bug
    # que celui trouve par Bruce Stephenson dans la contribution ewstools (§1ter.1).
    n_at_least_as_large = np.sum(null_values >= observed - _TIE_RTOL * max(1.0, abs(observed)))
    p_value = float((1 + n_at_least_as_large) / (1 + n_permutations))
    return {
        "observed_i": observed,
        "p_value": p_value,
        "n_permutations": n_permutations,
        "null_mean": float(np.mean(null_values)),
        "null_std": float(np.std(null_values)),
    }
