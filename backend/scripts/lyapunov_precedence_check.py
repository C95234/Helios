"""Rejoue la validation Monte-Carlo de precedence variance/Moran (§5.6quater
et §5.6quinquies) sur l'anneau (reproduction / test de non-regression) puis
sur le reseau reel des departements francais (§7bis, "instructions pour la
suite", points 1-2).

Calcul lourd (Monte-Carlo, 40 realisations x 2 regimes de couplage x 2
reseaux) -- script hors-ligne, pas un endpoint produit. Sortie : rapport
JSON dans app/data/journal_precedence_results.json, integre manuellement
dans le contenu du Journal de recherche (frontend/src/data/journal.js)
apres relecture, dans le meme esprit que le reste du §7bis (contenu
verifie puis fige, pas recalcule a chaque visite).

Usage : python scripts/lyapunov_precedence_check.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.geo import department_weight_matrix, load_department_network  # noqa: E402
from app.lyapunov_precedence import random_irregular_weights, ring_weights, run_precedence_batch  # noqa: E402

OUTPUT_PATH = Path(__file__).resolve().parent.parent / "app" / "data" / "journal_precedence_results.json"

N_REPS_RING = 40  # deja calibre/valide -- ~9 min pour les 2 regimes de couplage
N_REPS_IRREGULAR = 20
N_REPS_REAL = 20  # reseau reel = 96 noeuds (~5.8x plus lent par pas que N=40) -- reduit pour rester dans un temps raisonnable
SEED0 = 1000


def summarize(result: dict) -> dict:
    return {
        "coupling": result["coupling"],
        "n_reps": result["n_reps"],
        "n_tipped": result["n_tipped"],
        "n_precedence": result["n_precedence"],
        "n_valid": result["n_valid"],
        "precedence_rate": round(result["precedence_rate"], 4) if result["precedence_rate"] is not None else None,
        "advance_var": round(result["advance_var"], 1) if result["advance_var"] is not None else None,
        "advance_moran": round(result["advance_moran"], 1) if result["advance_moran"] is not None else None,
    }


def main():
    report = {}

    print("=== Reproduction sur anneau (N=40) -- §5.6quater/quinquies ===")
    W_ring = ring_weights(40)
    for coupling in ["diffusive", "contagion"]:
        res = run_precedence_batch(W_ring, coupling, n_reps=N_REPS_RING, seed0=SEED0)
        print(summarize(res))
        report[f"ring_{coupling}"] = summarize(res)

    print("\n=== Reseau irregulier aleatoire (N=40, une instance) -- §5.6ter ===")
    W_irr = random_irregular_weights(40, seed=7)
    res = run_precedence_batch(W_irr, "diffusive", n_reps=N_REPS_IRREGULAR, seed0=SEED0)
    print(summarize(res))
    report["irregular_diffusive"] = summarize(res)

    print("\n=== Reseau reel des departements francais (§7bis, instruction 1-2) ===")
    network = load_department_network()
    codes = list(network["adjacency"].keys())
    W_real = department_weight_matrix(codes, network["adjacency"])
    print(f"N = {len(codes)} departements, {int(W_real.sum() / 2)} paires de voisins")
    for coupling in ["diffusive", "contagion"]:
        res = run_precedence_batch(W_real, coupling, n_reps=N_REPS_REAL, seed0=SEED0, beta=0.6)
        print(summarize(res))
        report[f"real_network_{coupling}"] = summarize(res)

    report["n_departments"] = len(codes)
    OUTPUT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nRapport ecrit dans {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
