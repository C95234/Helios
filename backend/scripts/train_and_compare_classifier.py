"""Entraine le classifieur et compare a l'indicateur statistique classique
sur un jeu de test independant -- cahier des charges "banc d'essai IA vs
statistiques : rigueur, extension, pedagogie" (§1).

Corrections §1 par rapport a la version precedente (un seul entrainement,
un detecteur classique appauvri) :
- §1.1 : le CNN est entraine sur N_SEEDS initialisations/jeux d'entrainement
  independants, chaque seed evalue sur le MEME jeu de test partage (jamais
  vu a l'entrainement) -- moyenne et ecart-type rapportes pour chaque
  metrique, jamais un chiffre unique.
- §1.2 : le detecteur "classique" utilise desormais l'indicateur complet de
  H1 (variance ET AC1 glissantes, tau de Kendall, test par donnees de
  substitution -- `classical_verdict`, ml_benchmark.py) au lieu d'un seuil
  de variance simplifie -- calcule UNE SEULE FOIS (il ne depend pas de
  l'entrainement du CNN, donc pas besoin de le refaire a chaque seed).

Calcul hors-ligne, pas un endpoint produit. Sortie : JSON dans
frontend/src/data/results/ia_vs_stats.json (memes conventions que les
autres resultats geles : refreshedAt, chiffres reels).

Usage :
    python scripts/train_and_compare_classifier.py
"""
from __future__ import annotations

import json
import sys
import time
from datetime import date
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.ml_benchmark import (  # noqa: E402
    SimpleCNN1D,
    build_dataset,
    classical_verdict,
    generate_kuramoto_ramp_series,
    generate_saddle_node_series,
    make_windows,
)

OUTPUT_PATH = (
    Path(__file__).resolve().parent.parent.parent
    / "frontend"
    / "src"
    / "data"
    / "results"
    / "ia_vs_stats.json"
)

WINDOW_LEN = 60
STRIDE = 5

# §1.1 -- multiples initialisations/entrainements independants, jamais un seul.
N_SEEDS = 5

# Adaptation Helios -- echelle reduite par rapport a la premiere version (300/150)
# pour rester tractable : le detecteur classique corrige (§1.2) coute ~11ms par
# fenetre (test par donnees de substitution, contre une comparaison a un seuil
# quasi instantanee avant), et doit balayer chaque fenetre de chaque trajectoire
# de test -- multiplie par N_SEEDS entrainements CNN, un budget de calcul non
# extensible a l'identique. Le jeu de test partage (N_TEST_*) reste neanmoins
# proche de la taille precedente et est desormais commun a tous les seeds
# (economie : le detecteur classique n'est evalue qu'UNE FOIS, pas N_SEEDS fois).
N_TRAIN_SADDLE = 50
N_TRAIN_KURAMOTO = 50
N_TEST_SADDLE = 30
N_TEST_KURAMOTO = 30
TRAIN_SEED0_BASE = 10_000
TEST_SEED0 = 90_000  # FIXE, partage entre tous les seeds CNN et le detecteur classique

CLASSICAL_N_SURROGATES = 100
CLASSICAL_SUB_WINDOW = 15

# Meme garde-fou de persistance que la version precedente (voir historique du
# fichier / commentaire original) : sans lui, une regle appliquee fraiche a
# chaque fenetre independante finit presque toujours par declencher au moins
# une fois par pur hasard, meme sur un controle negatif.
CONSECUTIVE_REQUIRED = {"saddle_node": 6, "kuramoto": 6}


def _first_sustained_flag(flags: list[bool], t_ends: list[float], consecutive_required: int) -> float | None:
    run = 0
    for i, flag in enumerate(flags):
        run = run + 1 if flag else 0
        if run >= consecutive_required:
            return t_ends[i - consecutive_required + 1]
    return None


