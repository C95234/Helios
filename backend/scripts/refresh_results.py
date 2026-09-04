"""Rafraichissement automatique des resultats publies (H1, H2, H3, H5,
Fusion-sur-batterie-existante) -- cahier des charges Helios, chantier
"rafraichissement automatique sur les sources deja connectees".

Reutilise directement la logique des routers existants (import Python, pas
d'appel HTTP -- pas besoin d'un serveur qui tourne) et REFORME chaque
resultat dans la forme exacte deja consommee par la page Resultat
correspondante -- meme transformation que celle faite a la main pour
figer les resultats jusqu'ici.

Google Trends (acces non officiel, derogation ponctuelle deja assumee au
§6) et H4 (simulation pure, aucune donnee externe) restent EN DEHORS de ce
script -- decision utilisateur explicite (voir bilanPublie.js, en-tete).

Resilience : chaque hypothese est calculee dans son propre bloc
try/except. Un echec laisse le JSON existant INCHANGE plutot que d'ecrire
un resultat vide ou casse -- meme garde-fou que celui deja en place dans
curate_mast_shots.py (ne jamais ecraser une donnee valide par un resultat
degrade).

Usage : python -m scripts.refresh_results (depuis backend/, avec le venv
active -- fait de vrais appels reseau).
"""
from __future__ import annotations

import asyncio
import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
from fastapi import HTTPException

from app.phenomena import PHENOMENA
from app.routers.fusion import test_fusion_aggregate
from app.routers.h2 import test_h2
from app.routers.h3 import test_h3
from app.routers.h5 import test_h5
from app.routers.hypotheses import test_h1_aggregate

RESULTS_DIR = Path(__file__).resolve().parent.parent.parent / "frontend" / "src" / "data" / "results"
TODAY = date.today().isoformat()


def _write_if_ok(name: str, payload: dict) -> None:
    path = RESULTS_DIR / f"{name}.json"
    payload = {"refreshedAt": TODAY, **payload}
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"  {name}.json ecrit.")


def _h1_outcome(r) -> str:
    """Meme logique que le decompte agrege de test_h1_aggregate
    (routers/hypotheses.py), appliquee ici phenomene par phenomene."""
    peaked_before = r.decalage_jours is not None and r.decalage_jours > 0
    peaked_after = r.decalage_jours is not None and r.decalage_jours < 0
    favorable = peaked_before or (r.n_social_significant > 0 and r.n_official_significant == 0)
    against = peaked_after or (r.n_official_significant > 0 and r.n_social_significant == 0)
    if favorable and not against:
        return "favorable"
    if against and not favorable:
        return "against"
    return "neutral"


async def refresh_h1() -> None:
    print("H1...")
    agg = await test_h1_aggregate(n_surrogates=60)
    if not agg.results:
        raise RuntimeError("Aucun phenomene H1 exploitable -- run abandonne pour H1.")
    phenomena = [
        {
            "label": r.phenomenon_label,
            "nOffSig": r.n_official_significant,
            "nOff": len(r.official_signals),
            "nSocSig": r.n_social_significant,
            "nSoc": len(r.social_signals),
            "decalageJours": r.decalage_jours,
            "outcome": _h1_outcome(r),
        }
        for r in agg.results
    ]
    summary = {
        "favorable": agg.n_favorable_to_h1,
        "against": agg.n_against_h1,
        "neutral": agg.n_neutral,
        "nPhenomena": agg.n_phenomena_tested,
    }
    _write_if_ok("h1", {"phenomena": phenomena, "summary": summary})


