"""Curation d'une petite batterie de tirs MAST reels, verifiee en direct --
cahier des charges Helios §7ter (meme esprit que `phenomena.py` pour H1 :
"verifie en direct", pas devine).

Pour chaque tir candidat : verifie la presence de amc/plasma_current (ou
repli efm/plasma_current_x) ET efm/magpr_r/z/c, applique detect_quench,
et ne garde que les tirs ou les DEUX signaux sont exploitables. Fige le
resultat dans backend/app/data/mast_shots.json.

Usage : python -m scripts.curate_mast_shots (depuis backend/, avec le
venv active -- fait de vrais appels reseau, pas execute par la suite de
tests).
"""
from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import httpx

from app.connectors.mast import MastDataUnavailable, fetch_shot_metadata, fetch_signal
from app.routers.fusion import _fetch_current_signal
from app.stats.quench import detect_quench

OUTPUT_PATH = Path(__file__).resolve().parent.parent / "app" / "data" / "mast_shots.json"
CAMPAIGNS = ["M9", "M8", "M7", "M6", "M5"]
PAGE_SIZE = 80
CANDIDATES_PER_CAMPAIGN = 30  # sous-echantillonnes sur toute la page, pas seulement les premiers tirs (souvent calibration/setup)
TARGET_DISRUPTED = 4
TARGET_STABLE = 3


async def _list_shot_ids(campaign: str, page_size: int, n_candidates: int) -> list[int]:
    async with httpx.AsyncClient(timeout=20.0) as client:
        response = await client.get(
            "https://mastapp.site/json/shots",
            params={"filters": f"campaign$eq:{campaign}", "size": page_size},
        )
        response.raise_for_status()
    all_ids = [item["shot_id"] for item in response.json().get("items", [])]
    if len(all_ids) <= n_candidates:
        return all_ids
    idx = [round(i * (len(all_ids) - 1) / (n_candidates - 1)) for i in range(n_candidates)]
    return sorted({all_ids[i] for i in idx})


def _check_and_classify(shot_id: int) -> dict | None:
    try:
        time, current = _fetch_current_signal(shot_id)
    except MastDataUnavailable as exc:
        print(f"  {shot_id}: courant indisponible ({exc})")
        return None

    quench = detect_quench(time, current)
    if quench["t_peak"] is None:
        print(f"  {shot_id}: pas de vrai plasma courant")
        return None

    try:
        magpr_r = fetch_signal(shot_id, "efm", "magpr_r")
        fetch_signal(shot_id, "efm", "magpr_z")
        fetch_signal(shot_id, "efm", "magpr_c")
    except MastDataUnavailable as exc:
        print(f"  {shot_id}: sondes magnetiques indisponibles ({exc})")
        return None

    cutoff = quench["t_quench"] if quench["disrupted"] else float(quench["time"][-1])
    n_pre = int((quench["time"] < cutoff).sum())
    if n_pre < 60:
        print(f"  {shot_id}: fenetre pre-quench trop courte ({n_pre} points)")
        return None

    print(f"  {shot_id}: OK -- disrupted={quench['disrupted']} peak={quench['peak_current']:.0f}kA n_probes={len(magpr_r)}")
    return {
        "shot_id": shot_id,
        "disrupted": quench["disrupted"],
        "peak_current_ka": round(quench["peak_current"], 1),
        "t_quench": quench["t_quench"],
    }


async def main() -> None:
    disrupted: list[dict] = []
    stable: list[dict] = []

    for campaign in CAMPAIGNS:
        if len(disrupted) >= TARGET_DISRUPTED and len(stable) >= TARGET_STABLE:
            break
        print(f"Campagne {campaign}...")
        try:
            shot_ids = await _list_shot_ids(campaign, PAGE_SIZE, CANDIDATES_PER_CAMPAIGN)
        except Exception as exc:
            print(f"  liste indisponible pour {campaign} : {exc}")
            continue

        for shot_id in shot_ids:
            if len(disrupted) >= TARGET_DISRUPTED and len(stable) >= TARGET_STABLE:
                break
            result = _check_and_classify(shot_id)
            if result is None:
                continue
            try:
                metadata = await fetch_shot_metadata(shot_id)
                result["campaign"] = metadata.get("campaign")
            except MastDataUnavailable:
                result["campaign"] = campaign

            if result["disrupted"] and len(disrupted) < TARGET_DISRUPTED:
                disrupted.append(result)
            elif not result["disrupted"] and len(stable) < TARGET_STABLE:
                stable.append(result)

    shots = disrupted + stable
    print(f"\nRetenus : {len(disrupted)} disruptés, {len(stable)} stables ({len(shots)} au total).")
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps({"shots": shots, "source": "https://mastapp.site", "note": "Curation verifiee en direct, voir curate_mast_shots.py"}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"Ecrit dans {OUTPUT_PATH}")


if __name__ == "__main__":
    asyncio.run(main())
