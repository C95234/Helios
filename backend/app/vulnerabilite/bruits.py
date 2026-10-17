"""Modèles de bruit interchangeables (note, section 7.1).

Chaque modèle fournit :
- `simuler(moyenne, rng)` : un pas de la dynamique, de moyenne conditionnelle `moyenne` ;
- `variance(moyenne, niveau=None)` : variance conditionnelle d'un pas ;
- `cout_pas(suivant, moyenne, niveau=None)` : coût d'un pas, opposé du log de la vraisemblance du pas
  rapportée à celle du pas le plus probable (pour V*) ;
- `dispersion` : rapport variance / moyenne pour les comptages (1 pour Poisson, φ pour la binomiale
  négative), `None` pour un signal continu.

Aucun de ces objets ne connaît le domaine d'application.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np

_PLANCHER_MOYENNE = 1e-9
_PLAFOND_MOYENNE = 1e6


def _moyenne_valide(moyenne) -> np.ndarray:
    return np.clip(np.asarray(moyenne, dtype=float), _PLANCHER_MOYENNE, _PLAFOND_MOYENNE)


@dataclass(frozen=True)
class Poisson:
    """Comptages de Poisson : variance égale à la moyenne."""

    nom: str = "poisson"
    dispersion: float = 1.0

    def simuler(self, moyenne, rng: np.random.Generator) -> np.ndarray:
        return rng.poisson(_moyenne_valide(moyenne)).astype(float)

    def variance(self, moyenne, niveau=None) -> np.ndarray:
        return _moyenne_valide(moyenne)

    def cout_pas(self, suivant, moyenne, niveau=None) -> np.ndarray:
        """x' ln(x'/F) - x' + F, avec la convention 0 ln 0 = 0."""
        x = np.asarray(suivant, dtype=float)
        f = _moyenne_valide(moyenne)
        terme = np.where(x > 0, x * np.log(np.where(x > 0, x, 1.0) / f), 0.0)
        return terme - x + f


@dataclass(frozen=True)
class BinomialeNegative:
    """Comptages surdispersés : variance conditionnelle φ·F (φ ≥ 1 ; φ = 1 redonne Poisson).

    Paramétrage de la note (script `t9`) : r = F/(φ−1), p = 1/φ. Le coût d'un pas est
    x' ln(x'/F) − (x'+r) ln((x'+r)/(F+r)) avec ce r ; il tend vers le coût de Poisson quand φ → 1.
    """

    phi: float = 2.0
    nom: str = "binomiale_negative"

    def __post_init__(self):
        if not self.phi >= 1.0:
            raise ValueError("La dispersion φ d'une binomiale négative doit être ≥ 1.")

    @property
    def dispersion(self) -> float:
        return float(self.phi)

    def simuler(self, moyenne, rng: np.random.Generator) -> np.ndarray:
        lam = _moyenne_valide(moyenne)
        if self.phi == 1.0:
            return rng.poisson(lam).astype(float)
        return rng.negative_binomial(lam / (self.phi - 1.0), 1.0 / self.phi).astype(float)

    def variance(self, moyenne, niveau=None) -> np.ndarray:
        return self.phi * _moyenne_valide(moyenne)

    def cout_pas(self, suivant, moyenne, niveau=None) -> np.ndarray:
        if self.phi == 1.0:
            return Poisson().cout_pas(suivant, moyenne)
        x = np.asarray(suivant, dtype=float)
        f = _moyenne_valide(moyenne)
        r = f / (self.phi - 1.0)
        terme = np.where(x > 0, x * np.log(np.where(x > 0, x, 1.0) / f), 0.0)
        return terme - (x + r) * np.log((x + r) / (f + r))


@dataclass(frozen=True)
class Gaussien:
    """Signal continu à bruit gaussien. `sigma2` : variance constante, ou fonction du niveau (v(x))."""

    sigma2: float | Callable[[np.ndarray], np.ndarray] = 1.0
    nom: str = "gaussien"
    dispersion: None = None

    def variance(self, moyenne, niveau=None) -> np.ndarray:
        reference = np.asarray(moyenne if niveau is None else niveau, dtype=float)
        if callable(self.sigma2):
            return np.asarray(self.sigma2(reference), dtype=float)
        return np.full_like(reference, float(self.sigma2), dtype=float)

    def simuler(self, moyenne, rng: np.random.Generator, niveau=None) -> np.ndarray:
        moyenne = np.asarray(moyenne, dtype=float)
        return moyenne + np.sqrt(self.variance(moyenne, niveau)) * rng.standard_normal(moyenne.shape)

    def cout_pas(self, suivant, moyenne, niveau=None) -> np.ndarray:
        """(x' − F)² / (2 v(x))."""
        ecart = np.asarray(suivant, dtype=float) - np.asarray(moyenne, dtype=float)
        return ecart**2 / (2.0 * self.variance(moyenne, niveau))


def modele_bruit(nom: str, **parametres):
    """Fabrique à partir du nom utilisé par l'interface (`poisson`, `binomiale_negative`, `gaussien`)."""
    fabriques = {"poisson": Poisson, "binomiale_negative": BinomialeNegative, "gaussien": Gaussien}
    if nom not in fabriques:
        raise ValueError(f"Modèle de bruit inconnu : {nom!r} (attendu : {', '.join(fabriques)}).")
    return fabriques[nom](**parametres)