async def refresh_h2() -> None:
    print("H2...")
    # Les valeurs par defaut des routers sont des objets fastapi.Query --
    # resolus automatiquement lors d'une vraie requete HTTP, mais PAS quand
    # la fonction est appelee directement en Python : il faut les repasser
    # explicitement, sinon le code plante en les traitant comme des entiers.
    r = await test_h2(n_surrogates=500, n_permutations_snapshot=300)
    real_values = [v for v in r.real_network.moran_series.values if v is not None]
    grid_values = [v for v in r.control_grid.moran_series.values if v is not None]
    n_real_above_grid = sum(
        1
        for real, grid in zip(r.real_network.moran_series.values, r.control_grid.moran_series.values)
        if real is not None and grid is not None and real > grid
    )
    result = {
        "periodStart": r.period_start,
        "periodEnd": r.period_end,
        "nUnits": r.n_units,
        "nQuarters": r.n_quarters,
        "nEdgesRealNetwork": r.n_edges_real_network,
        "realNetwork": {
            "trendTau": round(r.real_network.trend.observed_tau, 3) if r.real_network.trend.observed_tau is not None else None,
            "trendP": round(r.real_network.trend.p_value, 3) if r.real_network.trend.p_value is not None else None,
            "trendSig": r.real_network.trend.significant_at_0_05,
            "latestI": round(r.real_network.latest_snapshot.observed_i, 3) if r.real_network.latest_snapshot.observed_i is not None else None,
            "latestP": round(r.real_network.latest_snapshot.p_value, 3) if r.real_network.latest_snapshot.p_value is not None else None,
            "latestSig": r.real_network.latest_snapshot.significant_at_0_05,
        },
        "controlGrid": {
            "trendTau": round(r.control_grid.trend.observed_tau, 3) if r.control_grid.trend.observed_tau is not None else None,
            "trendP": round(r.control_grid.trend.p_value, 3) if r.control_grid.trend.p_value is not None else None,
            "trendSig": r.control_grid.trend.significant_at_0_05,
            "latestI": round(r.control_grid.latest_snapshot.observed_i, 3) if r.control_grid.latest_snapshot.observed_i is not None else None,
            "latestP": round(r.control_grid.latest_snapshot.p_value, 3) if r.control_grid.latest_snapshot.p_value is not None else None,
            "latestSig": r.control_grid.latest_snapshot.significant_at_0_05,
        },
        "realMean": round(float(np.mean(real_values)), 3) if real_values else None,
        "realStd": round(float(np.std(real_values)), 3) if real_values else None,
        "gridMean": round(float(np.mean(grid_values)), 3) if grid_values else None,
        "gridStd": round(float(np.std(grid_values)), 3) if grid_values else None,
        "nRealAboveGrid": n_real_above_grid,
        "nQuartersTotal": len(r.real_network.moran_series.dates),
    }
    moran_series = {
        "dates": r.real_network.moran_series.dates,
        "real": r.real_network.moran_series.values,
        "grid": r.control_grid.moran_series.values,
    }
    _write_if_ok("h2", {"result": result, "moranSeries": moran_series})


async def refresh_h3() -> None:
    print("H3...")
    phenomena = []
    unavailable = []
    for code, spec in PHENOMENA.items():
        try:
            r = await test_h3(phenomenon=code, insee_window=4)
        except HTTPException as exc:
            unavailable.append({"label": spec["label"], "reason": exc.detail})
            continue
        phenomena.append(
            {
                "label": r.phenomenon_label,
                "tau": round(r.observed_national_tau, 3) if r.observed_national_tau is not None else None,
                "moran": round(r.observed_spatial_i, 3) if r.observed_spatial_i is not None else None,
                "pJoint": round(r.p_joint, 3) if r.p_joint is not None else None,
                "sig": r.significant_at_0_05,
            }
        )
    if not phenomena:
        raise RuntimeError("Aucun phenomene H3 calculable -- run abandonne pour H3.")
    summary = {
        "favorable": sum(1 for p in phenomena if p["sig"]),
        "neutral": sum(1 for p in phenomena if not p["sig"]),
        "unavailable": len(unavailable),
        "nCalculable": len(phenomena),
    }
    _write_if_ok("h3", {"phenomena": phenomena, "unavailable": unavailable, "summary": summary})


