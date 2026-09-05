"""Troisieme domaine d'application -- modele reduit de physique des plasmas
(bilan de puissance 0-D, seuil d'ignition) -- cahier des charges Helios
§7quater.

Reutilise EXACTEMENT le meme moteur de calcul statistique que H1 et Fusion
(variance/AC1 + surrogate_test, `stats/surrogates.py`), applique cette
fois a une temperature simulee par un vrai modele physique reduit
(`plasma_power_balance.py`) -- pas une donnee mesuree (contrairement a
Fusion, §7ter), pas une analogie sociale (contrairement a H4, §5.8).
Detection uniquement : ce module ne concoit aucun systeme de controle reel
de plasma (voir `scope_disclaimer` dans schemas.py). Jamais combine aux
deux autres domaines dans un meme verdict.
"""
from __future__ import annotations

from typing import Literal

import pandas as pd
from fastapi import APIRouter, Query

from ..plasma_power_balance import (
    ILLUSTRATIVE_IGNITED_HEATING_RATE,
    ILLUSTRATIVE_N_CM3,
    ILLUSTRATIVE_P_HEAT_BASE,
    ILLUSTRATIVE_STABLE_HEATING_RATE,
    ILLUSTRATIVE_TAU_E_S,
    ILLUSTRATIVE_T_MAX_S,
    simulate_power_balance,
)
from ..schemas import PlasmaAggregateResponse, PlasmaRunResult, SignificanceOut
from ..stats.surrogates import surrogate_test

router = APIRouter(prefix="/api/hypotheses", tags=["hypotheses"])

WINDOW_SAMPLES = 30  # fenetre glissante variance/AC1, sur l'echelle de temps du modele (dt=0.002s)
MAX_ANALYSIS_POINTS = 400  # meme raison que Fusion (MAX_ANALYSIS_POINTS) : garder le calcul gerable, les points les plus proches de l'ignition sont les plus pertinents


def _verdict(scenario: str, precursor: bool) -> str:
    if scenario == "stable":
        return (
            "Scénario stable (chauffage sous le seuil critique) : un signal a tort été jugé significatif "
            "-- faux positif à noter."
            if precursor
            else "Scénario stable : aucun signal significatif, comme attendu pour un cas de contrôle."
        )
    return (
        "Scénario ignité : signal précurseur (variance et/ou AC1) significatif avant l'emballement vers l'ignition."
        if precursor
        else "Scénario ignité : aucun signal précurseur significatif avant l'emballement vers l'ignition sur cette réalisation."
    )


def _run_one(seed: int, scenario: Literal["ignited", "stable"], n_surrogates: int) -> PlasmaRunResult:
    heating_rate = ILLUSTRATIVE_IGNITED_HEATING_RATE if scenario == "ignited" else ILLUSTRATIVE_STABLE_HEATING_RATE
    sim = simulate_power_balance(
        ILLUSTRATIVE_N_CM3,
        ILLUSTRATIVE_TAU_E_S,
        heating_rate=heating_rate,
        p_heat_base=ILLUSTRATIVE_P_HEAT_BASE,
        t_max=ILLUSTRATIVE_T_MAX_S,
        seed=seed,
    )
    cutoff = sim["t_ignition"] if sim["t_ignition"] is not None else float(sim["times"][-1])
    pre_mask = sim["times"] < cutoff
    pre_temp = pd.Series(sim["temperatures"][pre_mask])
    if len(pre_temp) > MAX_ANALYSIS_POINTS:
        pre_temp = pre_temp.iloc[-MAX_ANALYSIS_POINTS:].reset_index(drop=True)

    variance_sig = surrogate_test(pre_temp, WINDOW_SAMPLES, "variance", n_surrogates=n_surrogates, seed=seed)
    ac1_sig = surrogate_test(pre_temp, WINDOW_SAMPLES, "ac1", n_surrogates=n_surrogates, seed=seed + 1)
    precursor = bool(variance_sig["significant_at_0_05"] or ac1_sig["significant_at_0_05"])

    return PlasmaRunResult(
        seed=seed,
        scenario=scenario,
        ignited=sim["t_ignition"] is not None,
        t_ignition=sim["t_ignition"],
        peak_temperature_kev=float(sim["temperatures"].max()),
        n_points_analyzed=len(pre_temp),
        variance_significance=SignificanceOut(**variance_sig),
        ac1_significance=SignificanceOut(**ac1_sig),
        precursor_before_ignition=precursor,
        verdict_simple=_verdict(scenario, precursor),
    )


@router.get("/plasma", response_model=PlasmaRunResult)
async def test_plasma_run(
    seed: int = Query(default=0),
    scenario: Literal["ignited", "stable"] = Query(default="ignited"),
    n_surrogates: int = Query(default=200, ge=50, le=1000),
):
    return _run_one(seed, scenario, n_surrogates)


@router.get("/plasma/aggregate", response_model=PlasmaAggregateResponse)
async def test_plasma_aggregate(
    n_runs: int = Query(default=10, ge=5, le=30),
    n_surrogates: int = Query(default=50, ge=50, le=500),
):
    """Lance N réalisations "ignited" + N réalisations "stable" -- miroir de /hypotheses/fusion/aggregate."""
    results = [_run_one(seed, "ignited", n_surrogates) for seed in range(n_runs)]
    results += [_run_one(seed + 10_000, "stable", n_surrogates) for seed in range(n_runs)]

    n_ignited = sum(1 for r in results if r.scenario == "ignited")
    n_stable = len(results) - n_ignited
    n_ignited_with_precursor = sum(1 for r in results if r.scenario == "ignited" and r.precursor_before_ignition)
    n_stable_false_positive = sum(1 for r in results if r.scenario == "stable" and r.precursor_before_ignition)

    verdict = (
        f"{n_ignited_with_precursor}/{n_ignited} réalisations ignitées montrent un signal précurseur "
        f"avant l'emballement. Mais {n_stable_false_positive}/{n_stable} réalisations stables (cas de "
        "contrôle) montrent aussi un signal jugé significatif -- un faux positif à ne pas passer sous "
        "silence, pas seulement un résultat favorable à retenir."
    )

    return PlasmaAggregateResponse(
        n_runs=len(results),
        n_ignited=n_ignited,
        n_stable=n_stable,
        n_ignited_with_precursor=n_ignited_with_precursor,
        n_stable_false_positive=n_stable_false_positive,
        runs=results,
        verdict_simple=verdict,
    )
