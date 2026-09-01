"""Connecteur Wikimedia Pageviews -- cahier des charges Helios §6.

Substitut pragmatique au connecteur GDELT nomme dans le cahier des charges
(§6, table) : GDELT expose son API de timeline pretraitee sur un sous-domaine
qui s'est revele inaccessible depuis l'environnement de developpement de ce
projet, et ses fichiers bruts (exports 15 minutes, plusieurs centaines de Mo
par jour) ne se pretent pas a une requete interactive sans pipeline d'ingestion
dedie. Les vues quotidiennes d'articles Wikipedia jouent ici le meme role
qu'assignait le cahier des charges a GDELT/Google Trends : un signal social
rapide, bruite, mais precoce (§1).

Acces ouvert, sans cle, donnees sous licence CC0 (domaine public), agregees
(nombre de vues par jour, jamais de donnee individuelle) -- conforme aux
Wikimedia Foundation API Usage Guidelines
(https://foundation.wikimedia.org/wiki/Policy:Wikimedia_Foundation_API_Usage_Guidelines).
Un User-Agent descriptif est requis par cette politique et fourni ci-dessous.
"""
from __future__ import annotations

import httpx
import pandas as pd

from ..http_utils import get_with_retry
from .base import Connector

BASE_URL = "https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article"
TERMS_OF_USE_URL = "https://foundation.wikimedia.org/wiki/Policy:Wikimedia_Foundation_API_Usage_Guidelines"
USER_AGENT = "Helios-Research-Tool/0.1 (projet de recherche sur les signaux precurseurs ; contact via github)"

# Articles francophones curates comme proxy de "signal social" pour des
# phenomenes reels -- pas de decouverte automatique dans le MVP.
CURATED_ARTICLES = {
    "Gilets_jaunes": "Mouvement des Gilets jaunes",
    "Ch%C3%B4mage_en_France": "Chômage en France",
    "Confinement_de_2020_en_France": "Confinement de 2020 en France",
    "Gr%C3%A8ve_g%C3%A9n%C3%A9rale": "Grève générale",
}


class WikipediaPageviewsConnector(Connector):
    name = "wikipedia_pageviews"
    terms_of_use_url = TERMS_OF_USE_URL

    async def fetch(self, article: str, start: str, end: str, project: str = "fr.wikipedia") -> dict:
        """start/end au format YYYY-MM-DD."""
        start_compact = start.replace("-", "")
        end_compact = end.replace("-", "")
        url = f"{BASE_URL}/{project}/all-access/user/{article}/daily/{start_compact}/{end_compact}"
        async with httpx.AsyncClient(timeout=15.0, headers={"User-Agent": USER_AGENT}) as client:
            response = await get_with_retry(client, url)
            return response.json()

    def normalize(self, raw: dict) -> pd.DataFrame:
        items = raw.get("items", [])
        rows = []
        for item in items:
            timestamp = item["timestamp"]  # YYYYMMDDHH
            date = f"{timestamp[0:4]}-{timestamp[4:6]}-{timestamp[6:8]}"
            rows.append(
                {
                    "source": "wikipedia_pageviews",
                    "territoire": "FR",
                    "date": date,
                    "indicateur": item["article"],
                    "valeur": float(item["views"]),
                    "metadonnees": {"project": item["project"], "access": item["access"]},
                }
            )
        df = pd.DataFrame(rows)
        if df.empty:
            return df
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date").reset_index(drop=True)
        df.attrs["title"] = raw.get("items", [{}])[0].get("article", "") if items else ""
        return df

    async def fetch_combined(self, articles: list[str], start: str, end: str) -> pd.DataFrame:
        """Somme les vues quotidiennes de plusieurs articles lies au meme phenomene.

        Un seul article choisi a la main est un signal social fragile et arbitraire
        (retour utilisateur) ; sommer plusieurs articles thematiquement lies reduit
        cette arbitraire sans pretendre a une methode de selection automatisee.
        """
        frames = []
        labels = []
        for article in articles:
            raw = await self.fetch(article=article, start=start, end=end)
            df = self.normalize(raw)
            if df.empty:
                continue
            frames.append(df.set_index("date")["valeur"])
            labels.append(df.attrs.get("title", article))

        if not frames:
            return pd.DataFrame()

        combined = pd.concat(frames, axis=1).sum(axis=1, skipna=True)
        out = combined.reset_index()
        out.columns = ["date", "valeur"]
        out.attrs["title"] = " + ".join(labels)
        out.attrs["n_articles"] = len(frames)
        return out
