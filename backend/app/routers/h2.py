from __future__ import annotations

import pandas as pd
from fastapi import APIRouter, HTTPException, Query

from ..connectors.insee_departments import (
    CONSTRUCTION_CONNECTOR,
    CREATIONS_CONNECTOR,
    DEFAILLANCES_CONNECTOR,
    POPULATION_CONNECTOR,
    UNEMPLOYMENT_CONNECTOR,
)
from ..schemas import (
    DepartmentValueOut,
    H2AggregateResponse,
    H2Response,
    H2VariableResult,
    MoranSeriesOut,
    MoranTestOut,
    TrendTestOut,
)
from ..spatial_series import SpatialDataUnavailable, compute_network_moran_series, get_department_wide, get_real_network_moran_series
from ..stats.moran import permutation_test
from ..stats.surrogates import surrogate_trend_test

router = APIRouter(prefix="/api/hypotheses", tags=["hypotheses"])

# Cinq variables reelles au niveau departement -- "pousser" H2 au-dela du
# seul chomage (verifie en direct sur le catalogue SDMX Insee, 244
# dataflows : REF_AREA=Dxx confirme pour chacune, attributs de filtre
# exacts dans connectors/insee_departments.py). CREATIONS n'a pas de
# variante CVS au niveau departement (verifie) -- cumul glissant 12 mois
# applique ici, meme transformation que celle deja publiee par l'Insee
# pour DEFAILLANCES/CONSTRUCTION, pour rester comparable sans methode ad hoc.
VARIABLES = {
    "chomage": {
        "label": "Taux de chômage localisé",
        "connector": UNEMPLOYMENT_CONNECTOR,
        "start_period": "2000-Q1",
        "rolling_12": False,
    },
    "defaillances": {
        "label": "Défaillances d'entreprises (cumul 12 mois)",
        "connector": DEFAILLANCES_CONNECTOR,
        "start_period": "2000-01",
        "rolling_12": False,
    },
    "construction": {
        "label": "Logements autorisés (cumul 12 mois)",
        "connector": CONSTRUCTION_CONNECTOR,
        "start_period": "2000-01",
        "rolling_12": False,
    },
    "creations": {
        "label": "Créations d'entreprises (cumul 12 mois)",
        "connector": CREATIONS_CONNECTOR,
        "start_period": "2012-01",
        "rolling_12": True,
    },
    "population": {
        "label": "Estimations de population",
        "connector": POPULATION_CONNECTOR,
        "start_period": None,
        "rolling_12": False,
    },
}


def _trend_out(result: dict) -> TrendTestOut:
    return TrendTestOut(**result)


def _snapshot_out(result: dict) -> MoranTestOut:
    p = result["p_value"]
    return MoranTestOut(
        observed_i=result["observed_i"],
        p_value=p,
        n_permutations=result["n_permutations"],
        null_mean=result.get("null_mean"),
        null_std=result.get("null_std"),
        significant_at_0_05=bool(p is not None and p == p and p < 0.05),
    )


def _outcome(real_sig: bool, grid_sig: bool) -> str:
    if real_sig and not grid_sig:
        return "favorable"
    if grid_sig and not real_sig:
        return "against"
    return "neutral"


def _verdict(real_trend: TrendTestOut, grid_trend: TrendTestOut) -> str:
    outcome = _outcome(real_trend.significant_at_0_05, grid_trend.significant_at_0_05)
    if outcome == "favorable":
        return (
            "Sur 26 ans, la synchronisation spatiale (indice de Moran) suit une tendance significative sur "
            "le réseau réel des départements, mais pas sur la grille de contrôle avec les mêmes valeurs -- "
            "cohérent avec H2 : la topologie réelle change le comportement du test."
        )
    if outcome == "against":
        return (
            "La grille de contrôle montre une tendance significative mais pas le réseau réel -- ce résultat va "
            "à l'encontre de ce qu'on attendrait si la topologie réelle rendait le signal plus détectable."
        )
    if real_trend.significant_at_0_05 and grid_trend.significant_at_0_05:
        return (
            "Les deux réseaux montrent une tendance significative de l'indice de Moran sur 26 ans -- H2 "
            "n'est pas clairement démontrée par ce seul indicateur temporel ici, même si le réseau réel "
            "reste le plus économiquement interprétable."
        )
    return (
        "Ni le réseau réel ni la grille de contrôle ne montrent de tendance significative de "
        "synchronisation spatiale sur ces 26 ans -- cette série ne fournit pas de signal pour H2."
    )


