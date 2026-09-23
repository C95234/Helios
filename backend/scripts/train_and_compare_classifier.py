"""Entraine le classifieur et compare a l'indicateur statistique classique
sur un jeu de test independant -- cahier des charges, suite ewstools §3bis.

Calcul hors-ligne, pas un endpoint produit. Sortie : JSON dans
frontend/src/data/results/ia_vs_stats.json (memes conventions que les
autres resultats geles : refreshedAt, chiffres reels).

Usage :
    python scripts/train_and_compare_classifier.py               # entraine + evalue
    python scripts/train_and_compare_classifier.py --eval-only    # recharge le modele deja entraine, revalue seulement
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
    calibrate_variance_threshold,
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
CHECKPOINT_PATH = Path(__file__).resolve().parent.parent / "app" / "data" / "ia_vs_stats_cnn.pt"

WINDOW_LEN = 60
STRIDE = 5
N_TRAIN_SADDLE = 300
N_TRAIN_KURAMOTO = 300
N_TEST_SADDLE = 150
N_TEST_KURAMOTO = 150
TRAIN_SEED0 = 10_000
TEST_SEED0 = 90_000

# Nombre de fenetres CONSECUTIVES positives exigees avant de declarer un
# signal -- sans ce filtre de persistance, une regle appliquee fraiche a
# chaque fenetre independante (~1400 fenetres par trajectoire de test) finit
# presque toujours par declencher au moins une fois par pur hasard, meme sur
# une trajectoire de controle qui ne bascule jamais (verifie : sans filtre,
# le detecteur classique donnait 100% de faux positifs sur les controles
# nœud-col -- pas un vrai resultat, juste "assez d'essais pour que le bruit
# depasse le seuil au moins une fois").
#
# Deuxieme piege trouve en verifiant : a CONSECUTIVE_REQUIRED=3 (stride=5,
# sub_window=15), des fenetres voisines partagent 10 des 15 points de leur
# "queue" -- un seul sursaut de bruit isole se voit donc dans ~3 fenetres qui
# se chevauchent et satisfait trivialement l'exigence de 3 consecutives.
# Valeurs par modele trouvees en balayant 3 a 15 sur des donnees fraiches :
# le nœud-col se separe tres proprement a 6 (2% de fausses alertes, 100% de
# detection). Kuramoto ne se separe PAS proprement a aucune valeur testee
# (le taux de fausses alertes et le taux de detection varient quasiment
# ensemble d'un bout a l'autre du balayage) -- un vrai resultat, pas un bug :
# l'indicateur de variance classique ne discrimine pas bien l'approche d'une
# synchronisation sur ce modele a N=10 oscillateurs. Retenu ici au meilleur
# compromis trouve (percentile 99, 6 consecutives) plutot qu'un choix qui
# maquillerait ce constat en cachant le detecteur derriere un seuil qui ne
# declenche presque jamais.
CONSECUTIVE_REQUIRED = {"saddle_node": 6, "kuramoto": 6}
CALIBRATION_PERCENTILE = {"saddle_node": 95.0, "kuramoto": 99.0}


def _first_sustained_flag(flags: list[bool], t_ends: list[float], consecutive_required: int) -> float | None:
    run = 0
    for i, flag in enumerate(flags):
        run = run + 1 if flag else 0
        if run >= consecutive_required:
            return t_ends[i - consecutive_required + 1]
    return None


def evaluate_trajectory(sim: dict, cnn: SimpleCNN1D, variance_thresholds: dict) -> dict:
    """Fait glisser une fenetre le long de toute la trajectoire, note le
    premier instant ou chaque methode bascule en positif de facon
    SOUTENUE (`CONSECUTIVE_REQUIRED` fenetres consecutives, pas une
    fenetre isolee), compare a l'instant reel de bascule -- meme schema
    que `run_precedence_batch`, avec le meme esprit de garde-fou contre
    le bruit que `detect_precedence` (seuil + fenetre glissante, pas un
    coup isole). Le seuil du detecteur classique depend de `sim["kind"]`
    (nœud-col et Kuramoto n'ont pas la meme distribution de bruit de
    base -- voir `calibrate_variance_threshold`)."""
    series, dt, t_event = sim["series"], sim["dt"], sim["t_event"]
    threshold = variance_thresholds[sim["kind"]]
    consecutive_required = CONSECUTIVE_REQUIRED[sim["kind"]]
    windows = make_windows(series, dt, None, WINDOW_LEN, STRIDE)  # toutes les fenetres, labels ignores ici

    cnn_first_flag = None
    classical_first_flag = None

    if windows:
        t_ends = [w["t_end"] for w in windows]
        X = np.stack([w["window"] for w in windows]).astype(np.float32)
        probs = cnn.predict_proba(X)
        cnn_flags = [bool(p > 0.5) for p in probs]
        classical_flags = [classical_verdict(w["window"], dt, variance_threshold=threshold) for w in windows]

        cnn_first_flag = _first_sustained_flag(cnn_flags, t_ends, consecutive_required)
        classical_first_flag = _first_sustained_flag(classical_flags, t_ends, consecutive_required)

    return {
        "t_event": t_event,
        "cnn_first_flag": cnn_first_flag,
        "classical_first_flag": classical_first_flag,
    }


def summarize(records: list[dict], label: str) -> dict:
    tipped = [r for r in records if r["t_event"] is not None]
    stable = [r for r in records if r["t_event"] is None]

    def detection_stats(flag_key: str):
        detected = [r for r in tipped if r[flag_key] is not None]
        false_positives = [r for r in stable if r[flag_key] is not None]
        lead_times = [r["t_event"] - r[flag_key] for r in detected]
        return {
            "n_tipped": len(tipped),
            "n_detected": len(detected),
            "detection_rate": round(len(detected) / len(tipped), 4) if tipped else None,
            "mean_lead_time": round(float(np.mean(lead_times)), 2) if lead_times else None,
            "n_stable": len(stable),
            "n_false_positives": len(false_positives),
            "false_positive_rate": round(len(false_positives) / len(stable), 4) if stable else None,
        }

    return {
        "kind": label,
        "cnn": detection_stats("cnn_first_flag"),
        "classical": detection_stats("classical_first_flag"),
    }


def main():
    eval_only = "--eval-only" in sys.argv
    t0 = time.time()

    cnn = SimpleCNN1D(window_len=WINDOW_LEN, seed=0)

    if eval_only and CHECKPOINT_PATH.exists():
        print(f"=== Rechargement du modele deja entraine ({CHECKPOINT_PATH}) ===", flush=True)
        cnn.load(str(CHECKPOINT_PATH))
        loss_initial, loss_final = None, None
    else:
        print("=== Generation du jeu d'entrainement ===", flush=True)
        X_train, y_train = build_dataset(N_TRAIN_SADDLE, N_TRAIN_KURAMOTO, TRAIN_SEED0, WINDOW_LEN, STRIDE)
        print(f"{len(X_train)} fenetres, {int(y_train.sum())} positives, {int(len(y_train) - y_train.sum())} negatives", flush=True)

        print("=== Entrainement du CNN ===", flush=True)
        losses = cnn.fit(X_train, y_train, epochs=100, seed=0)
        loss_initial, loss_final = losses[0], losses[-1]
        print(f"loss initiale={loss_initial:.4f}, loss finale={loss_final:.4f}", flush=True)

        CHECKPOINT_PATH.parent.mkdir(parents=True, exist_ok=True)
        cnn.save(str(CHECKPOINT_PATH))
        print(f"Modele sauvegarde dans {CHECKPOINT_PATH}", flush=True)

    print("=== Calibration des seuils du detecteur classique ===", flush=True)
    threshold_saddle = calibrate_variance_threshold(n_series=150, percentile=CALIBRATION_PERCENTILE["saddle_node"], seed=20_000, kind="saddle_node")
    threshold_kuramoto = calibrate_variance_threshold(n_series=150, percentile=CALIBRATION_PERCENTILE["kuramoto"], seed=20_000, kind="kuramoto")
    variance_thresholds = {"saddle_node": threshold_saddle, "kuramoto": threshold_kuramoto}
    print(f"seuil noeud-col={threshold_saddle:.4f}, seuil kuramoto={threshold_kuramoto:.4f}", flush=True)

    print("=== Generation du jeu de test (graines fraiches) ===", flush=True)
    saddle_records = []
    for i in range(N_TEST_SADDLE):
        tips = i % 2 == 0
        sim = generate_saddle_node_series(seed=TEST_SEED0 + i, tips=tips)
        saddle_records.append(evaluate_trajectory(sim, cnn, variance_thresholds))

    kuramoto_records = []
    for i in range(N_TEST_KURAMOTO):
        tips = i % 2 == 0
        sim = generate_kuramoto_ramp_series(seed=TEST_SEED0 + N_TEST_SADDLE + i, tips=tips)
        kuramoto_records.append(evaluate_trajectory(sim, cnn, variance_thresholds))

    saddle_summary = summarize(saddle_records, "saddle_node")
    kuramoto_summary = summarize(kuramoto_records, "kuramoto")
    pooled_summary = summarize(saddle_records + kuramoto_records, "pooled")

    print(json.dumps(saddle_summary, indent=2), flush=True)
    print(json.dumps(kuramoto_summary, indent=2), flush=True)
    print(json.dumps(pooled_summary, indent=2), flush=True)

    report = {
        "refreshedAt": date.today().isoformat(),
        "windowLen": WINDOW_LEN,
        "stride": STRIDE,
        "consecutiveRequired": CONSECUTIVE_REQUIRED,
        "calibrationPercentile": CALIBRATION_PERCENTILE,
        "nTrainSaddle": N_TRAIN_SADDLE,
        "nTrainKuramoto": N_TRAIN_KURAMOTO,
        "nTestSaddle": N_TEST_SADDLE,
        "nTestKuramoto": N_TEST_KURAMOTO,
        "trainLossInitial": round(loss_initial, 4) if loss_initial is not None else None,
        "trainLossFinal": round(loss_final, 4) if loss_final is not None else None,
        "saddleVarianceThreshold": round(threshold_saddle, 4),
        "kuramotoVarianceThreshold": round(threshold_kuramoto, 4),
        "saddleNode": saddle_summary,
        "kuramoto": kuramoto_summary,
        "pooled": pooled_summary,
        "elapsedSeconds": round(time.time() - t0, 1),
    }
    OUTPUT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nDone in {report['elapsedSeconds']}s, written to {OUTPUT_PATH}", flush=True)


if __name__ == "__main__":
    main()
