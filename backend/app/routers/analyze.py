from __future__ import annotations

import pandas as pd
from fastapi import APIRouter, HTTPException, Query

from ..connectors.insee import InseeBdmConnector
from ..schemas import AnalysisResponse, IndicatorSeriesOut, SignificanceOut
from ..stats.indicators import rolling_ac1, rolling_variance
from ..stats.surrogates import surrogate_test

router = APIRouter(prefix="/api/analyze", tags=["analyze"])

_connector = InseeBdmConnector()


def _series_out(dates: list[str], values: pd.Series) -> IndicatorSeriesOut:
    return IndicatorSeriesOut(
        dates=dates,
        values=[None if pd.isna(v) else round(float(v), 6) for v in values],
    )


@router.get("/insee/{idbank}", response_model=AnalysisResponse)
async def analyze_insee_series(
    idbank: str,
    window: int = Query(default=12, ge=4, le=200),
    n_surrogates: int = Query(default=500, ge=50, le=2000),
    start_period: str | None = None,
):
    try:
        raw = await _connector.fetch(idbank=idbank, start_period=start_period)
        df = _connector.normalize(raw)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Connecteur INSEE indisponible : {exc}") from exc

    if df.empty:
        raise HTTPException(status_code=404, detail=f"Aucune observation pour l'idbank {idbank}")
    if len(df) < window + 4:
        raise HTTPException(
            status_code=422,
            detail=f"Serie trop courte ({len(df)} points) pour une fenetre de {window} : reduisez la fenetre.",
        )

    dates = df["date"].dt.strftime("%Y-%m-%d").tolist()
    values = df["valeur"]

    variance = rolling_variance(values, window)
    ac1 = rolling_ac1(values, window)

    variance_sig = surrogate_test(values, window, "variance", n_surrogates=n_surrogates, seed=0)
    ac1_sig = surrogate_test(values, window, "ac1", n_surrogates=n_surrogates, seed=1)

    return AnalysisResponse(
        source_title=df.attrs.get("title", idbank),
        source="insee_bdm",
        window=window,
        n_observations=len(df),
        raw=_series_out(dates, values),
        variance=_series_out(dates, variance),
        ac1=_series_out(dates, ac1),
        variance_significance=SignificanceOut(**variance_sig),
        ac1_significance=SignificanceOut(**ac1_sig),
    )
