from __future__ import annotations

import numpy as np
from fastapi import APIRouter, Query

from ..kuramoto import critical_coupling, simulate_adaptive_control, simulate_uncontrolled
from ..schemas import H4Response, KuramotoTraceOut

router = APIRouter(prefix="/api/hypotheses", tags=["hypotheses"])

MAX_POINTS = 600  # sous-echantillonnage pour le transport / l'affichage, jamais pour le calcul


def _downsample(time: np.ndarray, values: np.ndarray) -> KuramotoTraceOut:
    n = len(time)
    if n <= MAX_POINTS:
        idx = np.arange(n)
    else:
        idx = np.linspace(0, n - 1, MAX_POINTS).astype(int)
        idx[-1] = n - 1
    return KuramotoTraceOut(time=[round(float(t), 4) for t in time[idx]], values=[round(float(v), 4) for v in values[idx]])


@router.get("/h4", response_model=H4Response)
def simulate_h4(
    n_oscillators: int = Query(default=40, ge=10, le=100),
    coupling_k: float = Query(default=3.0, gt=0, le=20),
    r_threshold: float = Query(default=0.5, gt=0, lt=1),
    beta: float = Query(default=2.0, gt=0, le=20),
    duration: float = Query(default=30.0, gt=1, le=100),
    dt: float = Query(default=0.02, gt=0.001, le=0.1),
    seed: int | None = Query(default=None),
):
    k_c = critical_coupling(sigma=1.0)

    uncontrolled = simulate_uncontrolled(n=n_oscillators, k=coupling_k, duration=duration, dt=dt, seed=seed)
    controlled = simulate_adaptive_control(
        n=n_oscillators,
        k_base=coupling_k,
        r_target=r_threshold,
        beta=beta,
        duration=duration,
        dt=dt,
        seed=seed,
    )

    time = np.arange(len(uncontrolled["r"])) * dt
    r_unc, r_ctl = uncontrolled["r"], controlled["r"]

    tail = max(1, len(r_unc) // 5)  # dernier cinquieme de la simulation = regime "stationnaire"

    return H4Response(
        n_oscillators=n_oscillators,
        coupling_k=coupling_k,
        critical_coupling=round(k_c, 4),
        r_threshold=r_threshold,
        beta=beta,
        duration=duration,
        dt=dt,
        seed=seed,
        r_uncontrolled=_downsample(time, r_unc),
        r_controlled=_downsample(time, r_ctl),
        mean_coupling_controlled=_downsample(time, controlled["mean_k"]),
        r_mean_uncontrolled=round(float(np.mean(r_unc[-tail:])), 4),
        r_mean_controlled=round(float(np.mean(r_ctl[-tail:])), 4),
        r_final_uncontrolled=round(float(r_unc[-1]), 4),
        r_final_controlled=round(float(r_ctl[-1]), 4),
    )
