"""Modèles d'observation interchangeables (note, section 3 et section 7.3).

- `CanauxAmincis` (comptages) : chaque canal ne voit qu'une fraction binomiale des événements,
  o^k_t | y_t ~ Bin(y_t, θ^k_t) ; les amincissements de canaux différents sont indépendants conditionnellement
  à y_t (hypothèse 2). Un canal peut avoir une « boucle de surveillance » : son taux de détection dépend de ses
  propres observations passées (on patrouille là où l'on a enregistré) ; formes reprises des scripts `t7`/`t7b`.
- `CapteursAffines` (signal continu) : o^k_t = g_k·x_t + b_k + g_k·η·ξ^k_t, gains, décalages et bruits de
  mesure inconnus (proposition 14).

L'observation ne modifie jamais la dynamique de y (hypothèse 2) ; une observation qui la modifie est de la
réaction et se modélise comme telle.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np


@dataclass(frozen=True)
class CanauxAmincis:
    """Canaux d'observation à amincissement binomial.

    `taux` : taux de détection de base θ^k de chaque canal.
    `canal_sous_boucle` : indice du canal sous boucle de surveillance (None = aucun) ; `intensite_boucle` : η.
    `forme_boucle` :
      - "lineaire" (script t7) : θ_t = min(plafond, θ·(1 + η·o_{t−1})) ;
      - "centree" (script t7b) : θ_t = min(plafond, θ·max(1 + η·(o_{t−1}/(θ·niveau_reference) − 1), 0,05)).
    """

    taux: tuple[float, ...]
    canal_sous_boucle: int | None = None
    intensite_boucle: float = 0.0
    forme_boucle: str = "lineaire"
    niveau_reference: float = 1.0
    plafond: float = 0.95

    def __post_init__(self):
        if not all(0.0 < t <= 1.0 for t in self.taux):
            raise ValueError("Les taux de détection doivent être dans ]0, 1].")
        if self.forme_boucle not in ("lineaire", "centree"):
            raise ValueError("forme_boucle doit valoir « lineaire » ou « centree ».")

    @property
    def n_canaux(self) -> int:
        return len(self.taux)

    def observation_initiale(self, n_unites: int) -> np.ndarray:
        """Observation « précédente » du canal sous boucle au premier pas."""
        if self.forme_boucle == "centree":
            return np.full(n_unites, self.taux[self.canal_sous_boucle or 0] * self.niveau_reference)
        return np.zeros(n_unites)

    def taux_effectif(self, canal: int, observation_precedente: np.ndarray | None):
        base = self.taux[canal]
        if canal != self.canal_sous_boucle or observation_precedente is None:
            return base
        if self.forme_boucle == "lineaire":
            return np.minimum(self.plafond, base * (1 + self.intensite_boucle * observation_precedente))
        facteur = np.clip(1 + self.intensite_boucle * (observation_precedente / (base * self.niveau_reference) - 1), 0.05, None)
        return np.minimum(self.plafond, base * facteur)

    def observer(self, y: np.ndarray, rng: np.random.Generator, observation_precedente: np.ndarray | None = None) -> list[np.ndarray]:
        """Une observation par canal, dans l'ordre des canaux (c'est l'ordre de consommation du flux aléatoire)."""
        n = y.astype(int)
        return [rng.binomial(n, self.taux_effectif(k, observation_precedente)).astype(float) for k in range(self.n_canaux)]


@dataclass(frozen=True)
class CapteursAffines:
    """Capteurs continus affines : o^k = g_k·x + b_k + g_k·η·ξ (ξ ~ N(0,1))."""

    gains: tuple[float, ...]
    decalages: tuple[float, ...]
    bruit_mesure: float = 0.0

    def __post_init__(self):
        if len(self.gains) != len(self.decalages):
            raise ValueError("Autant de gains que de décalages.")
        if any(g == 0 for g in self.gains):
            raise ValueError("Un gain nul rend le capteur inutilisable.")

    @property
    def n_canaux(self) -> int:
        return len(self.gains)

    def observer(self, x: np.ndarray, rng: np.random.Generator) -> list[np.ndarray]:
        return [g * x + b + g * self.bruit_mesure * rng.standard_normal(x.shape) for g, b in zip(self.gains, self.decalages)]


def taux_depuis_sequence(taux: Sequence[float]) -> tuple[float, ...]:
    return tuple(float(t) for t in taux)
