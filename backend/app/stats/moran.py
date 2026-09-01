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


def morans_i(values: np.ndarray, weights: np.ndarray) -> float:
    """weights : matrice N x N, w_ij = 1 si i et j voisins, 0 sinon (diagonale nulle)."""
    n = len(values)
    if weights.shape != (n, n):
        raise ValueError("La matrice de poids doit etre de taille N x N")

    x = np.asarray(values, dtype=float)
    xbar = x.mean()
    deviations = x - xbar
    s0 = weights.sum()
    if s0 == 0:
        return float("nan")

    numerator = deviations @ weights @ deviations
    denominator = (deviations**2).sum()
    if denominator == 0:
        return float("nan")

    return float((n / s0) * (numerator / denominator))


def permutation_test(
    values: np.ndarray,
    weights: np.ndarray,
    n_permutations: int = 500,
    seed: int | None = None,
) -> dict:
    """Test de significativite par permutation -- methode standard pour l'indice de Moran
    (equivalent spatial des donnees de substitution du §5.4 : on detruit la structure
    spatiale en re-assignant les valeurs a des noeuds au hasard, en gardant le reseau fixe).
    """
    observed = morans_i(values, weights)
    if np.isnan(observed):
        return {"observed_i": None, "p_value": None, "n_permutations": 0, "null_mean": None, "null_std": None}

    rng = np.random.default_rng(seed)
    null_values = np.empty(n_permutations)
    for i in range(n_permutations):
        permuted = rng.permutation(values)
        null_values[i] = morans_i(permuted, weights)

    p_value = float(np.mean(null_values >= observed))
    return {
        "observed_i": observed,
        "p_value": p_value,
        "n_permutations": n_permutations,
        "null_mean": float(np.mean(null_values)),
        "null_std": float(np.std(null_values)),
    }
