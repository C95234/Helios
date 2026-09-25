"""§2.2 du cahier des charges "banc d'essai IA vs statistiques" : entraine un
ensemble de classifieurs spatiaux (`app/spatial_ml.SpatialGraphClassifier`) a
distinguer un instantane genere sur le RESEAU REEL des departements d'un
instantane genere sur la GRILLE DE CONTROLE de meme taille, evalue sa
capacite de discrimination face a la baseline classique (indice de Moran,
sans aucun parametre appris), puis applique l'ensemble a la vraie serie
spatiale de chomage departemental deja utilisee par H2 -- comparaison a
armes egales sur la MEME tache, jamais combinee au verdict statistique de H2
lui-meme (§2, garde-fou de presentation).

Topologie (reseau reel + grille de controle) DERIVEE de la vraie serie
Insee (memes codes departement, meme ordre) avant de generer la moindre
donnee d'entrainement synthetique -- pour que le nombre de noeuds et
l'identite de chaque noeud restent rigoureusement les memes entre
l'entrainement et l'application aux donnees reelles.

Calcul hors-ligne. Sortie : JSON dans
frontend/src/data/results/ia_vs_stats_real_h2.json
"""
from __future__ import annotations

import asyncio
import json
import sys
import time
from datetime import date
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.spatial_ml import (  # noqa: E402
    SpatialGraphClassifier,
    classical_moran_predictions,
    generate_topology_dataset,
)
from app.spatial_series import get_department_unemployment_wide, compute_network_moran_series  # noqa: E402

OUTPUT_PATH = (
    Path(__file__).resolve().parent.parent.parent
    / "frontend"
    / "src"
    / "data"
    / "results"
    / "ia_vs_stats_real_h2.json"
)
CHECKPOINT_DIR = Path(__file__).resolve().parent.parent / "app" / "data" / "spatial_classifier_ensemble"

N_SEEDS = 10
N_TRAIN_RUNS_PER_CLASS = 10
N_TEST_RUNS_PER_CLASS = 15
FIT_EPOCHS = 40
FIT_BATCH_SIZE = 64
TRAIN_SEED0_BASE = 20_000
TEST_SEED0 = 90_000
SIM_DT = 0.02
SIM_T_MAX = 150.0
SIM_MU_RATE = 0.02
SNAPSHOT_STRIDE = 50


def train_or_load_ensemble(w_real: np.ndarray, w_grid: np.ndarray, X_test: np.ndarray, y_test: np.ndarray) -> tuple[list[SpatialGraphClassifier], list[dict]]:
    CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)
    models = []
    per_seed = []
    all_checkpoints_exist = all((CHECKPOINT_DIR / f"seed_{i}.pt").exists() for i in range(N_SEEDS))
    if all_checkpoints_exist:
        print(f"  {N_SEEDS} checkpoints deja entraines trouves, rechargement...", flush=True)
        for seed_idx in range(N_SEEDS):
            model = SpatialGraphClassifier(w_real, w_grid, seed=seed_idx)
            model.load(str(CHECKPOINT_DIR / f"seed_{seed_idx}.pt"))
            models.append(model)
            probs = model.predict_proba(X_test)
            acc = float(np.mean((probs > 0.5) == y_test))
            per_seed.append({"seed": seed_idx, "accuracy": round(acc, 4)})
        return models, per_seed

    print("  Aucun checkpoint complet trouve, entrainement depuis zero...", flush=True)
    for seed_idx in range(N_SEEDS):
        t0 = time.time()
        train_seed0 = TRAIN_SEED0_BASE + seed_idx * 1_000
        X_train, y_train = generate_topology_dataset(
            w_real, w_grid, n_runs_per_class=N_TRAIN_RUNS_PER_CLASS, seed0=train_seed0,
            dt=SIM_DT, t_max=SIM_T_MAX, mu_rate=SIM_MU_RATE, snapshot_stride=SNAPSHOT_STRIDE,
        )
        model = SpatialGraphClassifier(w_real, w_grid, seed=seed_idx)
        losses = model.fit(X_train, y_train, epochs=FIT_EPOCHS, batch_size=FIT_BATCH_SIZE, seed=seed_idx)
        probs = model.predict_proba(X_test)
        acc = float(np.mean((probs > 0.5) == y_test))
        print(
            f"  modele {seed_idx} : loss {losses[0]:.4f} -> {losses[-1]:.4f}, "
            f"accuracy test {acc:.4f} ({time.time()-t0:.1f}s, {len(X_train)} exemples d'entrainement)",
            flush=True,
        )
        model.save(str(CHECKPOINT_DIR / f"seed_{seed_idx}.pt"))
        models.append(model)
        per_seed.append({"seed": seed_idx, "accuracy": round(acc, 4)})
    return models, per_seed


