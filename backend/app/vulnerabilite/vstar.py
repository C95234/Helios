"""V* : coût minimal d'embrasement en dimension 1 (note, section 6 et section 7).

V* = inf { Σ_k L(x_k, x_{k+1}) : x_0 = calme, x_K ∈ bassin d'embrasement }, où L est le coût d'un pas du modèle de
bruit (`bruits`, méthode `cout_pas`). On le calcule par programmation dynamique (Bellman) sur une grille de niveaux.
La loi unifiée ln E[T] = V* + O(1) (prop. 11) est une conjecture standard des grandes déviations, vérifiée
numériquement dans la note (pente 1,03 sur 147 jeux de paramètres, temps exacts) : [vérifié numériquement].

Hors périmètre de ce module (phase 1b du cahier) : modèle joint contagion + réaction sur la grille (y, z), et réseau
(points-selles, chemins de moindre action).
"""
from __future__ import annotations

from typing import Callable

import numpy as np
from scipy.stats import poisson

from .bruits import Poisson
from .modele import points_fixes


def vstar_1d(
    reponse: Callable[[np.ndarray], np.ndarray],
    bruit,
    m_bas: float,
    m_haut: float,
    bas: float,
    haut: float,
    n_noeuds: int = 1500,
    n_iterations_max: int = 500,
    tolerance: float = 1e-10,
) -> float:
    """V* pour une dynamique x ↦ `reponse(x)` perturbée par `bruit`, de l'état calme `m_bas` au seuil `m_haut`.

    La grille couvre [bas, haut] avec `n_noeuds` niveaux ; le bassin d'embrasement est {x ≥ m_haut}. Le résultat
    dépend de la finesse de la grille : à vérifier par convergence (les tests le font).
    """
    if not (bas < m_bas < m_haut < haut):
        raise ValueError("Il faut bas < m_bas < m_haut < haut.")
    xs = np.linspace(bas, haut, n_noeuds)
    F = reponse(xs)
    L = bruit.cout_pas(xs[None, :], F[:, None], niveau=xs[:, None])
    V = np.full(n_noeuds, np.inf)
    V[np.argmin(np.abs(xs - m_bas))] = 0.0
    for _ in range(n_iterations_max):
        V_suivant = np.minimum(V, np.min(V[:, None] + L, axis=0))
        if np.allclose(V_suivant, V, atol=tolerance, equal_nan=True):
            V = V_suivant
            break
        V = V_suivant
    cible = V[xs >= m_haut]
    if cible.size == 0:
        raise ValueError("Aucun niveau de la grille n'atteint le seuil m_haut.")
    return float(cible.min())


def vstar_poisson(a: float, mu: float, c: float, n_noeuds: int = 1500) -> float:
    """V* de la contagion complexe F(y) = μ + a·y + c·y² à bruit de Poisson (grille de la note : de 10⁻³ à 1,6·m₊ + 5)."""
    pts = points_fixes(a, mu, c)
    if pts is None:
        raise ValueError("Pas d'état calme : Δ < 0.")
    m_bas, m_haut = pts
    return vstar_1d(lambda x: mu + a * x + c * x * x, Poisson(), m_bas, m_haut, 1e-3, 1.6 * m_haut + 5.0, n_noeuds)


def vstar_gaussien(
    reponse: Callable[[np.ndarray], np.ndarray],
    sigma: float,
    m_bas: float,
    m_haut: float,
    bas: float | None = None,
    haut: float | None = None,
    n_noeuds: int = 1200,
) -> float:
    """V* pour un signal continu à bruit gaussien d'écart-type `sigma` (coût (x' − F(x))²/(2σ²)).

    Grille par défaut (script `g3`) : de m₋ − 3·s* à m₊ + 1,5·s*. Invariant par changement affine d'unités
    (c → c/g, σ → g·σ), ce qui permet de l'estimer sans connaître gains ni décalages des capteurs.
    """
    from .bruits import Gaussien

    s = m_haut - m_bas
    bas = m_bas - 3.0 * s if bas is None else bas
    haut = m_haut + 1.5 * s if haut is None else haut
    return vstar_1d(reponse, Gaussien(sigma2=sigma * sigma), m_bas, m_haut, bas, haut, n_noeuds, n_iterations_max=500, tolerance=1e-10)


def temps_moyen_exact_poisson(a: float, mu: float, c: float, m_bas: float, m_haut: float) -> float:
    """E[T] EXACT depuis l'état calme, en résolvant le système linéaire de la chaîne de Markov (états 0 à ⌈2·m₊ + 5⌉ − 1) :
    sert de vérité pour la loi ln E[T] ≈ V* (aucune simulation, valable jusqu'à ln E[T] ≈ 30)."""
    seuil = int(np.ceil(2 * m_haut + 5))
    ys = np.arange(seuil)
    lam = mu + a * ys + c * ys * ys
    Q = poisson.pmf(ys[None, :], lam[:, None])
    t = np.linalg.solve(np.eye(seuil) - Q, np.ones(seuil))
    return float(t[int(round(m_bas))])
