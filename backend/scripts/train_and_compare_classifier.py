"""Entraine le classifieur et compare a l'indicateur statistique classique
sur un jeu de test independant -- cahier des charges "banc d'essai IA vs
statistiques : rigueur, extension, pedagogie" (§1, revision "architecture
fidele a Bury et al.").

§1.1 : le classifieur reprend l'architecture reelle de Bury et al. (2021)
(CNN-LSTM, voir CnnLstmClassifier dans ml_benchmark.py) plutot qu'un CNN
simplifie, entraine en ENSEMBLE DE 10 MODELES independants (leur propre
methode de robustesse, reprise telle quelle plutot qu'un protocole "5 a 10
graines" improvise) -- moyenne et ecart-type rapportes pour chaque metrique,
jamais un chiffre unique.

Garde-fou de positionnement (§1.1, a ne jamais afficher sur le site) :
l'objectif est de reproduire fidelement une methode publiee et de la tester
sur de nouveaux modeles/donnees, jamais de pretendre "faire mieux" que Bury
et al. -- aucun tableau comparatif a leurs chiffres publies, aucun
vocabulaire de superiorite sur le site.

§1.1bis : le classifieur est aussi teste sur des series AR(1) stationnaires
(Dablander & Bury, 2021 -- critique de pretraitement) pour verifier qu'il ne
les classe pas a tort comme approchant une bascule.

§1.2 : le detecteur "classique" utilise l'indicateur complet de H1 (variance
ET AC1 glissantes, tau de Kendall, test par donnees de substitution --
`classical_verdict`, ml_benchmark.py). Ce detecteur ne depend pas de
l'architecture du classifieur : son resultat est REUTILISE tel quel depuis
le fichier de resultat existant si present (deja calcule ~19 minutes lors
du chantier precedent), jamais recalcule inutilement.

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
    CnnLstmClassifier,
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
CHECKPOINT_DIR = Path(__file__).resolve().parent.parent / "app" / "data" / "ia_vs_stats_ensemble"

WINDOW_LEN = 60
STRIDE = 5

# §1.1 -- ensemble de 10 modeles independants, la methode de Bury et al.
# eux-memes, reprise telle quelle plutot qu'un protocole ad hoc.
N_SEEDS = 10

# Adaptation Helios -- echelle d'entrainement drastiquement reduite par
# rapport a Bury et al. (200 000 sequences de longueur 500-1500, 1500
# epoques en pleine-batch) : verifie directement sur ce materiel qu'une
# seule epoque pleine-batch a 95 000 fenetres de longueur 60 prend deja
# ~150s -- l'echelle de Bury et al. y prendrait des heures par modele, x10
# modeles. Entrainement par mini-lots (Bury et al. utilisent aussi des
# lots, batch_size=1000 -- seule la taille change) sur un jeu reduit.
N_TRAIN_SADDLE = 10
N_TRAIN_KURAMOTO = 10
FIT_EPOCHS = 25
FIT_BATCH_SIZE = 256
N_TEST_SADDLE = 30
N_TEST_KURAMOTO = 30
TRAIN_SEED0_BASE = 10_000
TEST_SEED0 = 90_000  # FIXE, partage entre tous les seeds CNN et le detecteur classique

CLASSICAL_N_SURROGATES = 100
CLASSICAL_SUB_WINDOW = 15

# §1.1bis -- series AR(1) stationnaires (Dablander & Bury 2021) : aucune
# vraie bifurcation, le classifieur ne devrait PAS les flaguer comme
# approchant une bascule.
AR1_PHI_VALUES = [0.1, 0.3, 0.5, 0.7, 0.9]
AR1_N_PER_PHI = 30
AR1_SEED0 = 70_000


def generate_ar1_series(seed: int, phi: float, sigma: float = 1.0, n: int = WINDOW_LEN) -> np.ndarray:
    """Serie AR(1) stationnaire x_t = phi*x_{t-1} + bruit -- pas de bifurcation,
    juste de la persistance temporelle (§1.1bis, Dablander & Bury 2021)."""
    rng = np.random.default_rng(seed)
    x = np.zeros(n)
    for t in range(1, n):
        x[t] = phi * x[t - 1] + rng.normal(scale=sigma)
    return x


def evaluate_ar1_false_positive_rate(models: list[CnnLstmClassifier]) -> dict:
    """Fraction des fenetres AR(1) stationnaires flaguees a tort comme
    "approchant une bascule" par l'ensemble (moyenne des N_SEEDS modeles,
    seuil 0,5) -- par valeur de phi et au global."""
    per_phi = {}
    all_flags = []
    for phi in AR1_PHI_VALUES:
        windows = np.stack(
            [generate_ar1_series(seed=AR1_SEED0 + int(phi * 1000) + i, phi=phi) for i in range(AR1_N_PER_PHI)]
        ).astype(np.float32)
        probs = np.mean([m.predict_proba(windows) for m in models], axis=0)
        flags = probs > 0.5
        per_phi[str(phi)] = {"n": len(flags), "n_flagged": int(flags.sum()), "flagged_fraction": round(float(flags.mean()), 4), "mean_probability": round(float(probs.mean()), 4)}
        all_flags.extend(flags.tolist())
    return {
        "perPhi": per_phi,
        "overallFlaggedFraction": round(float(np.mean(all_flags)), 4),
        "nTotal": len(all_flags),
    }

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


def evaluate_trajectory_cnn(sim: dict, cnn: CnnLstmClassifier) -> dict:
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


def _load_existing_classical() -> dict | None:
    """Le detecteur classique (§1.2) ne depend pas de l'architecture du
    classifieur -- reutilise le resultat deja calcule (chantier precedent,
    ~19 minutes) plutot que de le recalculer inutilement pour ce changement
    d'architecture."""
    if not OUTPUT_PATH.exists():
        return None
    try:
        existing = json.loads(OUTPUT_PATH.read_text(encoding="utf-8"))
        classical = existing.get("classical")
        if classical and classical.get("saddleNode") and classical.get("kuramoto"):
            return classical
    except (json.JSONDecodeError, OSError):
        pass
    return None