def evaluate_trajectory_cnn(sim: dict, cnn: SimpleCNN1D) -> dict:
    windows = make_windows(sim["series"], sim["dt"], None, WINDOW_LEN, STRIDE)
    cnn_first_flag = None
    if windows:
        t_ends = [w["t_end"] for w in windows]
        X = np.stack([w["window"] for w in windows]).astype(np.float32)
        probs = cnn.predict_proba(X)
        cnn_flags = [bool(p > 0.5) for p in probs]
        cnn_first_flag = _first_sustained_flag(cnn_flags, t_ends, CONSECUTIVE_REQUIRED[sim["kind"]])
    return {"t_event": sim["t_event"], "flag": cnn_first_flag}


def evaluate_trajectory_classical(sim: dict, seed_offset: int) -> dict:
    windows = make_windows(sim["series"], sim["dt"], None, WINDOW_LEN, STRIDE)
    classical_first_flag = None
    if windows:
        t_ends = [w["t_end"] for w in windows]
        flags = [
            classical_verdict(w["window"], sub_window=CLASSICAL_SUB_WINDOW, n_surrogates=CLASSICAL_N_SURROGATES, seed=seed_offset + i)
            for i, w in enumerate(windows)
        ]
        classical_first_flag = _first_sustained_flag(flags, t_ends, CONSECUTIVE_REQUIRED[sim["kind"]])
    return {"t_event": sim["t_event"], "flag": classical_first_flag}


def summarize(records: list[dict]) -> dict:
    tipped = [r for r in records if r["t_event"] is not None]
    stable = [r for r in records if r["t_event"] is None]
    detected = [r for r in tipped if r["flag"] is not None]
    false_positives = [r for r in stable if r["flag"] is not None]
    lead_times = [r["t_event"] - r["flag"] for r in detected]
    return {
        "n_tipped": len(tipped),
        "n_detected": len(detected),
        "detection_rate": round(len(detected) / len(tipped), 4) if tipped else None,
        "mean_lead_time": round(float(np.mean(lead_times)), 2) if lead_times else None,
        "n_stable": len(stable),
        "n_false_positives": len(false_positives),
        "false_positive_rate": round(len(false_positives) / len(stable), 4) if stable else None,
    }


def _mean_std(values: list[float | None]) -> dict | None:
    clean = [v for v in values if v is not None]
    if not clean:
        return None
    return {"mean": round(float(np.mean(clean)), 4), "std": round(float(np.std(clean)), 4), "values": [round(float(v), 4) for v in clean]}


