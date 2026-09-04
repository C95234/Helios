from __future__ import annotations

import numpy as np
from fastapi import APIRouter, HTTPException, Query

from ..schemas import H5Response, ModelComparisonOut
from ..spatial_series import SpatialDataUnavailable, get_unemployment_shock_sizes
from ..stats.power_law import bootstrap_plausibility, compare_to_alternatives, fit_power_law

router = APIRouter(prefix="/api/hypotheses", tags=["hypotheses"])

MAX_TAIL_POINTS = 500  # sous-echantillonnage pour le transport, jamais pour le calcul (fait avant)


def _verdict(plausible: bool, favors_lognormal: bool | None, favors_exponential: bool | None) -> str:
    """§5.9.2 : favorable seulement si plausible ET préférée aux DEUX modèles
    alternatifs de façon significative ; against si rejetée par le test de
    plausibilité ou battue par une alternative -- neutral sinon (ex. plausible
    mais comparaison non tranchée)."""
    if not plausible:
        return "against"
    if favors_lognormal is False or favors_exponential is False:
        return "against"
    if favors_lognormal is True and favors_exponential is True:
        return "favorable"
    return "neutral"


@router.get("/h5", response_model=H5Response)
async def test_h5(
    n_synthetic: int = Query(default=200, ge=50, le=1000),
    seed: int | None = Query(default=42),
):
    try:
        data = await get_unemployment_shock_sizes()
    except SpatialDataUnavailable as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    shocks = data["shocks"]
    try:
        fit = fit_power_law(shocks)
    except ValueError as exc:
        raise HTTPException(status_code=502, detail=f"Ajustement impossible : {exc}") from exc

    plausibility = bootstrap_plausibility(shocks, fit["alpha"], fit["xmin"], n_synthetic=n_synthetic, seed=seed)
    comparison = compare_to_alternatives(shocks, fit["xmin"], fit["alpha"])

    tail_sorted = np.sort(shocks[shocks >= fit["xmin"]])
    if len(tail_sorted) > MAX_TAIL_POINTS:
        idx = np.linspace(0, len(tail_sorted) - 1, MAX_TAIL_POINTS).astype(int)
        tail_sorted = tail_sorted[idx]

    verdict = _verdict(
        plausibility["plausible_at_0_1"],
        comparison["lognormal"]["favors_power_law"],
        comparison["exponential"]["favors_power_law"],
    )

    return H5Response(
        alpha=round(fit["alpha"], 4),
        xmin=round(fit["xmin"], 4),
        ks_statistic=round(fit["ks_statistic"], 4),
        n_tail=fit["n_tail"],
        n_total=fit["n_total"],
        n_departments=data["n_departments"],
        n_quarters=data["n_quarters"],
        period_start=data["period_start"],
        period_end=data["period_end"],
        p_plausibility=plausibility["p_value"],
        n_synthetic=n_synthetic,
        tail_values=[round(float(v), 4) for v in tail_sorted],
        lognormal=ModelComparisonOut(**comparison["lognormal"]),
        exponential=ModelComparisonOut(**comparison["exponential"]),
        verdict=verdict,
    )
