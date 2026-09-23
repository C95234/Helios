"""Audit de robustesse (cahier des charges §3, suite ewstools) -- reseau
reel des departements francais, a un nombre de graines nettement plus
eleve que le run original (20 -> 200), pour verifier si le taux de
precedence rapporte (75%) est stable ou sensible a l'echantillon de
graines utilise.

Sortie : JSON dans app/data/robustness_audit_real_network.json
"""
from __future__ import annotations

import asyncio
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.geo import department_weight_matrix, load_department_network  # noqa: E402
from app.lyapunov_precedence import run_precedence_batch  # noqa: E402

OUTPUT_PATH = Path(__file__).resolve().parent.parent / "app" / "data" / "robustness_audit_real_network.json"

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


async def _load_network():
    result = load_department_network()
    if asyncio.iscoroutine(result):
        return await result
    return result


def main():
    report = {"n_reps": N_REPS, "seed0": SEED0}
    t0 = time.time()

    network = asyncio.run(_load_network())
    codes = list(network["adjacency"].keys())
    W_real = department_weight_matrix(codes, network["adjacency"])
    report["n_departments"] = len(codes)
    print(f"N = {len(codes)} departements", flush=True)

    for coupling in ["diffusive", "contagion"]:
        res = run_precedence_batch(W_real, coupling, n_reps=N_REPS, seed0=SEED0, beta=0.6)
        print(summarize(res), flush=True)
        report[f"real_network_{coupling}"] = summarize(res)

    report["elapsed_seconds"] = round(time.time() - t0, 1)
    OUTPUT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Done in {report['elapsed_seconds']}s, written to {OUTPUT_PATH}", flush=True)


if __name__ == "__main__":
    main()
