"""Interface commune des connecteurs -- cahier des charges Helios §6.

Chaque connecteur est un module independant exposant fetch() et normalize().
Ajouter une source ne doit jamais modifier le coeur du systeme : les routers
et le moteur de calcul ne dependent que du schema normalise ci-dessous.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class NormalizedObservation:
    """Schema commun a tous les connecteurs : (source, territoire, date, indicateur, valeur, metadonnees)."""

    source: str
    territoire: str
    date: str
    indicateur: str
    valeur: float
    metadonnees: dict


class Connector(ABC):
    """Un connecteur ne fournit jamais de donnees individuelles nominatives (§9.1)."""

    name: str
    terms_of_use_url: str

    @abstractmethod
    async def fetch(self, **kwargs) -> object:
        """Recupere les donnees brutes depuis la source externe."""

    @abstractmethod
    def normalize(self, raw: object) -> pd.DataFrame:
        """Convertit les donnees brutes vers le schema commun (colonnes ci-dessus)."""
