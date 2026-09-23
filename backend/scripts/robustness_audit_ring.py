"""Audit de robustesse (cahier des charges §3, suite ewstools) -- ring +
reseau irregulier, a un nombre de graines nettement plus eleve que le
run original (40/20 -> 200), pour verifier si le taux de precedence
rapporte est stable ou sensible a l'echantillon de graines utilise.

Sortie : JSON dans app/data/robustness_audit_ring.json
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.lyapunov_precedence import random_irregular_weights, ring_weights, run_precedence_batch  # noqa: E402

OUTPUT_PATH = Path(__file__).resolve().parent.parent / "app" / "data" / "robustness_audit_ring.json"

N_REPS = 200
SEED0 = 5000


def summarize(result: dict) -> dict:
    return {
        "coupling": result["coupling"],
        "n_reps": result["n_reps"],
        "n_tipped": result["n_tipped"],
        "n_precedence": result["n_precedence"],
        "n_valid": result["n_valid"],
        "precedence_rate": round(result["precedence_rate"], 4) if result["precedence_rate"] is not None else None,
    }


def main():
    report = {"n_reps": N_REPS, "seed0": SEED0}
    t0 = time.time()

    print("=== Ring N=40, 200 reps ===", flush=True)
    W_ring = ring_weights(40)
    for coupling in ["diffusive", "contagion"]:
        res = run_precedence_batch(W_ring, coupling, n_reps=N_REPS, seed0=SEED0)
        print(summarize(res), flush=True)
        report[f"ring_{coupling}"] = summarize(res)

    print("=== Irregular network N=40, 200 reps ===", flush=True)
    W_irr = random_irregular_weights(40, seed=7)
    res = run_precedence_batch(W_irr, "diffusive", n_reps=N_REPS, seed0=SEED0)
    print(summarize(res), flush=True)
    report["irregular_diffusive"] = summarize(res)

    report["elapsed_seconds"] = round(time.time() - t0, 1)
    OUTPUT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Done in {report['elapsed_seconds']}s, written to {OUTPUT_PATH}", flush=True)


if __name__ == "__main__":
    main()
