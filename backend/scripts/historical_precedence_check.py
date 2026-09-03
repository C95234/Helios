"""Confronte le test de precedence variance/Moran a des episodes historiques
REELS (pas simules) -- cahier des charges §7bis, "instructions pour la
suite", point 3 : chomage 2008-2009, mouvement social 2018, tension
sanitaire 2020 (§5.7).

Reutilise l'infrastructure deja en place pour H1/H2/H3 (meme serie
nationale, meme reseau spatial departemental) plutot que d'ajouter un
nouveau connecteur -- aucune donnee ici n'est nouvelle, seule la question
posee (precedence) differe des modules H1/H2/H3 deja livres.

Limite assumee : le chomage departemental est publie au TRIMESTRE (pas de
tendance fine possible sur une fenetre de quelques mois, meme limite deja
documentee pour H3) -- la comparaison porte donc sur "quel trimestre / quel
mois porte le pic", pas sur un test de tendance formel comme en simulation.

Usage : python scripts/historical_precedence_check.py (necessite un acces
reseau vers l'API Insee).
"""
from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd  # noqa: E402

from app.connectors.insee import InseeBdmConnector  # noqa: E402
from app.spatial_series import get_real_network_moran_series  # noqa: E402
from app.stats.indicators import rolling_ac1, rolling_variance  # noqa: E402

NATIONAL_IDBANK = "001587668"  # confiance des menages -- meme serie que H3
WINDOW_MONTHS = 6

EPISODES = {
    "chomage_2008_2009": {
        "label": "Choc de chomage 2008-2009 (crise financiere)",
        "start": "2007-10-01",
        "end": "2009-12-01",
    },
    "gilets_jaunes_2018": {
        "label": "Mouvement social 2018 (gilets jaunes)",
        "start": "2018-06-01",
        "end": "2019-03-01",
    },
    "confinement_2020": {
        "label": "Tension sanitaire 2020 (premier confinement)",
        "start": "2019-10-01",
        "end": "2020-08-01",
    },
}


async def main():
    insee = InseeBdmConnector()
    raw = await insee.fetch(idbank=NATIONAL_IDBANK, start_period="2000-01")
    national_df = insee.normalize(raw)
    national_series = national_df.set_index("date")["valeur"]

    spatial = await get_real_network_moran_series()
    moran_series = pd.Series(spatial["i_real"], index=spatial["dates"])

    # Indicateurs glissants calcules UNE FOIS sur la serie complete (avec tout
    # son historique avant chaque episode), jamais sur une serie tronquee --
    # sinon les premiers points de chaque fenetre glissante manquent de
    # contexte et le "pic" est artificiellement tire vers le debut de la
    # fenetre observee (effet de bord, pas un vrai signal precurseur).
    variance_full = rolling_variance(national_series, WINDOW_MONTHS)
    ac1_full = rolling_ac1(national_series, WINDOW_MONTHS)

    report = {}
    for code, ep in EPISODES.items():
        start, end = pd.Timestamp(ep["start"]), pd.Timestamp(ep["end"])

        window_nat = national_series[(national_series.index >= start) & (national_series.index <= end)]
        window_variance = variance_full[(variance_full.index >= start) & (variance_full.index <= end)]
        window_ac1 = ac1_full[(ac1_full.index >= start) & (ac1_full.index <= end)]
        temporal_peak = None
        if window_ac1.notna().any():
            temporal_peak = str(window_ac1.idxmax().date())
        elif window_variance.notna().any():
            temporal_peak = str(window_variance.idxmax().date())

        window_moran = moran_series[(moran_series.index >= start) & (moran_series.index <= end)]
        spatial_peak = None
        if len(window_moran) > 0:
            spatial_peak = str(window_moran.index[window_moran.values.argmax()].date())

        precedence = None
        if temporal_peak and spatial_peak:
            precedence = "temporel" if temporal_peak < spatial_peak else ("spatial" if spatial_peak < temporal_peak else "simultane")

        result = {
            "label": ep["label"],
            "start": ep["start"],
            "end": ep["end"],
            "n_monthly_points": len(window_nat),
            "n_quarterly_points": len(window_moran),
            "temporal_peak_date": temporal_peak,
            "spatial_peak_date": spatial_peak,
            "precedence": precedence,
        }
        report[code] = result
        print(code, "->", result)

    out_path = Path(__file__).resolve().parent.parent / "app" / "data" / "journal_historical_precedence.json"
    out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nRapport ecrit dans {out_path}")


if __name__ == "__main__":
    asyncio.run(main())
