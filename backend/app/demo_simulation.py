"""Demo pedagogique -- cahier des charges Helios §2.

Simule une serie qui traverse une bifurcation : un processus de retour a la
moyenne dont la force de rappel decroit lineairement vers zero (ralentissement
critique), suivi d'un saut brusque -- le mecanisme canonique documente dans
la litterature sur les transitions critiques (Scheffer et al., 2009 ; Dakos
et al., 2012) et repris au §5.1 du cahier des charges. Aucune donnee reelle
n'est requise : c'est une illustration, presentee comme telle.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .stats.indicators import rolling_ac1, rolling_variance


def simulate_tipping_series(
    n: int = 200,
    tipping_at: int = 150,
    lambda_start: float = 0.6,
    sigma: float = 1.0,
    jump: float = 8.0,
    seed: int | None = None,
) -> tuple[pd.Series, int]:
    rng = np.random.default_rng(seed)
    x = np.zeros(n)
    for t in range(1, n):
        progress = min(t / tipping_at, 1.0)
        lam = lambda_start * (1.0 - progress) + 0.01  # ralentissement critique
        x[t] = x[t - 1] - lam * x[t - 1] + sigma * rng.normal()
        if t == tipping_at:
            x[t] += jump
    return pd.Series(x), tipping_at


def build_demo_payload(seed: int, window: int = 20) -> dict:
    values, tipping_at = simulate_tipping_series(seed=seed)
    dates = pd.date_range("2020-01-01", periods=len(values), freq="W").strftime("%Y-%m-%d").tolist()
    variance = rolling_variance(values, window)
    ac1 = rolling_ac1(values, window)
    return {
        "seed": seed,
        "dates": dates,
        "values": values.round(4).tolist(),
        "tipping_index": tipping_at,
        "variance": {
            "dates": dates,
            "values": [None if pd.isna(v) else round(float(v), 4) for v in variance],
        },
        "ac1": {
            "dates": dates,
            "values": [None if pd.isna(v) else round(float(v), 4) for v in ac1],
        },
    }
