"""Connecteur INSEE -- taux de chomage localise par departement -- cahier des charges Helios §6, §5.2.

Meme service ouvert que le connecteur BDM (connectors/insee.py), mais sur le
dataflow agrege TAUX-CHOMAGE qui renvoie en une seule requete les 115 series
regionales et departementales -- exactement ce qu'il faut pour calculer une
coupe spatiale (indice de Moran, §5.2) sur les departements de metropole.
"""
from __future__ import annotations

import xml.etree.ElementTree as ET

import httpx
import pandas as pd

from .base import Connector
from .insee import TERMS_OF_USE_URL, _parse_time_period

DATAFLOW_URL = "https://bdm.insee.fr/series/sdmx/data/TAUX-CHOMAGE"


class InseeDepartmentUnemploymentConnector(Connector):
    name = "insee_taux_chomage_departements"
    terms_of_use_url = TERMS_OF_USE_URL

    async def fetch(self, start_period: str | None = None, last_n_observations: int | None = None) -> str:
        params = {}
        if start_period:
            params["startPeriod"] = start_period
        if last_n_observations:
            params["lastNObservations"] = last_n_observations
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(DATAFLOW_URL, params=params)
            response.raise_for_status()
            return response.text

    def normalize(self, raw: str) -> pd.DataFrame:
        root = ET.fromstring(raw)
        rows = []
        for series_el in root.iter("Series"):
            ref_area = series_el.get("REF_AREA", "")
            if not ref_area.startswith("D"):
                continue  # on ne garde que les departements (pas les regions "R.." ni "FM"/"FE")
            code = ref_area[1:]  # "D33" -> "33"
            title = series_el.get("TITLE_FR", ref_area)
            for obs in series_el.findall("Obs"):
                period = obs.get("TIME_PERIOD")
                raw_value = obs.get("OBS_VALUE")
                if period is None or raw_value is None:
                    continue
                rows.append(
                    {
                        "source": "insee_taux_chomage_departements",
                        "territoire": code,
                        "date": _parse_time_period(period),
                        "indicateur": "taux_chomage_localise",
                        "valeur": float(raw_value),
                        "metadonnees": {"title": title, "raw_period": period},
                    }
                )
        df = pd.DataFrame(rows)
        if df.empty:
            return df
        df["date"] = pd.to_datetime(df["date"])
        return df.sort_values(["territoire", "date"]).reset_index(drop=True)
