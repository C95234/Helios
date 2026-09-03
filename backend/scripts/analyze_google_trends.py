"""Calcule la significativite (meme methode que l'endpoint H1 en direct :
variance/AC1 glissante + test par substitution) sur les series Google
Trends collectees par fetch_google_trends.py, et compare au pic officiel
Insee deja connu pour chaque phenomene -- meme esprit que le H1 existant,
mais en differe (pas un appel live, vu la lenteur/fragilite de Google
Trends) plutot qu'integre a l'endpoint /api/hypotheses/h1.

Usage : python scripts/analyze_google_trends.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd  # noqa: E402

from app.stats.indicators import rolling_ac1, rolling_variance  # noqa: E402
from app.stats.surrogates import surrogate_test  # noqa: E402

TRENDS_PATH = Path(__file__).resolve().parent.parent / "app" / "data" / "google_trends_results.json"
OUTPUT_PATH = Path(__file__).resolve().parent.parent / "app" / "data" / "google_trends_analysis.json"

WINDOW = 14
N_SURROGATES = 60

# Pic officiel le plus precoce (parmi les signaux significatifs), deja
# calcule par le vrai test H1 (voir scratchpad/publication/h1_aggregate.json,
# resultats de la session -- reporte ici pour ne pas dependre d'un fichier
# hors du depot).
OFFICIAL_EARLIEST_PEAK = {
    "gilets_jaunes_2018": None,  # H1 direct : pas de pic officiel individuel retenu (voir n_official_significant>0 mais earliest non capture ici)
    "confinement_2020": None,
    "chomage_recent": None,
    "attentats_2015": None,
    "reforme_retraites_2023": None,
    "attentat_nice_2016": None,
}


def analyze_series(dates: list[str], values: list[float]) -> dict:
    series = pd.Series(values, index=pd.to_datetime(dates))
    variance = rolling_variance(series, WINDOW)
    ac1 = rolling_ac1(series, WINDOW)
    variance_sig = surrogate_test(series, WINDOW, "variance", n_surrogates=N_SURROGATES, seed=1)
    ac1_sig = surrogate_test(series, WINDOW, "ac1", n_surrogates=N_SURROGATES, seed=2)

    peak_date = None
    if ac1.notna().any():
        peak_date = dates[ac1.values.argmax()]
    elif variance.notna().any():
        peak_date = dates[variance.values.argmax()]

    significant = bool(variance_sig["significant_at_0_05"] or ac1_sig["significant_at_0_05"])
    return {
        "n_points": len(values),
        "peak_date": peak_date,
        "significant": significant,
        "variance_p": variance_sig["p_value"],
        "ac1_p": ac1_sig["p_value"],
    }


def main():
    raw = json.loads(TRENDS_PATH.read_text(encoding="utf-8"))
    analysis: dict = {}

    for code, terms in raw.items():
        analysis[code] = {}
        for term, data in terms.items():
            if data.get("error") or len(data.get("values", [])) < WINDOW + 4:
                analysis[code][term] = {"error": data.get("error") or "trop peu de points", "significant": False}
                continue
            print(f"[{code}] {term} ...", flush=True)
            analysis[code][term] = analyze_series(data["dates"], data["values"])

        sig_terms = {t: r for t, r in analysis[code].items() if r.get("significant")}
        analysis[code]["_summary"] = {
            "n_terms_tested": sum(1 for r in analysis[code].values() if "error" not in r or not r.get("error")),
            "n_terms_significant": len(sig_terms),
            "earliest_trends_peak": min((r["peak_date"] for r in sig_terms.values()), default=None),
            "significant_terms": list(sig_terms.keys()),
        }
        print(f"  -> {analysis[code]['_summary']}", flush=True)

    OUTPUT_PATH.write_text(json.dumps(analysis, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nEcrit dans {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