def ensemble_predict(models: list[SpatialGraphClassifier], X: np.ndarray) -> np.ndarray:
    probs = np.stack([m.predict_proba(X) for m in models])
    return probs.mean(axis=0)


async def main():
    t0 = time.time()
    print("=== Recuperation de la serie reelle Insee (topologie + application) ===", flush=True)
    wide = await get_department_unemployment_wide()
    spatial = compute_network_moran_series(wide)
    w_real, w_grid = spatial["w_real"], spatial["w_grid"]
    codes = spatial["codes"]
    print(f"  {len(codes)} departements, topologie reelle + grille de controle {spatial['grid_shape']}", flush=True)

    print("=== Generation du jeu de test partage (graines jamais vues a l'entrainement) ===", flush=True)
    X_test, y_test = generate_topology_dataset(
        w_real, w_grid, n_runs_per_class=N_TEST_RUNS_PER_CLASS, seed0=TEST_SEED0,
        dt=SIM_DT, t_max=SIM_T_MAX, mu_rate=SIM_MU_RATE, snapshot_stride=SNAPSHOT_STRIDE,
    )
    print(f"  {len(X_test)} instantanes de test ({int(y_test.sum())} reseau reel, {int((1-y_test).sum())} grille)", flush=True)

    print("=== Baseline classique (indice de Moran, sans parametre appris) ===", flush=True)
    classical_preds = classical_moran_predictions(X_test, w_real, w_grid)
    classical_accuracy = float(np.mean(classical_preds == y_test))
    print(f"  accuracy classique : {classical_accuracy:.4f}", flush=True)

    print(f"=== Ensemble de {N_SEEDS} classifieurs spatiaux (graphe) ===", flush=True)
    models, per_seed = train_or_load_ensemble(w_real, w_grid, X_test, y_test)
    accuracies = [r["accuracy"] for r in per_seed]
    cnn_ensemble_probs = ensemble_predict(models, X_test)
    cnn_ensemble_accuracy = float(np.mean((cnn_ensemble_probs > 0.5) == y_test))

    print("=== Application a la vraie serie de chomage departemental (residus detrendes, §5.2) ===", flush=True)
    residuals = spatial["residuals"].to_numpy().astype(np.float32)
    real_probs = ensemble_predict(models, residuals)
    real_classical_preds = classical_moran_predictions(residuals, w_real, w_grid)
    n_periods = len(residuals)

    report = {
        "refreshedAt": date.today().isoformat(),
        "nSeeds": N_SEEDS,
        "nNodes": len(codes),
        "nTrainRunsPerClass": N_TRAIN_RUNS_PER_CLASS,
        "nTestRunsPerClass": N_TEST_RUNS_PER_CLASS,
        "nTestSnapshots": len(X_test),
        "classical": {
            "accuracy": round(classical_accuracy, 4),
        },
        "cnn": {
            "perSeed": per_seed,
            "meanAccuracy": round(float(np.mean(accuracies)), 4),
            "stdAccuracy": round(float(np.std(accuracies)), 4),
            "ensembleAccuracy": round(cnn_ensemble_accuracy, 4),
        },
        "realData": {
            "nPeriods": n_periods,
            "periodStart": spatial["dates"][0].strftime("%Y-%m-%d"),
            "periodEnd": spatial["dates"][-1].strftime("%Y-%m-%d"),
            "meanProbabilityRealNetwork": round(float(real_probs.mean()), 4),
            "fractionClassifiedRealNetworkCnn": round(float((real_probs > 0.5).mean()), 4),
            "fractionClassifiedRealNetworkClassical": round(float(real_classical_preds.mean()), 4),
        },
        "elapsedSeconds": round(time.time() - t0, 1),
    }
    OUTPUT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nDone in {report['elapsedSeconds']}s, written to {OUTPUT_PATH}", flush=True)
    print(
        f"Accuracy sur instantanes simules -- classique : {classical_accuracy:.4f}, "
        f"ensemble CNN : {cnn_ensemble_accuracy:.4f} (individuel : {np.mean(accuracies):.4f} +/- {np.std(accuracies):.4f})",
        flush=True,
    )
    print(
        f"Sur les {n_periods} periodes reelles : {report['realData']['fractionClassifiedRealNetworkCnn']*100:.1f}% "
        f"classees 'reseau reel' par le CNN, {report['realData']['fractionClassifiedRealNetworkClassical']*100:.1f}% par Moran.",
        flush=True,
    )


if __name__ == "__main__":
    asyncio.run(main())