@router.get("/h2", response_model=H2Response)
async def test_h2(
    n_surrogates: int = Query(default=500, ge=100, le=2000),
    n_permutations_snapshot: int = Query(default=300, ge=100, le=1000),
):
    try:
        spatial = await get_real_network_moran_series()
    except SpatialDataUnavailable as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    wide = spatial["wide"]
    codes = spatial["codes"]
    dates = spatial["dates"].strftime("%Y-%m-%d").tolist()
    i_real = spatial["i_real"]
    i_grid = spatial["i_grid"]
    w_real = spatial["w_real"]
    w_grid = spatial["w_grid"]

    real_trend = surrogate_trend_test(i_real, n_surrogates=n_surrogates, seed=100)
    grid_trend = surrogate_trend_test(i_grid, n_surrogates=n_surrogates, seed=101)

    latest_values = wide.iloc[-1].to_numpy()
    real_snapshot = permutation_test(latest_values, w_real, n_permutations=n_permutations_snapshot, seed=42)
    grid_snapshot = permutation_test(latest_values, w_grid, n_permutations=n_permutations_snapshot, seed=42)

    real_trend_out = _trend_out(real_trend)
    grid_trend_out = _trend_out(grid_trend)

    def series_out(values) -> dict:
        return {"dates": dates, "values": [None if pd.isna(v) else round(float(v), 6) for v in values]}

    return H2Response(
        n_units=len(codes),
        n_quarters=len(wide),
        period_start=dates[0],
        period_end=dates[-1],
        grid_shape=spatial["grid_shape"],
        n_edges_real_network=int(w_real.sum() / 2),
        real_network=MoranSeriesOut(
            moran_series=series_out(i_real),
            trend=real_trend_out,
            latest_snapshot=_snapshot_out(real_snapshot),
        ),
        control_grid=MoranSeriesOut(
            moran_series=series_out(i_grid),
            trend=grid_trend_out,
            latest_snapshot=_snapshot_out(grid_snapshot),
        ),
        values_latest=[
            DepartmentValueOut(code=c, name=spatial["network_names"].get(c, c), value=float(v))
            for c, v in zip(codes, latest_values)
        ],
        verdict_simple=_verdict(real_trend_out, grid_trend_out),
    )


async def _analyze_variable(key: str, n_surrogates: int) -> H2VariableResult:
    cfg = VARIABLES[key]
    wide = await get_department_wide(cfg["connector"], start_period=cfg["start_period"], rolling_12=cfg["rolling_12"])
    spatial = compute_network_moran_series(wide)
    real_trend = surrogate_trend_test(spatial["i_real"], n_surrogates=n_surrogates, seed=hash(key) % 1000)
    grid_trend = surrogate_trend_test(spatial["i_grid"], n_surrogates=n_surrogates, seed=(hash(key) + 1) % 1000)
    real_trend_out = _trend_out(real_trend)
    grid_trend_out = _trend_out(grid_trend)
    dates = spatial["dates"]
    return H2VariableResult(
        key=key,
        label=cfg["label"],
        n_periods=len(wide),
        period_start=dates[0].strftime("%Y-%m-%d"),
        period_end=dates[-1].strftime("%Y-%m-%d"),
        real_trend=real_trend_out,
        grid_trend=grid_trend_out,
        outcome=_outcome(real_trend_out.significant_at_0_05, grid_trend_out.significant_at_0_05),
    )


@router.get("/h2/aggregate", response_model=H2AggregateResponse)
async def test_h2_aggregate(n_surrogates: int = Query(default=300, ge=100, le=1000)):
    """Rejoue le test H2 (reseau reel vs grille de controle) sur 5 variables
    territoriales reelles au lieu du seul chomage -- miroir de
    /hypotheses/h1/aggregate."""
    results: list[H2VariableResult] = []
    errors: list[str] = []
    for key in VARIABLES:
        try:
            results.append(await _analyze_variable(key, n_surrogates))
        except SpatialDataUnavailable as exc:
            errors.append(f"{key} : {exc}")

    n_favorable = sum(1 for r in results if r.outcome == "favorable")
    n_against = sum(1 for r in results if r.outcome == "against")
    n_neutral = len(results) - n_favorable - n_against

    if not results:
        verdict = "Aucune des variables testées n'a pu être analysée."
    elif n_favorable > n_against and n_favorable >= len(results) / 2:
        verdict = (
            f"{n_favorable}/{len(results)} variables réelles montrent une tendance significative sur le "
            "réseau réel mais pas sur la grille de contrôle -- majorité favorable à H2."
        )
    elif n_against > n_favorable and n_against >= len(results) / 2:
        verdict = (
            f"{n_against}/{len(results)} variables réelles vont à l'encontre de H2 (grille significative, "
            "pas le réseau réel) -- majorité défavorable."
        )
    else:
        verdict = (
            f"Sur {len(results)} variables réelles testées, {n_favorable} favorables, {n_against} "
            f"défavorables, {n_neutral} non concluantes -- pas de majorité claire dans un sens ou l'autre."
        )

    return H2AggregateResponse(
        n_variables_tested=len(results),
        n_favorable=n_favorable,
        n_against=n_against,
        n_neutral=n_neutral,
        results=results,
        errors=errors,
        verdict_simple=verdict,
    )
