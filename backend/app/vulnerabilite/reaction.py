"""EXPÉRIMENTAL — décomposition de la réaction de la société (note, section 4, proposition 9).

Modèle minimal (cas linéaire) : y_{t+1} ~ Poisson(μ + (a − κ·z_t)·y_t), z_{t+1} = (1 − ρ)·z_t + ρ·y_t, où z est une
vigilance qui suit l'activité avec une mémoire de 1/ρ pas et κ son efficacité. Linéarisé autour de l'équilibre, y suit
un ARMA(2,1) dont les trois coefficients identifient ρ, A (inflammabilité à vigilance fixée) et B·ρ (force de réaction),
donc l'inflammabilité SANS réaction a = A + B.

Statut des résultats de la note : [démontré] pour la décomposition, [vérifié numériquement ; fragile] pour l'estimation :
elle retrouve a quand la réaction est tenue (a = 1,03 pour une vraie valeur de 1,05) mais devient très instable quand la
réaction est faible ou lente (queue large, a non identifiable sans réaction). Ne pas présenter ces valeurs comme des
résultats ; étiqueter « exploratoire ».
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

STATUT = "EXPERIMENTAL"


@dataclass(frozen=True)
class DecompositionReaction:
    ac1_naive: float  # autocorrélation d'ordre 1, qui mélange inflammabilité et réaction
    A: float  # inflammabilité à vigilance fixée
    rho: float  # inverse de la mémoire de la vigilance
    B_rho: float  # B·ρ : force de réaction (B = κ·y*), multipliée par la vitesse
    a: float  # inflammabilité sans réaction : A + B = A + Bρ/ρ
    fragile: bool  # réaction faible ou lente ou ρ hors ]0, 1[ : a non fiable
    statut: str = STATUT


def _autocovariance(X: np.ndarray, k: int) -> float:
    D = X - X.mean(axis=0)
    return float(np.mean(D[k:] * D[:len(D) - k])) if k > 0 else float(np.mean(D * D))


def decomposer_reaction(X: np.ndarray, seuil_fragilite_rho: float = 0.05) -> DecompositionReaction:
    """Décomposition ARMA(2,1) par moments : Yule–Walker décalé (rangs 2 et 3), puis racine MA de module < 1.

    `X` de forme (n_pas, n_unites), sans NaN. `fragile` est vrai si ρ̂ ∉ ]seuil, 1[ ou si B̂ρ ≤ 0 (pas de réaction
    détectable : alors a n'est pas identifiable, la note rapporte des valeurs de −1,6 à 4,1 pour une vraie valeur de 0,7).
    """
    X = np.asarray(X, dtype=float)
    if np.isnan(X).any():
        raise ValueError("La décomposition de la réaction exige des séries complètes (sans NaN).")
    g = [_autocovariance(X, k) for k in range(5)]
    phi1, phi2 = np.linalg.solve([[g[1], g[0]], [g[2], g[1]]], [g[2], g[3]])
    D = X - X.mean(axis=0)
    w = D[2:] - phi1 * D[1:-1] - phi2 * D[:-2]
    r1 = float(np.mean(w[1:] * w[:-1]) / np.mean(w * w))
    # r1 = −q/(1+q²) avec q = 1 − ρ : racine de module < 1
    q = (-1.0 + np.sqrt(max(1.0 - 4.0 * r1 * r1, 0.0))) / (2.0 * r1) if r1 != 0 else 0.0
    rho = 1.0 - q
    A = float(phi1) - 1.0 + rho
    B_rho = float(-phi2 - A * (1.0 - rho))
    fragile = not (seuil_fragilite_rho < rho < 1.0) or B_rho <= 0
    a = A + B_rho / rho if rho != 0 else float("nan")
    return DecompositionReaction(_autocovariance(X, 1) / g[0], float(A), float(rho), B_rho, float(a), bool(fragile))
