"""Collecte les series Google Trends (terme direct + panier oblique fixe)
pour les 6 phenomenes deja curatures dans phenomena.py -- utilise pour
reevaluer H1 avec Google Trends comme troisieme signal social, a cote de
Wikipedia. Voir connectors/google_trends.py pour la derogation documentee.

Requetes espacees pour respecter le rate-limit non documente de Google
Trends -- script lent par construction (~5-10 min), pas un endpoint produit.

Usage : python scripts/fetch_google_trends.py
"""
from __future__ import annotations

import asyncio
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.connectors.google_trends import OBLIQUE_TERMS, GoogleTrendsConnector  # noqa: E402

OUTPUT_PATH = Path(__file__).resolve().parent.parent / "app" / "data" / "google_trends_results.json"

PHENOMENA = {
    "gilets_jaunes_2018": {"start": "2018-06-01", "end": "2019-03-01", "direct_term": "gilets jaunes"},
    "confinement_2020": {"start": "2019-10-01", "end": "2020-08-01", "direct_term": "confinement"},
    "chomage_recent": {"start": "2024-01-01", "end": "2026-08-01", "direct_term": None},
    "attentats_2015": {"start": "2015-08-01", "end": "2016-03-01", "direct_term": "attentat paris"},
    "reforme_retraites_2023": {"start": "2022-10-01", "end": "2023-07-01", "direct_term": "réforme des retraites"},
    "attentat_nice_2016": {"start": "2016-04-01", "end": "2016-11-01", "direct_term": "attentat nice"},
}

DELAY_BETWEEN_REQUESTS = 6.0


async def main():
    connector = GoogleTrendsConnector()
    results: dict = {}

    for code, spec in PHENOMENA.items():
        results[code] = {}
        terms = OBLIQUE_TERMS.copy()
        if spec["direct_term"]:
            terms = [spec["direct_term"]] + terms

        for term in terms:
            print(f"[{code}] {term} ...", flush=True)
            t0 = time.time()
            try:
                series = await connector.fetch_series(term, spec["start"], spec["end"])
                results[code][term] = {
                    "dates": [d.strftime("%Y-%m-%d") for d in series.index],
                    "values": series.tolist(),
                    "error": None,
                }
                print(f"  -> {len(series)} points en {time.time()-t0:.1f}s", flush=True)
            except Exception as exc:
                results[code][term] = {"dates": [], "values": [], "error": str(exc)}
                print(f"  -> ECHEC : {exc}", flush=True)
            await asyncio.sleep(DELAY_BETWEEN_REQUESTS)

    OUTPUT_PATH.write_text(json.dumps(results, ensure_ascii=False), encoding="utf-8")
    print(f"\nEcrit dans {OUTPUT_PATH}")


if __name__ == "__main__":
    asyncio.run(main())
