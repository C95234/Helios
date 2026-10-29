"""Intervalles d'incertitude par bootstrap (note, section 5, « Incertitude »).

- `bootstrap_unites` : rééchantillonne les UNITÉS (colonnes). Couverture mesurée dans la note pour un intervalle
  à 90 % de Φ̂ : 90 % avec 100 unités × 200 pas, 92 % avec 100 × 60, mais 80 % avec 16 × 200 : avec peu d'unités
  le bootstrap simple est trop optimiste (drapeau sous 30 unités).
- `bootstrap_blocs_temps` : rééchantillonne des BLOCS DE PAS consécutifs, pour des unités corrélées dans le temps
  (chocs communs, vagues synchrones). La note signale cette variante comme NON TESTÉE : à valider par simulation
  avant tout usage sur données réelles. Une ligne vide sépare les blocs pour ne jamais fabriquer de transition
  y_t → y_{t+1} entre deux blocs non contigus.
"""
from __future__ import annotations

import warnings
from dataclasses import dataclass
from typing import Callable

import numpy as np

SEUIL_PEU_D_UNITES = 30


@dataclass(frozen=True)
class IntervalleBootstrap:
    bas: float
    haut: float
    niveau: float
    n_tirages: int
    n_tirages_invalides: int  # tirages dont la statistique n'a pas pu être calculée (écartés)
    avertissement: str | None = None

    @property
    def largeur(self) -> float:
        return self.haut - self.bas


def _intervalle(valeurs: list[float], niveau: float, invalides: int, avertissement: str | None) -> IntervalleBootstrap:
    if not valeurs:
        raise ValueError("Aucun tirage bootstrap exploitable.")
    alpha = (1.0 - niveau) / 2.0 * 100.0
    bas, haut = np.percentile(valeurs, [alpha, 100.0 - alpha])
    return IntervalleBootstrap(float(bas), float(haut), niveau, len(valeurs), invalides, avertissement)


def bootstrap_unites(
    X: np.ndarray,
    statistique: Callable[[np.ndarray], float],
    n_tirages: int = 200,
    rng: np.random.Generator | None = None,
    niveau: float = 0.90,
    plafond: float = 99.0,
) -> IntervalleBootstrap:
    """Intervalle de `statistique(X)` par bootstrap des colonnes de X (forme (n_pas, n_unites)).

    `plafond` : valeur maximale retenue pour la statistique (Φ̂ infini → plafonné, comme dans la note).
    """
    rng = rng or np.random.default_rng()
    X = np.asarray(X, dtype=float)
    n = X.shape[1]
    avertissement = None
    if n < SEUIL_PEU_D_UNITES:
        avertissement = (f"Seulement {n} unités (< {SEUIL_PEU_D_UNITES}) : le bootstrap par unités sous-couvre "
                         "(80 % au lieu de 90 % avec 16 unités dans la note). Intervalle trop optimiste.")
        warnings.warn(avertissement, stacklevel=2)
    valeurs, invalides = [], 0
    for _ in range(n_tirages):
        try:
            valeurs.append(min(float(statistique(X[:, rng.integers(0, n, n)])), plafond))
        except ValueError:
            invalides += 1
    return _intervalle(valeurs, niveau, invalides, avertissement)


def bootstrap_blocs_temps(
    X: np.ndarray,
    statistique: Callable[[np.ndarray], float],
    taille_bloc: int,
    n_tirages: int = 200,
    rng: np.random.Generator | None = None,
    niveau: float = 0.90,
    plafond: float = 99.0,
) -> IntervalleBootstrap:
    """Bootstrap par blocs de `taille_bloc` pas consécutifs (EXPÉRIMENTAL : non testé dans la note)."""
    rng = rng or np.random.default_rng()
    X = np.asarray(X, dtype=float)
    n_pas = X.shape[0]
    if not 2 <= taille_bloc <= n_pas:
        raise ValueError("taille_bloc doit être comprise entre 2 et le nombre de pas.")
    n_blocs = int(np.ceil(n_pas / taille_bloc))
    ligne_vide = np.full((1, X.shape[1]), np.nan)
    valeurs, invalides = [], 0
    for _ in range(n_tirages):
        debuts = rng.integers(0, n_pas - taille_bloc + 1, n_blocs)
        morceaux = []
        for d in debuts:
            morceaux += [X[d:d + taille_bloc], ligne_vide]
        try:
            valeurs.append(min(float(statistique(np.vstack(morceaux))), plafond))
        except ValueError:
            invalides += 1
    return _intervalle(valeurs, niveau, invalides, "Bootstrap par blocs de temps non testé dans la note : à valider par simulation.")
