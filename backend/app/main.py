from __future__ import annotations

import logging
import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from .routers import analyze, connectors, demo, h2, h3, hypotheses, series
from .settings import ALLOWED_ORIGINS, ENVIRONMENT, RATE_LIMIT

# Journalisation d'audit (qui, quand, quoi) sans jamais loguer le contenu des
# donnees -- cahier des charges §9.6.
audit_logger = logging.getLogger("helios.audit")
audit_logger.setLevel(logging.INFO)
if not audit_logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(message)s"))
    audit_logger.addHandler(handler)

limiter = Limiter(key_func=get_remote_address, default_limits=[RATE_LIMIT])

app = FastAPI(
    title="Helios API",
    description="Detection et test de signaux precurseurs de bascules collectives.",
    version="0.1.0-mvp",
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.middleware("http")
async def audit_log_middleware(request: Request, call_next):
    start = time.monotonic()
    response = await call_next(request)
    duration_ms = round((time.monotonic() - start) * 1000, 1)
    audit_logger.info(
        "%s client=%s method=%s path=%s status=%s duration_ms=%s",
        time.strftime("%Y-%m-%dT%H:%M:%S"),
        get_remote_address(request),
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response


app.include_router(demo.router)
app.include_router(series.router)
app.include_router(analyze.router)
app.include_router(hypotheses.router)
app.include_router(h2.router)
app.include_router(h3.router)
app.include_router(connectors.router)


@app.get("/api/health")
def health():
    return {"status": "ok", "environment": ENVIRONMENT}
