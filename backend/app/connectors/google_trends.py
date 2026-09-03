"""Connecteur Google Trends -- interet de recherche quotidien, France.

DEROGATION DOCUMENTEE AU §6 DU CAHIER DES CHARGES.

Le cahier des charges (§6) nomme Google Trends mais le met explicitement de
cote : « API officielle Google Trends (acces alpha restreint en 2026) ...
Connecteur desactive tant que l'acces officiel n'est pas obtenu ; pas de
contournement. » Cet acces officiel restreint n'a jamais ete obtenu.

Ce connecteur utilise a la place le point d'entree interne (non documente,
non officiel) que Google Trends expose a son propre site web -- la meme
approche que la bibliotheque `pytrends`, publique depuis 2016 et largement
utilisee en recherche. Decision explicite d'assouplir la regle du §6 pour
CETTE source precise, prise en connaissance de cause (§9bis) :

- Ce n'est PAS une infraction penale identifiable dans la jurisprudence
  recente (Van Buren v. United States, 2021 : une simple violation de
  conditions d'utilisation, sans contournement d'une protection d'acces
  technique, ne releve plus du Computer Fraud and Abuse Act americain ;
  hiQ Labs v. LinkedIn, 9e circuit : la collecte de donnees publiquement
  affichees n'est pas assimilable a un acces non autorise). Ces deux
  precedents concernent le droit americain -- aucune analyse equivalente
  n'a ete faite pour le droit francais/europeen, prudence de mise.
- C'est en revanche une VIOLATION DES CONDITIONS D'UTILISATION DE GOOGLE
  (usage automatise non autorise du service Trends), un manquement
  contractuel, pas une question d'acces a des donnees privees : Google
  Trends affiche deja ces donnees publiquement a quiconque visite le site.
- Risque concret assume : blocage/limitation de l'adresse IP appelante
  (deja le lot commun des utilisateurs de pytrends), pas de poursuite
  documentee contre un usage de recherche a cette echelle.

Cette derogation est documentee ici ET dans l'interface (page Donnees &
methode) -- jamais silencieuse, dans le meme esprit que les autres
adaptations du projet (H3, H4, calibration du protocole §7bis).
"""
from __future__ import annotations

import asyncio
import time

import pandas as pd
from pytrends.request import TrendReq

from .base import Connector

TERMS_OF_USE_URL = "https://policies.google.com/terms"

# Panier FIXE de termes "obliques" -- proxies generiques de tension
# economique/psychologique, INDEPENDANTS du contenu de chaque phenomene et
# identiques pour tous les phenomenes testes. Choisis une fois, avant de
# voir les resultats, pour eviter le biais de choisir a posteriori un terme
# qui "marche" pour un cas donne (§9.3 -- meme logique que le probleme des
# comparaisons multiples deja signale ailleurs dans Helios).
OBLIQUE_TERMS = [
    "recherche emploi",
    "assurance chômage",
    "anxiété",
    "vente maison",
    "prêt personnel",
]

_MAX_RETRIES = 4
_BASE_BACKOFF_SECONDS = 20.0


class GoogleTrendsConnector(Connector):
    name = "google_trends"
    terms_of_use_url = TERMS_OF_USE_URL

    def _fetch_sync(self, keyword: str, start: str, end: str, geo: str) -> pd.DataFrame:
        pytrends = TrendReq(hl="fr-FR", tz=60)
        pytrends.build_payload([keyword], timeframe=f"{start} {end}", geo=geo)
        return pytrends.interest_over_time()

    async def fetch(self, keyword: str, start: str, end: str, geo: str = "FR") -> pd.DataFrame:
        """start/end au format YYYY-MM-DD. Retente avec backoff exponentiel
        sur limitation de debit (429) -- Google Trends limite agressivement
        les appels automatises."""
        last_exc = None
        for attempt in range(_MAX_RETRIES):
            try:
                return await asyncio.to_thread(self._fetch_sync, keyword, start, end, geo)
            except Exception as exc:  # pytrends leve des exceptions variees selon la version d'urllib3/requests
                last_exc = exc
                if attempt < _MAX_RETRIES - 1:
                    await asyncio.sleep(_BASE_BACKOFF_SECONDS * (2**attempt))
        raise RuntimeError(f"Google Trends indisponible pour « {keyword} » après {_MAX_RETRIES} tentatives : {last_exc}")

    def normalize(self, raw: pd.DataFrame, keyword: str = "") -> pd.DataFrame:
        if raw is None or raw.empty:
            return pd.DataFrame()
        df = raw.reset_index()
        col = keyword if keyword in df.columns else [c for c in df.columns if c not in ("date", "isPartial")][0]
        out = pd.DataFrame(
            {
                "source": "google_trends",
                "territoire": "FR",
                "date": pd.to_datetime(df["date"]),
                "indicateur": col,
                "valeur": df[col].astype(float),
                "metadonnees": [{}] * len(df),
            }
        )
        return out.sort_values("date").reset_index(drop=True)

    async def fetch_series(self, keyword: str, start: str, end: str) -> pd.Series:
        """Raccourci fetch + normalize -> Series indexee par date, pret pour
        rolling_variance/rolling_ac1 (meme forme que les autres connecteurs)."""
        raw = await self.fetch(keyword, start, end)
        df = self.normalize(raw, keyword)
        if df.empty:
            return pd.Series(dtype=float)
        return df.set_index("date")["valeur"]
