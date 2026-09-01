"""Configuration par environnement -- cahier des charges §9.9 (separation dev/staging/prod).

Tout vient de variables d'environnement, avec des valeurs par defaut qui
reproduisent le comportement de developpement local actuel (aucun .env
requis pour continuer a lancer `uvicorn app.main:app` comme avant).
"""
from __future__ import annotations

import os

ENVIRONMENT = os.environ.get("HELIOS_ENV", "development")

_default_origins = "http://localhost:5173,http://127.0.0.1:5173"
ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.environ.get("HELIOS_ALLOWED_ORIGINS", _default_origins).split(",")
    if origin.strip()
]

RATE_LIMIT = os.environ.get("HELIOS_RATE_LIMIT", "100/minute")
