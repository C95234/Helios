from __future__ import annotations

import pandas as pd
from fastapi import APIRouter, HTTPException, Query

from ..connectors.insee import InseeBdmConnector
from ..phenomena import PHENOMENA
from ..schemas import H3Response, HistoricalPointOut
from ..spatial_series import SpatialDataUnavailable, get_real_network_moran_series
from ..stats.h3_joint import joint_test, national_tau_per_window_end
from ..stats.indicators import kendall_trend, rolling_variance

router = APIRouter(prefix="/api/hypotheses", tags=["hypotheses"])

_insee = InseeBdmConnector()

# Serie nationale la plus longue disponible (couvre 2000-2026, coherente avec H2) --
# on reste sur une serie deja verifiee dans la batterie H1, pas une nouvelle source.
NATIONAL_IDBANK = "001587668"  # Confiance des menages (indice composite)


def _verdict(result: dict, n_historical: int) -> str:
    p_joint = result["p_joint"]
    if p_joint is None:
        return "Pas assez d'historique comparable pour calibrer un verdict sur cette période."
    if p_joint < 0.05:
        return (
            f"Sur cette période, la combinaison du signal temporel national et du signal spatial "
            f"départemental est plus inhabituelle que {round((1 - p_joint) * 100)}% des {n_historical} "
            f"trimestres comparables des 26 dernières années -- cohérent avec H3 sur ce cas isolé."
        )
    return (
        f"Sur cette période, la combinaison des deux signaux n'est pas plus inhabituelle que la "
        f"plupart des {n_historical} trimestres comparables de l'historique -- H3 n'est pas soutenue "
        "par ce cas."
    )


@router.get("/h3", response_model=H3Response)
async def test_h3(
    phenomenon: str,
    insee_window: int = Query(default=4, ge=4, le=12),
):
    if phenomenon not in PHENOMENA:
        raise HTTPException(status_code=404, detail=f"Phénomène inconnu : {phenomenon}")
    spec = PHENOMENA[phenomenon]
    start, end = pd.Timestamp(spec["start"]), pd.Timestamp(spec["end"])
    window_months = max(4, round((end - start).days / 30.44))

    try:
        spatial = await get_real_network_moran_series()
    except SpatialDataUnavailable as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    try:
        raw = await _insee.fetch(idbank=NATIONAL_IDBANK, start_period="2000-01")
        national_df = _insee.normalize(raw)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Connecteur INSEE (série nationale) indisponible : {exc}") from exc

    national_series = national_df.set_index("date")["valeur"]
    quarterly_dates = spatial["dates"]
    i_real = pd.Series(spatial["i_real"], index=quarterly_dates)

    historical_national_tau = national_tau_per_window_end(national_series, quarterly_dates, window_months, insee_window)

    # Trimestre spatial le plus proche de la fin du phenomene.
    nearest_idx = quarterly_dates.get_indexer([end], method="nearest")[0]
    nearest_quarter = quarterly_dates[nearest_idx]
    observed_spatial_i = float(i_real.iloc[nearest_idx]) if not pd.isna(i_real.iloc[nearest_idx]) else None

    observed_window = national_series[national_series.index <= end].tail(window_months)
    observed_national_tau = None
    if len(observed_window) >= window_months and len(observed_window) >= insee_window + 4:
        variance_series = rolling_variance(observed_window, insee_window)
        tau, n_points = kendall_trend(variance_series)
        if n_points >= 4 and tau == tau:  # pas NaN
            observed_national_tau = float(tau)

    if observed_national_tau is None or observed_spatial_i is None:
        raise HTTPException(
            status_code=422,
            detail="Pas assez de points pour calculer les deux composantes (temporelle et spatiale) sur cette période.",
        )

    result = joint_test(
        observed_national_tau,
        observed_spatial_i,
        historical_national_tau,
        i_real,
        exclude_dates=(start, end),
    )

    aligned = pd.DataFrame({"national_tau": historical_national_tau, "spatial_i": i_real}).dropna()
    historical_points = [
        HistoricalPointOut(date=d.strftime("%Y-%m-%d"), national_tau=float(row["national_tau"]), spatial_i=float(row["spatial_i"]))
        for d, row in aligned.iterrows()
    ]

    p_joint = result["p_joint"]
    return H3Response(
        phenomenon_label=spec["label"],
        phenomenon_description=spec["description"],
        window_months=window_months,
        observed_national_tau=observed_national_tau,
        observed_spatial_i=observed_spatial_i,
        nearest_spatial_quarter=nearest_quarter.strftime("%Y-%m-%d"),
        p_temporal_rank=result["p_temporal_rank"],
        p_spatial_rank=result["p_spatial_rank"],
        t_observed=result["t_observed"],
        p_joint=p_joint,
        n_historical_windows=result["n_historical_windows"],
        significant_at_0_05=bool(p_joint is not None and p_joint < 0.05),
        historical_points=historical_points,
        verdict_simple=_verdict(result, result["n_historical_windows"]),
    )
