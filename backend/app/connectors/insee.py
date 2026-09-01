"""Connecteur INSEE - Banque de Donnees Macroeconomiques (BDM) -- cahier des charges Helios §6.

Acces ouvert, sans cle, conforme aux conditions d'utilisation du service web
SDMX de l'Insee (https://www.insee.fr/fr/information/2862759). Retourne
exclusivement des series agregees nationales/regionales -- aucune donnee
individuelle n'existe dans ce service.
"""
from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from datetime import datetime

import httpx
import pandas as pd

from .base import Connector

BASE_URL = "https://bdm.insee.fr/series/sdmx/data/SERIES_BDM"
TERMS_OF_USE_URL = "https://www.insee.fr/fr/information/2862759"

# Quelques series de reference utiles a la demonstration (choix eclaires
# par le protocole de validation §5.7 : le taux de chomage BIT est l'un des
# episodes de reference cites), curatees manuellement -- pas de decouverte
# automatique de dataflow dans le MVP.
CURATED_SERIES = {
    "001688527": "Taux de chomage au sens du BIT - Ensemble - France hors Mayotte - CVS",
    "001515333": "Indice de reference des loyers (IRL)",
    "010001991": "Indices des prix des matieres premieres importees - Agro-industrielles",
    "001587668": "Indicateur synthetique de confiance des menages - CVS",
}

_PERIOD_PARSERS = [
    (re.compile(r"^(\d{4})$"), lambda m: f"{m.group(1)}-01-01"),
    (re.compile(r"^(\d{4})-(\d{2})$"), lambda m: f"{m.group(1)}-{m.group(2)}-01"),
    (re.compile(r"^(\d{4})-Q(\d)$"), lambda m: _quarter_to_date(m.group(1), m.group(2))),
]


def _quarter_to_date(year: str, quarter: str) -> str:
    month = (int(quarter) - 1) * 3 + 1
    return f"{year}-{month:02d}-01"


def _parse_time_period(period: str) -> str:
    for pattern, formatter in _PERIOD_PARSERS:
        m = pattern.match(period)
        if m:
            return formatter(m)
    return period


class InseeBdmConnector(Connector):
    name = "insee_bdm"
    terms_of_use_url = TERMS_OF_USE_URL

    async def fetch(self, idbank: str, start_period: str | None = None) -> str:
        params = {}
        if start_period:
            params["startPeriod"] = start_period
        url = f"{BASE_URL}/{idbank}"
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.text

    def normalize(self, raw: str) -> pd.DataFrame:
        root = ET.fromstring(raw)
        series_el = root.find(".//Series")
        if series_el is None:
            raise ValueError("Reponse INSEE inattendue : aucune serie trouvee")

        idbank = series_el.get("IDBANK", "")
        title = series_el.get("TITLE_FR", idbank)
        ref_area = series_el.get("REF_AREA", "")

        rows = []
        for obs in series_el.findall("Obs"):
            period = obs.get("TIME_PERIOD")
            raw_value = obs.get("OBS_VALUE")
            if period is None or raw_value is None:
                continue
            rows.append(
                {
                    "source": "insee_bdm",
                    "territoire": ref_area or "national",
                    "date": _parse_time_period(period),
                    "indicateur": idbank,
                    "valeur": float(raw_value),
                    "metadonnees": {"title": title, "idbank": idbank, "raw_period": period},
                }
            )

        df = pd.DataFrame(rows)
        if df.empty:
            return df
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date").reset_index(drop=True)
        df.attrs["title"] = title
        df.attrs["idbank"] = idbank
        return df
