"""Contrôles de calendrier : jours fériés et vacances scolaires par zone (pré-enregistrement, §6 point 4).

Sources (data.gouv.fr, licence ouverte v2) :
- jours fériés en métropole (etalab), fichier `jours_feries_metropole.csv` ;
- calendrier scolaire de l'Éducation nationale, fichier `fr-en-calendrier-scolaire.csv`.

Pour chaque semaine ISO et chaque département : `ferie` = au moins un jour férié dans la semaine (0 ou 1) ;
`vacances` = part des 7 jours en vacances scolaires de la zone du département (de 0 à 1). Les intervalles de vacances sont
[début, reprise[ en heure de Paris (la « date de fin » du fichier est le jour de reprise).
L'Alsace-Moselle (jours fériés supplémentaires) n'est pas distinguée : le fichier de jours fériés n'a qu'une zone « Métropole ».
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

#: département → académie (métropole). Les zones A, B, C sont celles du calendrier scolaire ; vérifié contre le fichier
#: (colonne « Académies ») par `tests/vulnerabilite/test_calendrier.py`.
ACADEMIES = {
    "Besançon": ["25", "39", "70", "90"], "Bordeaux": ["24", "33", "40", "47", "64"], "Clermont-Ferrand": ["03", "15", "43", "63"],
    "Dijon": ["21", "58", "71", "89"], "Grenoble": ["07", "26", "38", "73", "74"], "Limoges": ["19", "23", "87"],
    "Lyon": ["01", "42", "69"], "Poitiers": ["16", "17", "79", "86"],
    "Aix-Marseille": ["04", "05", "13", "84"], "Amiens": ["02", "60", "80"], "Normandie": ["14", "27", "50", "61", "76"],
    "Lille": ["59", "62"], "Nancy-Metz": ["54", "55", "57", "88"], "Nantes": ["44", "49", "53", "72", "85"], "Nice": ["06", "83"],
    "Orléans-Tours": ["18", "28", "36", "37", "41", "45"], "Reims": ["08", "10", "51", "52"], "Rennes": ["22", "29", "35", "56"],
    "Strasbourg": ["67", "68"],
    "Créteil": ["77", "93", "94"], "Paris": ["75"], "Versailles": ["78", "91", "92", "95"],
    "Montpellier": ["11", "30", "34", "48", "66"], "Toulouse": ["09", "12", "31", "32", "46", "65", "81", "82"],
    "Corse": ["2A", "2B"],
}
ZONE_DE_L_ACADEMIE = {
    **{a: "Zone A" for a in ("Besançon", "Bordeaux", "Clermont-Ferrand", "Dijon", "Grenoble", "Limoges", "Lyon", "Poitiers")},
    **{a: "Zone B" for a in ("Aix-Marseille", "Amiens", "Normandie", "Lille", "Nancy-Metz", "Nantes", "Nice", "Orléans-Tours", "Reims", "Rennes", "Strasbourg")},
    **{a: "Zone C" for a in ("Créteil", "Paris", "Versailles", "Montpellier", "Toulouse")},
    "Corse": "Corse",
}
ZONE_DU_DEPARTEMENT = {d: ZONE_DE_L_ACADEMIE[a] for a, deps in ACADEMIES.items() for d in deps}


def departements_metropole() -> list[str]:
    return [f"{i:02d}" for i in range(1, 96) if i != 20] + ["2A", "2B"]


def charger_jours_feries(chemin: Path) -> pd.DatetimeIndex:
    f = pd.read_csv(chemin, parse_dates=["date"])
    return pd.DatetimeIndex(sorted(set(f.loc[f.zone == "Métropole", "date"])))


def charger_vacances(chemin: Path) -> dict[str, list[tuple[pd.Timestamp, pd.Timestamp]]]:
    """Intervalles [début, reprise[ de vacances scolaires par zone (A, B, C, Corse), élèves, dates locales de Paris."""
    d = pd.read_csv(chemin, sep=";", encoding="utf-8-sig")
    d = d[d.Zones.isin(["Zone A", "Zone B", "Zone C", "Corse"])]
    d = d[d.Description.str.contains("Vacances") & ~d.Description.str.startswith("Début") & ~d.Description.str.contains("Pont")]
    d = d[~d.Population.str.contains("Enseignants", na=False)]
    for col in ("Date de début", "Date de fin"):
        d[col] = pd.to_datetime(d[col], utc=True).dt.tz_convert("Europe/Paris").dt.normalize().dt.tz_localize(None)
    sortie = {}
    for zone, g in d.groupby("Zones"):
        sortie[zone] = sorted({(a, b) for a, b in zip(g["Date de début"], g["Date de fin"]) if b > a})
    return sortie


def controles_hebdomadaires(semaines: pd.DatetimeIndex, departements: list[str], feries: pd.DatetimeIndex, vacances: dict) -> np.ndarray:
    """Tableau (n_semaines, n_départements, 2) : [férié dans la semaine, part de la semaine en vacances scolaires]."""
    C = np.zeros((len(semaines), len(departements), 2))
    jours_feries = set(feries.normalize())
    for i, lundi in enumerate(semaines):
        jours = pd.date_range(lundi, periods=7, freq="D")
        C[i, :, 0] = float(any(j in jours_feries for j in jours))
        for k, dep in enumerate(departements):
            zone = ZONE_DU_DEPARTEMENT.get(dep)
            if zone is None:
                C[i, k, 1] = np.nan  # département d'outre-mer : zones propres, non gérées
                continue
            C[i, k, 1] = np.mean([any(a <= j < b for a, b in vacances[zone]) for j in jours])
    return C


def controles_quotidiens(jours: pd.DatetimeIndex, departements: list[str], feries: pd.DatetimeIndex, vacances: dict) -> np.ndarray:
    """Tableau (n_jours, n_départements, 8) pour le pas quotidien : 6 indicatrices de jour de semaine (mardi à dimanche, le lundi sert de
    référence), jour férié (0 ou 1), vacances scolaires de la zone du département (0 ou 1)."""
    C = np.zeros((len(jours), len(departements), 8))
    for k in range(6):
        C[:, :, k] = (jours.dayofweek.to_numpy() == k + 1)[:, None]
    ferie = np.isin(jours.normalize(), feries.normalize().to_numpy())
    C[:, :, 6] = ferie[:, None]
    for j, dep in enumerate(departements):
        zone = ZONE_DU_DEPARTEMENT.get(dep)
        if zone is None:
            C[:, j, 7] = np.nan
            continue
        C[:, j, 7] = np.array([any(a <= d < b for a, b in vacances[zone]) for d in jours], dtype=float)
    return C
