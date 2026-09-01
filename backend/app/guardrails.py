"""Garde-fous structurels d'ingestion -- cahier des charges Helios §9.1 et §9.2.

Le schema d'ingestion n'accepte que des colonnes numeriques + date + territoire.
Toute colonne qui ressemble a un identifiant personnel est rejetee AVANT tout
calcul, avec un message explicite -- jamais silencieusement ignoree (§11).

Ce module est reutilise par tout futur connecteur d'import (CSV, API tierce) ;
aucune source de donnees ne doit contourner cette verification.
"""
from __future__ import annotations

import re

import pandas as pd

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_NOMINAL_COLUMN_NAME_RE = re.compile(
    r"(^|_)(nom|prenom|first_?name|last_?name|full_?name|email|e-?mail|"
    r"ssn|nir|numero_?secu|id_?utilisateur|user_?id|adresse|telephone|phone)($|_)",
    re.IGNORECASE,
)

MIN_K_ANONYMITY = 20
MIN_COMMUNE_POPULATION = 2000


class NominalDataRejected(ValueError):
    """Leve quand une colonne d'entree ressemble a un identifiant personnel."""


def _column_looks_nominal(name: str, series: pd.Series) -> str | None:
    if _NOMINAL_COLUMN_NAME_RE.search(name):
        return f"le nom de colonne « {name} » evoque un identifiant personnel"

    if series.dtype == object:
        sample = series.dropna().astype(str).head(200)
        if len(sample) == 0:
            return None
        email_ratio = sample.apply(lambda v: bool(_EMAIL_RE.match(v.strip()))).mean()
        if email_ratio > 0.5:
            return f"la colonne « {name} » contient majoritairement des adresses email"

        unique_ratio = series.nunique(dropna=True) / max(len(series.dropna()), 1)
        looks_like_free_name = sample.apply(
            lambda v: bool(re.match(r"^[A-ZÀ-Ý][a-zà-ÿ'-]+(\s[A-ZÀ-Ý][a-zà-ÿ'-]+){1,3}$", v.strip()))
        ).mean()
        if unique_ratio > 0.9 and looks_like_free_name > 0.5:
            return f"la colonne « {name} » ressemble a des noms propres uniques par ligne"

    return None


def validate_no_nominal_columns(df: pd.DataFrame) -> None:
    """Leve NominalDataRejected au premier signe de colonne nominative.

    Ne modifie jamais silencieusement les donnees : soit l'import passe,
    soit il est rejete avec la raison exacte (cahier des charges §11).
    """
    reasons = []
    for column in df.columns:
        reason = _column_looks_nominal(column, df[column])
        if reason:
            reasons.append(reason)
    if reasons:
        raise NominalDataRejected(
            "Import refuse : ce fichier semble contenir des donnees nominatives "
            "individuelles, ce qu'Helios n'accepte pas (donnees agregees uniquement). "
            + " ; ".join(reasons)
        )


def enforce_k_anonymity(group_sizes: pd.Series, k: int = MIN_K_ANONYMITY) -> pd.Series:
    """Masque (NaN) les sous-groupes dont l'effectif est sous le seuil de k-anonymat (§9.2)."""
    return group_sizes.where(group_sizes >= k)


def population_below_display_threshold(population: int, threshold: int = MIN_COMMUNE_POPULATION) -> bool:
    """True si la population communale est sous le seuil d'affichage territorial (§9.2)."""
    return population < threshold
