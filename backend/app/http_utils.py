"""Requetes HTTP avec re-essai sur 429 -- necessaire des que plusieurs connecteurs
(vues + editions Wikipedia, sur plusieurs articles et plusieurs phenomenes) sont
appeles en sequence rapide et declenchent la limitation de debit du serveur distant.
"""
from __future__ import annotations

import asyncio

import httpx


async def get_with_retry(
    client: httpx.AsyncClient,
    url: str,
    params: dict | None = None,
    max_retries: int = 5,
    base_delay: float = 1.0,
) -> httpx.Response:
    for attempt in range(max_retries + 1):
        response = await client.get(url, params=params)

        if response.status_code != 429:
            response.raise_for_status()
            return response

        if attempt == max_retries:
            response.raise_for_status()  # leve HTTPStatusError sur le dernier essai

        retry_after = response.headers.get("Retry-After")
        delay = float(retry_after) if retry_after and retry_after.isdigit() else base_delay * (2**attempt)
        await asyncio.sleep(delay)

    raise AssertionError("unreachable")