def main():
    t0 = time.time()

    print("=== Generation du jeu de test partage (graines fraiches, jamais entrainees) ===", flush=True)
    saddle_test_sims = [generate_saddle_node_series(seed=TEST_SEED0 + i, tips=(i % 2 == 0)) for i in range(N_TEST_SADDLE)]
    kuramoto_test_sims = [generate_kuramoto_ramp_series(seed=TEST_SEED0 + N_TEST_SADDLE + i, tips=(i % 2 == 0)) for i in range(N_TEST_KURAMOTO)]
    print(f"{len(saddle_test_sims)} trajectoires noeud-col, {len(kuramoto_test_sims)} trajectoires Kuramoto ({time.time()-t0:.1f}s)", flush=True)

    existing_classical = _load_existing_classical()
    if existing_classical is not None:
        print("=== Detecteur classique : reutilise le resultat deja calcule (§1.2, independant de l'architecture) ===", flush=True)
        classical_saddle_summary = existing_classical["saddleNode"]
        classical_kuramoto_summary = existing_classical["kuramoto"]
    else:
        print("=== Evaluation du detecteur classique (aucun resultat existant trouve -- §1.2) ===", flush=True)
        tc0 = time.time()
        saddle_classical_records = [evaluate_trajectory_classical(sim, seed_offset=i * 10_000) for i, sim in enumerate(saddle_test_sims)]
        kuramoto_classical_records = [evaluate_trajectory_classical(sim, seed_offset=(N_TEST_SADDLE + i) * 10_000) for i, sim in enumerate(kuramoto_test_sims)]
        classical_saddle_summary = summarize(saddle_classical_records)
        classical_kuramoto_summary = summarize(kuramoto_classical_records)
        print(f"Detecteur classique evalue en {time.time()-tc0:.1f}s", flush=True)
    print(f"noeud-col detect={classical_saddle_summary['detection_rate']}, kuramoto detect={classical_kuramoto_summary['detection_rate']}", flush=True)

    print(f"=== {N_SEEDS} entrainements independants du CNN-LSTM (architecture Bury et al., §1.1) ===", flush=True)
    per_seed = []
    models: list[CnnLstmClassifier] = []
    for seed_idx in range(N_SEEDS):
        ts0 = time.time()
        train_seed0 = TRAIN_SEED0_BASE + seed_idx * 1_000
        X_train, y_train = build_dataset(N_TRAIN_SADDLE, N_TRAIN_KURAMOTO, train_seed0, WINDOW_LEN, STRIDE)
        cnn = CnnLstmClassifier(window_len=WINDOW_LEN, seed=seed_idx)
        losses = cnn.fit(X_train, y_train, epochs=FIT_EPOCHS, batch_size=FIT_BATCH_SIZE, seed=seed_idx)
        models.append(cnn)
        CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)
        cnn.save(str(CHECKPOINT_DIR / f"seed_{seed_idx}.pt"))

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

    print("=== Test de validite sur series AR(1) stationnaires (§1.1bis, Dablander & Bury 2021) ===", flush=True)
    ar1_result = evaluate_ar1_false_positive_rate(models)
    print(f"  fraction flaguee a tort (toutes phi confondues) : {ar1_result['overallFlaggedFraction']*100:.1f}% sur {ar1_result['nTotal']} fenetres", flush=True)
    for phi, stats in ar1_result["perPhi"].items():
        print(f"    phi={phi}: {stats['n_flagged']}/{stats['n']} flaguees ({stats['flagged_fraction']*100:.1f}%)", flush=True)

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
        "architecture": {
            "type": "CNN-LSTM",
            "sourcedFrom": "github.com/ThomasMBury/deep-early-warnings-pnas (dl_train/DL_training.py)",
            "filters": CnnLstmClassifier.FILTERS,
            "kernelSize": CnnLstmClassifier.KERNEL_SIZE,
            "lstm1Units": CnnLstmClassifier.LSTM1_UNITS,
            "lstm2Units": CnnLstmClassifier.LSTM2_UNITS,
            "dropout": CnnLstmClassifier.DROPOUT,
            "fitEpochs": FIT_EPOCHS,
            "fitBatchSize": FIT_BATCH_SIZE,
        },
        "classical": {
            "saddleNode": classical_saddle_summary,
            "kuramoto": classical_kuramoto_summary,
        },
        "cnn": {
            "saddleNode": cnn_saddle_agg,
            "kuramoto": cnn_kuramoto_agg,
            "perSeed": per_seed,
        },
        "ar1Validity": ar1_result,
        "elapsedSeconds": round(time.time() - t0, 1),
    }
    OUTPUT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nDone in {report['elapsedSeconds']}s, written to {OUTPUT_PATH}", flush=True)


if __name__ == "__main__":
    main()
