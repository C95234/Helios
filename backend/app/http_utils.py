"""Requetes HTTP avec re-essai : 429 (limitation de debit), 502/503/504 et erreurs reseau transitoires.

Necessaire des que plusieurs connecteurs (vues + editions Wikipedia, sur plusieurs articles et plusieurs phenomenes) sont appeles en
sequence rapide, et pour l'Insee depuis les serveurs GitHub : le 28 octobre 2026, une partie des nouvelles connexions vers
bdm.insee.fr echouait au hasard a la negociation TLS (≈ 30 s puis `ConnectError('')`), alors que d'autres passaient en moins d'une
seconde (diagnostic : workflow diagnostic-insee.yml). Une nouvelle tentative suffit en general.
"""
from __future__ import annotations

import asyncio

import httpx

#: erreurs reseau transitoires : on re-essaie avec attente croissante
ERREURS_TRANSITOIRES = (httpx.ConnectError, httpx.ConnectTimeout, httpx.ReadTimeout, httpx.RemoteProtocolError, httpx.ReadError)
STATUTS_TRANSITOIRES = (429, 502, 503, 504)


async def get_with_retry(
    client: httpx.AsyncClient,
    url: str,
    params: dict | None = None,
    max_retries: int = 5,
    base_delay: float = 1.0,
) -> httpx.Response:
    for attempt in range(max_retries + 1):
        try:
            response = await client.get(url, params=params)
        except ERREURS_TRANSITOIRES:
            if attempt == max_retries:
                raise
            await asyncio.sleep(base_delay * (2**attempt))
            continue

        if response.status_code not in STATUTS_TRANSITOIRES:
            response.raise_for_status()
            return response

        if attempt == max_retries:
            response.raise_for_status()  # leve HTTPStatusError sur le dernier essai

        retry_after = response.headers.get("Retry-After")
        delay = float(retry_after) if retry_after and retry_after.isdigit() else base_delay * (2**attempt)
        await asyncio.sleep(delay)

    raise AssertionError("unreachable")