async def refresh_h5() -> None:
    print("H5...")
    r = await test_h5(n_synthetic=200, seed=42)
    payload = {
        "alpha": r.alpha,
        "xmin": r.xmin,
        "ksStatistic": r.ks_statistic,
        "nTail": r.n_tail,
        "nTotal": r.n_total,
        "nDepartments": r.n_departments,
        "nQuarters": r.n_quarters,
        "periodStart": r.period_start,
        "periodEnd": r.period_end,
        "pPlausibility": r.p_plausibility,
        "nSynthetic": r.n_synthetic,
        "lognormal": {"r": round(r.lognormal.r, 4), "pValue": r.lognormal.p_value, "favorsPowerLaw": r.lognormal.favors_power_law},
        "exponential": {"r": round(r.exponential.r, 4), "pValue": r.exponential.p_value, "favorsPowerLaw": r.exponential.favors_power_law},
        "verdict": r.verdict,
    }
    _write_if_ok("h5", payload)


def _fusion_verdict(agg) -> str:
    """Meme seuils que aggregateVerdict() dans FusionResult.jsx -- dupliquee
    ici faute d'un endroit commun entre le script Python et le frontend JS."""
    if agg.n_disrupted == 0:
        return "neutral"
    hit_rate = agg.n_disrupted_with_precursor / agg.n_disrupted
    false_positive_rate = (agg.n_stable_false_positive / agg.n_stable) if agg.n_stable > 0 else 0.0
    if hit_rate == 0:
        return "against"
    if hit_rate >= 0.5 and false_positive_rate < 0.5:
        return "favorable"
    return "neutral"


async def refresh_fusion() -> None:
    print("Fusion (sur la batterie deja curatee)...")
    agg = await test_fusion_aggregate(n_surrogates=50)
    shots = [
        {
            "shotId": s.shot_id,
            "campaign": s.campaign,
            "disrupted": s.disrupted,
            "tQuench": s.t_quench,
            "peakCurrentKa": round(s.peak_current_ka, 1),
            "varianceSig": s.variance_significance.significant_at_0_05,
            "ac1Sig": s.ac1_significance.significant_at_0_05,
            "moranSig": s.moran_trend.significant_at_0_05,
            "precursor": s.precursor_before_quench,
        }
        for s in agg.shots
    ]
    payload = {
        "nShots": agg.n_shots,
        "nDisrupted": agg.n_disrupted,
        "nStable": agg.n_stable,
        "nDisruptedWithPrecursor": agg.n_disrupted_with_precursor,
        "nStableFalsePositive": agg.n_stable_false_positive,
        "verdict": _fusion_verdict(agg),
        "shots": shots,
    }
    _write_if_ok("fusion", payload)


ALL_TASKS = {
    "h1": refresh_h1,
    "h2": refresh_h2,
    "h3": refresh_h3,
    "h5": refresh_h5,
    "fusion": refresh_fusion,
}


async def main() -> None:
    """--only NAME (ex. --only fusion) limite le run a une seule hypothese --
    utilise par grow-mast-battery.yml pour ne regenerer que fusion.json apres
    une curation de nouveaux tirs, sans retoucher H1/H2/H3/H5."""
    only = sys.argv[sys.argv.index("--only") + 1] if "--only" in sys.argv else None
    tasks = {only: ALL_TASKS[only]} if only else ALL_TASKS
    failures = []
    for label, task in tasks.items():
        try:
            await task()
        except Exception as exc:
            print(f"  {label} : ECHEC, JSON existant conserve ({exc})")
            failures.append(label)

    if failures:
        print(f"\nTermine avec {len(failures)} echec(s) : {', '.join(failures)} (JSON existants conserves pour ceux-la).")
    else:
        print("\nTermine, tout rafraichi avec succes.")


if __name__ == "__main__":
    asyncio.run(main())
