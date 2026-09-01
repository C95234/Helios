from __future__ import annotations

from fastapi import APIRouter, Query

from ..demo_simulation import build_demo_payload
from ..schemas import DemoResponse

router = APIRouter(prefix="/api/demo", tags=["demo"])


@router.get("/simulated", response_model=DemoResponse)
def get_simulated_demo(seed: int = Query(default=42, ge=0, le=1_000_000)):
    return build_demo_payload(seed=seed)
