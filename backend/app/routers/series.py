from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ..connectors.insee import CURATED_SERIES, TERMS_OF_USE_URL, InseeBdmConnector
from ..schemas import SeriesCatalogEntry

router = APIRouter(prefix="/api/series/insee", tags=["series"])

_connector = InseeBdmConnector()


@router.get("/catalog", response_model=list[SeriesCatalogEntry])
def get_catalog():
    return [SeriesCatalogEntry(idbank=k, title=v) for k, v in CURATED_SERIES.items()]


@router.get("/terms-of-use")
def get_terms_of_use():
    return {"connector": "insee_bdm", "terms_of_use_url": TERMS_OF_USE_URL}


@router.get("/{idbank}")
async def get_series(idbank: str, start_period: str | None = None):
    try:
        raw = await _connector.fetch(idbank=idbank, start_period=start_period)
        df = _connector.normalize(raw)
    except Exception as exc:  # connecteur externe : toute erreur devient une 502 lisible
        raise HTTPException(status_code=502, detail=f"Connecteur INSEE indisponible : {exc}") from exc

    if df.empty:
        raise HTTPException(status_code=404, detail=f"Aucune observation pour l'idbank {idbank}")

    return {
        "idbank": idbank,
        "title": df.attrs.get("title", idbank),
        "dates": df["date"].dt.strftime("%Y-%m-%d").tolist(),
        "values": df["valeur"].tolist(),
    }
