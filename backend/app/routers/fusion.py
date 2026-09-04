"""Second domaine d'application -- detection sur donnees de tokamak (MAST) --
cahier des charges Helios §7ter.

Reutilise EXACTEMENT le meme moteur de calcul que H1 (variance/AC1 +
surrogate_test) et H2 (indice de Moran + surrogate_trend_test), sans
branche specifique -- seuls les connecteurs de donnees changent (§7ter,
critere d'acceptation : "un seul moteur de calcul, deux jeux de
connecteurs"). Detection uniquement : ce module ne simule, ne concoit ni
ne propose aucun systeme de controle reel de plasma (voir
`scope_disclaimer` dans schemas.py).
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from fastapi import APIRouter, HTTPException, Query

from ..connectors.mast import MastDataUnavailable, fetch_shot_metadata, fetch_signal
from ..geo import knn_weight_matrix
from ..schemas import FusionAggregateResponse, FusionShotResult, SignificanceOut, TrendTestOut
from ..stats.moran import morans_i
from ..stats.quench import detect_quench
from ..stats.surrogates import surrogate_test, surrogate_trend_test

router = APIRouter(prefix="/api/hypotheses", tags=["hypotheses"])

CURATED_SHOTS_PATH = Path(__file__).resolve().parent.parent / "data" / "mast_shots.json"
CURRENT_WINDOW_SAMPLES = 50  # ~25ms a ~2kHz (amc/plasma_current) -- resolution courte adaptee a l'echelle du phenomene, comme les fenetres H1 sont adaptees a leur echelle mensuelle
MAX_ANALYSIS_POINTS = 400  # amc/plasma_current a ~2kHz donne des milliers de points par tir -- rolling_ac1 (une acf() par position de fenetre) x n_surrogates deviendrait ingerable ; on retient les MAX_ANALYSIS_POINTS derniers points avant la coupure (les plus proches du quench, les plus pertinents pour un signal precurseur), pas toute la duree du tir
N_PROBE_NEIGHBORS = 5


def _load_curated_shots() -> list[dict]:
    if not CURATED_SHOTS_PATH.exists():
        raise HTTPException(
            status_code=502,
            detail="Liste de tirs MAST curatee non disponible (backend/scripts/curate_mast_shots.py non execute).",
        )
    return json.loads(CURATED_SHOTS_PATH.read_text(encoding="utf-8"))["shots"]


def _fetch_current_signal(shot_id: int) -> tuple[np.ndarray, np.ndarray]:
    """`amc/plasma_current` (mesure magnetique brute) prefere a
    `efm/plasma_current_x` (reconstruction EFIT, qui echoue souvent au
    moment meme d'une disruption) -- repli si le premier manque."""
    try:
        return fetch_signal(shot_id, "amc", "time"), fetch_signal(shot_id, "amc", "plasma_current")
    except MastDataUnavailable:
        return fetch_signal(shot_id, "efm", "time"), fetch_signal(shot_id, "efm", "plasma_current_x")


def _verdict(disrupted: bool, precursor: bool, has_temporal: bool, has_spatial: bool) -> str:
    if not disrupted:
        return "Tir stable (pas de quench détecté) : " + (
            "un signal a tort été jugé significatif sur cette fenêtre de contrôle -- faux positif à noter."
            if precursor
            else "aucun signal temporel ni spatial significatif, comme attendu pour un cas de contrôle."
        )
    signals = []
    if has_temporal:
        signals.append("temporel (variance/AC1 du courant)")
    if has_spatial:
        signals.append("spatial (indice de Moran, sondes magnétiques)")
    if signals:
        return f"Tir disrupté : signal précurseur {' et '.join(signals)} significatif avant le quench."
    return "Tir disrupté : aucun signal précurseur (temporel ou spatial) significatif avant le quench sur ce tir."


async def _analyze_shot(shot_id: int, n_surrogates: int) -> FusionShotResult:
    try:
        metadata = await fetch_shot_metadata(shot_id)
    except MastDataUnavailable as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    try:
        time, current = _fetch_current_signal(shot_id)
    except MastDataUnavailable as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    quench = detect_quench(time, current)
    clean_time, clean_current = quench["time"], quench["current"]
    if quench["t_peak"] is None:
        raise HTTPException(status_code=422, detail=f"Tir {shot_id} : pas de vrai courant plasma détecté.")

    cutoff = quench["t_quench"] if quench["disrupted"] else float(clean_time[-1])
    pre_mask = clean_time < cutoff
    pre_current = pd.Series(clean_current[pre_mask])
    if len(pre_current) > MAX_ANALYSIS_POINTS:
        pre_current = pre_current.iloc[-MAX_ANALYSIS_POINTS:].reset_index(drop=True)

    if len(pre_current) < CURRENT_WINDOW_SAMPLES + 4:
        raise HTTPException(status_code=422, detail=f"Tir {shot_id} : fenêtre pré-quench trop courte pour l'analyse temporelle.")

    variance_sig = surrogate_test(pre_current, CURRENT_WINDOW_SAMPLES, "variance", n_surrogates=n_surrogates, seed=shot_id)
    ac1_sig = surrogate_test(pre_current, CURRENT_WINDOW_SAMPLES, "ac1", n_surrogates=n_surrogates, seed=shot_id + 1)

    try:
        magpr_r = fetch_signal(shot_id, "efm", "magpr_r")
        magpr_z = fetch_signal(shot_id, "efm", "magpr_z")
        magpr_c = fetch_signal(shot_id, "efm", "magpr_c")
        efm_time = fetch_signal(shot_id, "efm", "time")
    except MastDataUnavailable as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    weights = knn_weight_matrix(magpr_r, magpr_z, k=N_PROBE_NEIGHBORS)
    efm_pre_mask = np.isfinite(efm_time) & (efm_time < cutoff)
    moran_series = np.array(
        [
            morans_i(magpr_c[i, :], weights)
            for i in range(len(efm_time))
            if efm_pre_mask[i] and np.all(np.isfinite(magpr_c[i, :]))
        ]
    )
    moran_trend = surrogate_trend_test(moran_series, n_surrogates=n_surrogates, seed=shot_id + 2)

    has_temporal = bool(variance_sig["significant_at_0_05"] or ac1_sig["significant_at_0_05"])
    has_spatial = bool(moran_trend["significant_at_0_05"])
    precursor = has_temporal or has_spatial

    return FusionShotResult(
        shot_id=shot_id,
        campaign=metadata.get("campaign"),
        disrupted=quench["disrupted"],
        t_quench=quench["t_quench"],
        t_peak=quench["t_peak"],
        peak_current_ka=quench["peak_current"],
        n_current_points_analyzed=len(pre_current),
        variance_significance=SignificanceOut(**variance_sig),
        ac1_significance=SignificanceOut(**ac1_sig),
        n_probes=len(magpr_r),
        moran_trend=TrendTestOut(**moran_trend),
        precursor_before_quench=precursor,
        verdict_simple=_verdict(quench["disrupted"], precursor, has_temporal, has_spatial),
    )


@router.get("/fusion", response_model=FusionShotResult)
async def test_fusion_shot(
    shot_id: int = Query(...),
    n_surrogates: int = Query(default=200, ge=50, le=1000),
):
    return await _analyze_shot(shot_id, n_surrogates)


@router.get("/fusion/aggregate", response_model=FusionAggregateResponse)
async def test_fusion_aggregate(n_surrogates: int = Query(default=50, ge=50, le=500)):
    """Lance la batterie de tirs curatés -- miroir de /hypotheses/h1/aggregate."""
    shots_meta = _load_curated_shots()
    results: list[FusionShotResult] = []
    for entry in shots_meta:
        try:
            results.append(await _analyze_shot(entry["shot_id"], n_surrogates))
        except HTTPException:
            continue

    if not results:
        raise HTTPException(status_code=502, detail="Aucun tir de la batterie curatée n'a pu être analysé.")

    n_disrupted = sum(1 for r in results if r.disrupted)
    n_stable = len(results) - n_disrupted
    n_disrupted_with_precursor = sum(1 for r in results if r.disrupted and r.precursor_before_quench)
    n_stable_false_positive = sum(1 for r in results if not r.disrupted and r.precursor_before_quench)

    verdict = (
        f"{n_disrupted_with_precursor}/{n_disrupted} tirs disruptés montrent un signal précurseur "
        f"(temporel ou spatial) avant le quench, sur {len(results)} tirs analysés. Mais {n_stable_false_positive}/"
        f"{n_stable} tirs stables (cas de contrôle) montrent aussi un signal jugé significatif -- un faux "
        "positif à ne pas passer sous silence, pas seulement un résultat favorable à retenir."
        if n_disrupted > 0
        else "Aucun tir disrupté dans la batterie curatée -- pas de comparaison possible."
    )

    return FusionAggregateResponse(
        n_shots=len(results),
        n_disrupted=n_disrupted,
        n_stable=n_stable,
        n_disrupted_with_precursor=n_disrupted_with_precursor,
        n_stable_false_positive=n_stable_false_positive,
        shots=results,
        verdict_simple=verdict,
    )
