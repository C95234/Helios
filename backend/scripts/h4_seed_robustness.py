"""Verifie la robustesse du resultat H4 (8/8 configurations sous le seuil)
sur plusieurs graines aleatoires, plutot que sur la graine unique utilisee
pour figer H4_CONFIGS dans bilanPublie.js.

H4 est une simulation pure (Kuramoto, aucune donnee externe) : elle n'entre
pas dans le rafraichissement automatique (refresh_results.py) puisqu'il n'y
a rien a rafraichir dans le temps. Ce script est une verification ponctuelle
de robustesse, pas un job planifie -- a relancer a la main si le modele
kuramoto.py change.

Usage : python -m scripts.h4_seed_robustness (depuis backend/)
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np

from app.kuramoto import critical_coupling, simulate_adaptive_control, simulate_uncontrolled

R_THRESHOLD = 0.5
DURATION = 30.0
DT = 0.02
N_SEEDS = 30

CONFIGS = [
    {"name": "K=2K_c, beta=2 (reference)", "n": 40, "k_over_kc": 2.0, "beta": 2.0},
    {"name": "K=3K_c, beta=2", "n": 40, "k_over_kc": 3.0, "beta": 2.0},
    {"name": "K=5K_c, beta=2 (couplage fort)", "n": 40, "k_over_kc": 5.0, "beta": 2.0},
    {"name": "K=3K_c, beta=0.5 (controle faible)", "n": 40, "k_over_kc": 3.0, "beta": 0.5},
    {"name": "K=3K_c, beta=1", "n": 40, "k_over_kc": 3.0, "beta": 1.0},
    {"name": "K=3K_c, beta=4 (controle fort)", "n": 40, "k_over_kc": 3.0, "beta": 4.0},
    {"name": "Petit reseau", "n": 15, "k_over_kc": 3.0, "beta": 2.0},
    {"name": "Grand reseau", "n": 80, "k_over_kc": 3.0, "beta": 2.0},
]


def _run_one(n: int, k: float, beta: float, seed: int) -> tuple[float, float]:
    uncontrolled = simulate_uncontrolled(n=n, k=k, duration=DURATION, dt=DT, seed=seed)
    controlled = simulate_adaptive_control(
        n=n, k_base=k, r_target=R_THRESHOLD, beta=beta, duration=DURATION, dt=DT, seed=seed
    )
    tail = max(1, len(controlled["r"]) // 5)
    r_controlled_mean = float(np.mean(controlled["r"][-tail:]))
    r_uncontrolled_mean = float(np.mean(uncontrolled["r"][-tail:]))
    return r_controlled_mean, r_uncontrolled_mean


def main() -> None:
    k_c = critical_coupling(sigma=1.0)
    print(f"K_c = {k_c:.4f} -- {N_SEEDS} graines par configuration (0..{N_SEEDS - 1})\n")

    overall_failures = 0
    for cfg in CONFIGS:
        k = cfg["k_over_kc"] * k_c
        r_controlled_values = []
        for seed in range(N_SEEDS):
            r_controlled, _ = _run_one(cfg["n"], k, cfg["beta"], seed)
            r_controlled_values.append(r_controlled)

        n_under = sum(1 for r in r_controlled_values if r < R_THRESHOLD)
        overall_failures += N_SEEDS - n_under
        print(
            f"{cfg['name']:<38} {n_under:>2}/{N_SEEDS} sous le seuil "
            f"-- r_controlled in [{min(r_controlled_values):.3f}, {max(r_controlled_values):.3f}], "
            f"moyenne {np.mean(r_controlled_values):.3f}"
        )

    total = N_SEEDS * len(CONFIGS)
    print(f"\nTotal : {total - overall_failures}/{total} graines x configurations sous le seuil.")


if __name__ == "__main__":
    main()
