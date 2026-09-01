"""Connecteur Wikimedia -- activite d'edition d'un article -- cahier des charges Helios §6.

Types de signaux sociaux distincts des vues (frequentation passive), tous
deux derives de la meme requete a l'historique des revisions :
- "edit_count" : nombre de modifications par jour (intensite d'activite).
- "unique_editors" : nombre de contributeurs DIFFERENTS par jour (est-ce
  qu'une seule personne edite beaucoup, ou est-ce que beaucoup de monde
  s'y met ?) -- une lecture differente du meme evenement, pas un doublon.

Meme plateforme que le connecteur pageviews, mais une API differente
(MediaWiki Action API, historique des revisions).

Acces ouvert, sans cle. Les identifiants de compte sont utilises uniquement
pour un COMPTAGE agrege (nombre de contributeurs distincts par jour) --
jamais exposes individuellement en sortie (§9.1, §9.2).
"""
from __future__ import annotations

import httpx
import pandas as pd

from ..http_utils import get_with_retry
from .base import Connector
from .wikipedia import TERMS_OF_USE_URL, USER_AGENT

API_URL = "https://fr.wikipedia.org/w/api.php"
MAX_PAGES = 20  # garde-fou : au plus 20*500 = 10000 revisions par requete


class WikipediaEditActivityConnector(Connector):
    name = "wikipedia_edit_activity"
    terms_of_use_url = TERMS_OF_USE_URL

    async def fetch(self, article: str, start: str, end: str) -> list[dict]:
        """Renvoie une liste de {timestamp, user} pour chaque revision de `article` dans [start, end]."""
        article_title = article.replace("_", " ").replace("%20", " ")
        for pair in [("%C3%A9", "é"), ("%C3%A8", "è"), ("%C3%B4", "ô"), ("%27", "'")]:
            article_title = article_title.replace(*pair)

        revisions: list[dict] = []
        params = {
            "action": "query",
            "prop": "revisions",
            "titles": article_title,
            "rvlimit": 500,
            "rvprop": "timestamp|user",
            "format": "json",
            "rvstart": f"{end}T23:59:59Z",
            "rvend": f"{start}T00:00:00Z",
            "rvdir": "older",
        }

        async with httpx.AsyncClient(timeout=20.0, headers={"User-Agent": USER_AGENT}) as client:
            for _ in range(MAX_PAGES):
                response = await get_with_retry(client, API_URL, params=params)
                data = response.json()
                pages = data.get("query", {}).get("pages", {})
                for page in pages.values():
                    for rev in page.get("revisions", []):
                        revisions.append({"timestamp": rev["timestamp"], "user": rev.get("user", "?")})

                if "continue" in data:
                    params["rvcontinue"] = data["continue"]["rvcontinue"]
                else:
                    break

        return revisions

    def normalize(self, raw: list[dict], start: str | None = None, end: str | None = None, mode: str = "edit_count") -> pd.DataFrame:
        """Un jour sans activite vaut 0, pas "donnee manquante" -- necessaire pour que la
        serie soit uniformement echantillonnee (condition des calculs de variance/AC1/surrogates).

        mode: "edit_count" (nombre de modifications/jour) ou "unique_editors" (nombre de
        contributeurs distincts/jour).
        """
        if start is None or end is None:
            if not raw:
                return pd.DataFrame()
            timestamps = pd.to_datetime([r["timestamp"][:10] for r in raw])
            start = start or timestamps.min().strftime("%Y-%m-%d")
            end = end or timestamps.max().strftime("%Y-%m-%d")

        full_range = pd.date_range(start, end, freq="D")
        if raw:
            frame = pd.DataFrame(raw)
            frame["date"] = pd.to_datetime(frame["timestamp"].str[:10])
            if mode == "unique_editors":
                counts = frame.groupby("date")["user"].nunique()
            else:
                counts = frame.groupby("date").size()
        else:
            counts = pd.Series(dtype=float)

        counts = counts.reindex(full_range, fill_value=0)
        df = counts.reset_index()
        df.columns = ["date", "valeur"]
        df["valeur"] = df["valeur"].astype(float)
        return df
