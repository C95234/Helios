"""Outils d'évaluation (phase 4) : AUC et tendance de Kendall. Séparés du moteur d'estimation."""
from __future__ import annotations

import numpy as np
from scipy.stats import kendalltau


def auc(positifs, negatifs) -> float:
    """Probabilité qu'un positif tiré au hasard ait une valeur supérieure à celle d'un négatif (égalités comptées 1/2).
    Une AUC de 0,5 est le hasard."""
    p = np.asarray(positifs, dtype=float)[:, None]
    n = np.asarray(negatifs, dtype=float)[None, :]
    return float((p > n).mean() + 0.5 * (p == n).mean())


def tendance_kendall(valeurs, nan_en_zero: bool = True) -> float:
    """τ de Kendall entre le temps (0, 1, 2, …) et la série ; NaN du test (série constante) ramené à 0 si demandé."""
    v = np.asarray(valeurs, dtype=float)
    tau = float(kendalltau(np.arange(len(v)), v)[0])
    return 0.0 if (nan_en_zero and np.isnan(tau)) else tau
