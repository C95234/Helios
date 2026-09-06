"""Connecteur INSEE -- series agregees par departement -- cahier des charges Helios §6, §5.2.

Meme service ouvert que le connecteur BDM (connectors/insee.py), mais sur
des dataflows agreges qui renvoient en une seule requete une serie par
departement -- exactement ce qu'il faut pour calculer une coupe spatiale
(indice de Moran, §5.2) sur les departements de metropole.

Generalise (H2, "pousser au maximum de series reelles") : chaque dataflow
Insee de ce type contient en realite PLUSIEURS variantes par departement
(secteurs d'activite, sexe/age, correction CVS/brut...) -- contrairement
au chomage localise (TAUX-CHOMAGE, une seule variante), il faut filtrer
explicitement par un jeu d'attributs verifie en direct pour isoler UNE
serie par departement. `required_attrs` porte ce filtre ; vide pour le
chomage (jamais eu besoin de filtrer).
"""
from __future__ import annotations

import xml.etree.ElementTree as ET

import httpx
import pandas as pd

from .base import Connector
from .insee import TERMS_OF_USE_URL, _parse_time_period

BASE_URL = "https://bdm.insee.fr/series/sdmx/data"


class InseeDepartmentSeriesConnector(Connector):
    """Connecteur generique pour un dataflow BDM Insee agrege par
    departement (REF_AREA = 'D' + 2 chiffres, ~94 codes metropolitains)."""

    terms_of_use_url = TERMS_OF_USE_URL

    def __init__(self, name: str, dataflow_id: str, required_attrs: dict[str, str] | None = None):
        self.name = name
        self.dataflow_id = dataflow_id
        self.required_attrs = required_attrs or {}

    async def fetch(self, start_period: str | None = None, last_n_observations: int | None = None) -> str:
        params = {}
        if start_period:
            params["startPeriod"] = start_period
        if last_n_observations:
            params["lastNObservations"] = last_n_observations
        url = f"{BASE_URL}/{self.dataflow_id}"
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.text

    def normalize(self, raw: str) -> pd.DataFrame:
        root = ET.fromstring(raw)
        rows = []
        for series_el in root.iter("Series"):
            ref_area = series_el.get("REF_AREA", "")
            if not (len(ref_area) == 3 and ref_area.startswith("D") and ref_area[1:].isdigit()):
                continue  # ne garde que les departements metropolitains (Dxx), pas les regions/DOM
            if any(series_el.get(k) != v for k, v in self.required_attrs.items()):
                continue  # isole la seule variante voulue parmi celles du dataflow
            code = ref_area[1:]  # "D33" -> "33"
            title = series_el.get("TITLE_FR", ref_area)
            for obs in series_el.findall("Obs"):
                period = obs.get("TIME_PERIOD")
                raw_value = obs.get("OBS_VALUE")
                if period is None or raw_value is None:
                    continue
                rows.append(
                    {
                        "source": self.name,
                        "territoire": code,
                        "date": _parse_time_period(period),
                        "indicateur": self.dataflow_id,
                        "valeur": float(raw_value),
                        "metadonnees": {"title": title, "raw_period": period},
                    }
                )
        df = pd.DataFrame(rows)
        if df.empty:
            return df
        df["date"] = pd.to_datetime(df["date"])
        return df.sort_values(["territoire", "date"]).reset_index(drop=True)


# Chomage localise -- dataflow a une seule variante par departement, aucun filtre necessaire.
UNEMPLOYMENT_CONNECTOR = InseeDepartmentSeriesConnector(
    name="insee_taux_chomage_departements", dataflow_id="TAUX-CHOMAGE"
)

# Quatre variables supplementaires, verifiees en direct (catalogue SDMX Insee,
# 244 dataflows -- attributs de filtre confirmes par requete reelle avant
# d'etre codes en dur ici) pour "pousser" H2 au-dela du seul chomage.
DEFAILLANCES_CONNECTOR = InseeDepartmentSeriesConnector(
    name="insee_defaillances_entreprises",
    dataflow_id="DEFAILLANCES-ENTREPRISES",
    required_attrs={"CORRECTION": "BRUT", "INDICATEUR": "NOMBRE_DEFAILLANCES", "ACTIVITE_CREAT_ENT": "ENS"},
)

CONSTRUCTION_CONNECTOR = InseeDepartmentSeriesConnector(
    name="insee_logements_autorises",
    dataflow_id="CONSTRUCTION-LOGEMENTS",
    required_attrs={
        "CORRECTION": "BRUT",
        "INDICATEUR": "NBRE_LOG_AUT",
        "LOGEMENT": "SO",
        "ETAT_CONSTRUCTION": "CLA",
        "CUMUL12MOIS": "CUMUL",
    },
)

CREATIONS_CONNECTOR = InseeDepartmentSeriesConnector(
    name="insee_creations_entreprises",
    dataflow_id="CREATIONS-ENTREPRISES-METHODE-2022",
    required_attrs={"CORRECTION": "BRUT", "INDICATEUR": "TYPE-ENT_TOTAL", "ACTIVITE_CREAT_ENT": "ENS"},
)

POPULATION_CONNECTOR = InseeDepartmentSeriesConnector(
    name="insee_estimations_population",
    dataflow_id="TCRED-ESTIMATIONS-POPULATION",
    required_attrs={
        "NATURE": "VALEUR_ABSOLUE",
        "INDICATEUR": "ESTIMATIONS_POPULATION_AGE_SEXE",
        "UNIT_MEASURE": "INDIVIDUS",
        "SEXE": "0",
        "AGE": "00-",
        "CORRECTION": "BRUT",
    },
)
