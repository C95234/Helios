"""Connecteur MAST (Mega Ampere Spherical Tokamak) -- cahier des charges
Helios §7ter, second domaine d'application (detection sur donnees de
fusion).

Verifie en direct (pas suppose) avant d'ecrire ce module :
- L'API REST (https://mastapp.site/json/...) est ouverte, sans identifiants
  -- metadata uniquement (aucun champ "disruption" structure).
- Les signaux bruts sont sur S3 au format Zarr v2
  (s3://mast/level1/shots/{id}.zarr/...), accessibles ANONYMEMENT en HTTPS
  pur (pas besoin de s3fs/boto3/identifiants) via
  https://s3.echo.stfc.ac.uk/mast/level1/shots/{id}.zarr/{groupe}/{nom}.
- `amc/plasma_current` (mesure magnetique brute, kA) est prefere a
  `efm/plasma_current_x` (reconstruction EFIT, qui echoue souvent au
  moment meme d'une disruption) pour la detection de quench.
- `efm/magpr_r`/`efm/magpr_z` (positions R,Z des sondes magnetiques, m) et
  `efm/magpr_c` (lecture, [temps, sonde], T) donnent un reseau spatial reel
  de capteurs -- l'equivalent tokamak du reseau des departements pour H2.

DisruptionBench (§6/§7ter du cahier des charges) n'est PAS "public" comme
indique : DIII-D, EAST et Alcator C-Mod exigent des identifiants
institutionnels (verifie via la documentation de DisruptionPy) -- ce
connecteur n'y accede donc pas. La verite terrain de disruption est
derivee des donnees MAST elles-memes (voir stats/quench.py), decision
utilisateur explicite plutot qu'une etiquette externe a faire confiance.
"""
from __future__ import annotations

import fsspec
import httpx
import numpy as np
import zarr

REST_BASE_URL = "https://mastapp.site/json"
S3_BASE_URL = "https://s3.echo.stfc.ac.uk/mast/level1/shots"


class MastDataUnavailable(Exception):
    pass


async def fetch_shot_metadata(shot_id: int) -> dict:
    async with httpx.AsyncClient(timeout=20.0) as client:
        try:
            response = await client.get(f"{REST_BASE_URL}/shots", params={"filters": f"shot_id$eq:{shot_id}"})
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise MastDataUnavailable(f"API MAST (metadata) indisponible pour le tir {shot_id} : {exc}") from exc
    items = response.json().get("items", [])
    if not items:
        raise MastDataUnavailable(f"Tir {shot_id} introuvable dans le catalogue MAST.")
    return items[0]


def fetch_signal(shot_id: int, group: str, name: str) -> np.ndarray:
    """Lit un signal (numerique, 1D ou 2D) directement depuis le magasin Zarr
    public sur S3, en HTTPS anonyme -- pas de tentative de repli silencieux :
    toute erreur reseau ou signal absent leve MastDataUnavailable, a charge
    de l'appelant de savoir s'il existe un signal de repli (ex.
    efm/plasma_current_x si amc/plasma_current manque pour ce tir)."""
    url = f"{S3_BASE_URL}/{shot_id}.zarr/{group}/{name}"
    try:
        store = fsspec.get_mapper(url)
        array = zarr.open(store, mode="r")
        return np.asarray(array[:])
    except Exception as exc:
        raise MastDataUnavailable(f"Signal {group}/{name} indisponible pour le tir {shot_id} : {exc}") from exc
