from __future__ import annotations

import pandas as pd
from fastapi import APIRouter, HTTPException, Query

from ..schemas import (
    DepartmentValueOut,
    H2Response,
    MoranSeriesOut,
    MoranTestOut,
    TrendTestOut,
)
from ..spatial_series import SpatialDataUnavailable, get_real_network_moran_series
from ..stats.moran import permutation_test
from ..stats.surrogates import surrogate_trend_test

router = APIRouter(prefix="/api/hypotheses", tags=["hypotheses"])


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


def _verdict(real_trend: TrendTestOut, grid_trend: TrendTestOut) -> str:
    real_sig = real_trend.significant_at_0_05
    grid_sig = grid_trend.significant_at_0_05

    if real_sig and not grid_sig:
        return (
            "Sur 26 ans, la synchronisation spatiale (indice de Moran) suit une tendance significative sur "
            "le réseau réel des départements, mais pas sur la grille de contrôle avec les mêmes valeurs -- "
            "cohérent avec H2 : la topologie réelle change le comportement du test."
        )
    if real_sig and grid_sig:
        return (
            "Les deux réseaux montrent une tendance significative de l'indice de Moran sur 26 ans -- H2 "
            "n'est pas clairement démontrée par ce seul indicateur temporel ici, même si le réseau réel "
            "reste le plus économiquement interprétable."
        )
    if not real_sig and not grid_sig:
        return (
            "Ni le réseau réel ni la grille de contrôle ne montrent de tendance significative de "
            "synchronisation spatiale sur ces 26 ans -- cette série ne fournit pas de signal pour H2."
        )
    return (
        "La grille de contrôle montre une tendance significative mais pas le réseau réel -- ce résultat va "
        "à l'encontre de ce qu'on attendrait si la topologie réelle rendait le signal plus détectable."
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