def main():
    t0 = time.time()

    print("=== Generation du jeu de test partage (graines fraiches, jamais entrainees) ===", flush=True)
    saddle_test_sims = [generate_saddle_node_series(seed=TEST_SEED0 + i, tips=(i % 2 == 0)) for i in range(N_TEST_SADDLE)]
    kuramoto_test_sims = [generate_kuramoto_ramp_series(seed=TEST_SEED0 + N_TEST_SADDLE + i, tips=(i % 2 == 0)) for i in range(N_TEST_KURAMOTO)]
    print(f"{len(saddle_test_sims)} trajectoires noeud-col, {len(kuramoto_test_sims)} trajectoires Kuramoto ({time.time()-t0:.1f}s)", flush=True)

    print("=== Evaluation du detecteur classique (une seule fois, independant de l'entrainement du CNN -- §1.2) ===", flush=True)
    tc0 = time.time()
    saddle_classical_records = [evaluate_trajectory_classical(sim, seed_offset=i * 10_000) for i, sim in enumerate(saddle_test_sims)]
    kuramoto_classical_records = [evaluate_trajectory_classical(sim, seed_offset=(N_TEST_SADDLE + i) * 10_000) for i, sim in enumerate(kuramoto_test_sims)]
    classical_saddle_summary = summarize(saddle_classical_records)
    classical_kuramoto_summary = summarize(kuramoto_classical_records)
    print(f"Detecteur classique evalue en {time.time()-tc0:.1f}s -- noeud-col detect={classical_saddle_summary['detection_rate']}, kuramoto detect={classical_kuramoto_summary['detection_rate']}", flush=True)

    print(f"=== {N_SEEDS} entrainements independants du CNN (initialisation + jeu d'entrainement, §1.1) ===", flush=True)
    per_seed = []
    for seed_idx in range(N_SEEDS):
        ts0 = time.time()
        train_seed0 = TRAIN_SEED0_BASE + seed_idx * 1_000
        X_train, y_train = build_dataset(N_TRAIN_SADDLE, N_TRAIN_KURAMOTO, train_seed0, WINDOW_LEN, STRIDE)
        cnn = SimpleCNN1D(window_len=WINDOW_LEN, seed=seed_idx)
        losses = cnn.fit(X_train, y_train, epochs=100, seed=seed_idx)

        saddle_cnn_records = [evaluate_trajectory_cnn(sim, cnn) for sim in saddle_test_sims]
        kuramoto_cnn_records = [evaluate_trajectory_cnn(sim, cnn) for sim in kuramoto_test_sims]
        saddle_summary = summarize(saddle_cnn_records)
        kuramoto_summary = summarize(kuramoto_cnn_records)

        per_seed.append(
            {
                "seed": seed_idx,
                "n_train_windows": len(X_train),
                "train_loss_initial": round(float(losses[0]), 4),
                "train_loss_final": round(float(losses[-1]), 4),
                "saddle_node": saddle_summary,
                "kuramoto": kuramoto_summary,
                "elapsed_seconds": round(time.time() - ts0, 1),
            }
        )
        print(
            f"  seed {seed_idx}: loss {losses[0]:.4f} -> {losses[-1]:.4f} | "
            f"noeud-col detect={saddle_summary['detection_rate']} lead={saddle_summary['mean_lead_time']} fp={saddle_summary['false_positive_rate']} | "
            f"kuramoto detect={kuramoto_summary['detection_rate']} lead={kuramoto_summary['mean_lead_time']} fp={kuramoto_summary['false_positive_rate']} | "
            f"{time.time()-ts0:.1f}s",
            flush=True,
        )

    cnn_saddle_agg = {
        "detection_rate": _mean_std([s["saddle_node"]["detection_rate"] for s in per_seed]),
        "mean_lead_time": _mean_std([s["saddle_node"]["mean_lead_time"] for s in per_seed]),
        "false_positive_rate": _mean_std([s["saddle_node"]["false_positive_rate"] for s in per_seed]),
    }
    cnn_kuramoto_agg = {
        "detection_rate": _mean_std([s["kuramoto"]["detection_rate"] for s in per_seed]),
        "mean_lead_time": _mean_std([s["kuramoto"]["mean_lead_time"] for s in per_seed]),
        "false_positive_rate": _mean_std([s["kuramoto"]["false_positive_rate"] for s in per_seed]),
    }

    report = {
        "refreshedAt": date.today().isoformat(),
        "windowLen": WINDOW_LEN,
        "stride": STRIDE,
        "nSeeds": N_SEEDS,
        "consecutiveRequired": CONSECUTIVE_REQUIRED,
        "classicalNSurrogates": CLASSICAL_N_SURROGATES,
        "classicalSubWindow": CLASSICAL_SUB_WINDOW,
        "nTrainSaddlePerSeed": N_TRAIN_SADDLE,
        "nTrainKuramotoPerSeed": N_TRAIN_KURAMOTO,
        "nTestSaddle": N_TEST_SADDLE,
        "nTestKuramoto": N_TEST_KURAMOTO,
        "classical": {
            "saddleNode": classical_saddle_summary,
            "kuramoto": classical_kuramoto_summary,
        },
        "cnn": {
            "saddleNode": cnn_saddle_agg,
            "kuramoto": cnn_kuramoto_agg,
            "perSeed": per_seed,
        },
        "elapsedSeconds": round(time.time() - t0, 1),
    }
    OUTPUT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nDone in {report['elapsedSeconds']}s, written to {OUTPUT_PATH}", flush=True)


if __name__ == "__main__":
    main()
