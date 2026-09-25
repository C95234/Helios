"""§2.3 du cahier des charges "banc d'essai IA vs statistiques" : entraine un
ensemble de classifieurs a double entree (`app/h3_ml.DualBranchFusionClassifier`,
fenetre temporelle + instantane spatial, MEME systeme, MEME instant) a
detecter une anomalie JOINTE pres d'une bascule reelle simulee sur le reseau
reel des departements, evalue face a une baseline classique combinant
tendance temporelle + indice de Moran, puis applique l'ensemble aux 6
phenomenes reels deja testes par H3 (`stats/h3_joint.py`) -- comparaison a
armes egales sur la MEME tache, jamais combinee au verdict statistique de H3
lui-meme (§2, garde-fou de presentation).

Meme topologie reelle (w_real, memes departements) que le classifieur
spatial de §2.2, recuperee une seule fois avant de generer la moindre
donnee d'entrainement synthetique.

Calcul hors-ligne. Sortie : JSON dans
frontend/src/data/results/ia_vs_stats_real_h3.json
"""
from __future__ import annotations

import asyncio
import json
import sys
import time
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
import torch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.connectors.insee import InseeBdmConnector  # noqa: E402
from app.h3_ml import DualBranchFusionClassifier, classical_joint_predictions, generate_joint_dataset  # noqa: E402
from app.phenomena import PHENOMENA  # noqa: E402
from app.spatial_series import get_real_network_moran_series  # noqa: E402

OUTPUT_PATH = (
    Path(__file__).resolve().parent.parent.parent
    / "frontend"
    / "src"
    / "data"
    / "results"
    / "ia_vs_stats_real_h3.json"
)
CHECKPOINT_DIR = Path(__file__).resolve().parent.parent / "app" / "data" / "joint_classifier_ensemble"
NATIONAL_IDBANK = "001587668"  # meme serie que routers/h3.py -- confiance des menages

N_SEEDS = 10
N_TRAIN_RUNS_PER_CLASS = 10
N_TEST_RUNS_PER_CLASS = 15
FIT_EPOCHS = 30
FIT_BATCH_SIZE = 64
TRAIN_SEED0_BASE = 40_000
TEST_SEED0 = 95_000
WINDOW_LEN = 60
SIM_DT = 0.02
SIM_T_MAX = 150.0
SIM_MU_RATE_TIP = 0.02
SNAPSHOT_STRIDE = 5
HORIZON_STEPS = 150


def train_or_load_ensemble(w_real: np.ndarray, x_temporal_test, x_spatial_test, y_test) -> tuple[list[DualBranchFusionClassifier], list[dict]]:
    CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)
    models, per_seed = [], []
    all_checkpoints_exist = all((CHECKPOINT_DIR / f"seed_{i}.pt").exists() for i in range(N_SEEDS))
    if all_checkpoints_exist:
        print(f"  {N_SEEDS} checkpoints deja entraines trouves, rechargement...", flush=True)
        for seed_idx in range(N_SEEDS):
            model = DualBranchFusionClassifier(WINDOW_LEN, w_real, seed=seed_idx)
            model.load(str(CHECKPOINT_DIR / f"seed_{seed_idx}.pt"))
            models.append(model)
            probs = model.predict_proba(x_temporal_test, x_spatial_test)
            acc = float(np.mean((probs > 0.5) == y_test))
            per_seed.append({"seed": seed_idx, "accuracy": round(acc, 4)})
        return models, per_seed

    print("  Aucun checkpoint complet trouve, entrainement depuis zero...", flush=True)
    for seed_idx in range(N_SEEDS):
        t0 = time.time()
        train_seed0 = TRAIN_SEED0_BASE + seed_idx * 1_000
        xt_train, xs_train, y_train = generate_joint_dataset(
            w_real, n_runs_per_class=N_TRAIN_RUNS_PER_CLASS, seed0=train_seed0, window_len=WINDOW_LEN,
            dt=SIM_DT, t_max=SIM_T_MAX, mu_rate_tip=SIM_MU_RATE_TIP, snapshot_stride=SNAPSHOT_STRIDE,
            horizon_steps=HORIZON_STEPS,
        )
        model = DualBranchFusionClassifier(WINDOW_LEN, w_real, seed=seed_idx)
        losses = model.fit(xt_train, xs_train, y_train, epochs=FIT_EPOCHS, batch_size=FIT_BATCH_SIZE, seed=seed_idx)
        probs = model.predict_proba(x_temporal_test, x_spatial_test)
        acc = float(np.mean((probs > 0.5) == y_test))
        print(
            f"  modele {seed_idx} : loss {losses[0]:.4f} -> {losses[-1]:.4f}, "
            f"accuracy test {acc:.4f} ({time.time()-t0:.1f}s, {len(y_train)} exemples d'entrainement, "
            f"{int(y_train.sum())} positifs)",
            flush=True,
        )
        model.save(str(CHECKPOINT_DIR / f"seed_{seed_idx}.pt"))
        models.append(model)
        per_seed.append({"seed": seed_idx, "accuracy": round(acc, 4)})
    return models, per_seed


def ensemble_predict(models: list[DualBranchFusionClassifier], xt: np.ndarray, xs: np.ndarray) -> np.ndarray:
    """Evaluation sur donnees SIMULEES (jeu de test partage) : reutilise la
    normalisation globale figee a l'entrainement (`predict_proba`), pour que
    l'accuracy en ensemble reste comparable aux accuracy individuelles
    (memes conditions que celles vues a l'entrainement)."""
    probs = np.stack([m.predict_proba(xt, xs) for m in models])
    return probs.mean(axis=0)


def ensemble_predict_real_data(models: list[DualBranchFusionClassifier], xt: np.ndarray, xs: np.ndarray) -> np.ndarray:
    """Application a des donnees REELLES (§2.1/§2.4, meme adaptation) :
    l'indice de confiance des menages et les residus de chomage n'ont aucun
    rapport d'echelle avec les quantites simulees vues a l'entrainement --
    chaque fenetre/instantane est donc centre-reduit par SA PROPRE
    moyenne/ecart-type plutot que par la normalisation globale d'entrainement,
    qui ne conviendrait pas du tout a cette echelle."""
    probs = []
    for m in models:
        m.eval()
        xt_norm = (xt - xt.mean(axis=1, keepdims=True)) / (xt.std(axis=1, keepdims=True) + 1e-8)
        xs_norm = (xs - xs.mean(axis=1, keepdims=True)) / (xs.std(axis=1, keepdims=True) + 1e-8)
        with torch.no_grad():
            logits = m(torch.tensor(xt_norm, dtype=torch.float32), torch.tensor(xs_norm, dtype=torch.float32))
            probs.append(torch.sigmoid(logits).numpy())
    return np.stack(probs).mean(axis=0)


async def main():
    t0 = time.time()
    print("=== Recuperation de la topologie reelle + serie spatiale Insee ===", flush=True)
    spatial = await get_real_network_moran_series()
    w_real, codes = spatial["w_real"], spatial["codes"]
    residuals = spatial["residuals"]
    print(f"  {len(codes)} departements", flush=True)

    print("=== Recuperation de la serie nationale (confiance des menages, meme serie que H3) ===", flush=True)
    insee = InseeBdmConnector()
    raw = await insee.fetch(idbank=NATIONAL_IDBANK, start_period="2000-01")
    national_series = insee.normalize(raw).set_index("date")["valeur"].sort_index()

    print("=== Generation du jeu de test partage (graines jamais vues a l'entrainement) ===", flush=True)
    xt_test, xs_test, y_test = generate_joint_dataset(
        w_real, n_runs_per_class=N_TEST_RUNS_PER_CLASS, seed0=TEST_SEED0, window_len=WINDOW_LEN,
        dt=SIM_DT, t_max=SIM_T_MAX, mu_rate_tip=SIM_MU_RATE_TIP, snapshot_stride=SNAPSHOT_STRIDE,
        horizon_steps=HORIZON_STEPS,
    )
    print(f"  {len(y_test)} paires de test ({int(y_test.sum())} anomalies jointes, {int((1-y_test).sum())} negatives)", flush=True)

    print("=== Baseline classique (tendance temporelle + indice de Moran, sans reseau de neurones) ===", flush=True)
    classical_preds = classical_joint_predictions(xt_test, xs_test, w_real)
    classical_accuracy = float(np.mean(classical_preds == y_test))
    print(f"  accuracy classique : {classical_accuracy:.4f}", flush=True)

    print(f"=== Ensemble de {N_SEEDS} classifieurs a double entree ===", flush=True)
    models, per_seed = train_or_load_ensemble(w_real, xt_test, xs_test, y_test)
    accuracies = [r["accuracy"] for r in per_seed]
    cnn_ensemble_probs = ensemble_predict(models, xt_test, xs_test)
    cnn_ensemble_accuracy = float(np.mean((cnn_ensemble_probs > 0.5) == y_test))

    print("=== Application aux 6 phenomenes reels deja testes par H3 ===", flush=True)
    phenomena_results = []
    quarterly_dates = spatial["dates"]
    for key, spec in PHENOMENA.items():
        end = pd.Timestamp(spec["end"])
        window = national_series[national_series.index <= end].tail(WINDOW_LEN)
        nearest_idx = quarterly_dates.get_indexer([end], method="nearest")[0]
        if len(window) < WINDOW_LEN:
            phenomena_results.append({"key": key, "label": spec["label"], "error": f"historique national insuffisant ({len(window)} points)"})
            continue
        xt = window.to_numpy(dtype=np.float32)[None, :]
        xs = residuals.iloc[nearest_idx].to_numpy(dtype=np.float32)[None, :]
        prob = float(ensemble_predict_real_data(models, xt, xs)[0])
        classical_pred = bool(classical_joint_predictions(xt, xs, w_real)[0])
        phenomena_results.append({
            "key": key,
            "label": spec["label"],
            "nearest_spatial_quarter": quarterly_dates[nearest_idx].strftime("%Y-%m-%d"),
            "cnn_probability_joint_anomaly": round(prob, 4),
            "cnn_flagged": prob > 0.5,
            "classical_flagged": classical_pred,
        })
        print(f"  {key}: P(anomalie jointe)={prob:.4f} (CNN {'OUI' if prob > 0.5 else 'non'}, classique {'OUI' if classical_pred else 'non'})", flush=True)

    report = {
        "refreshedAt": date.today().isoformat(),
        "nSeeds": N_SEEDS,
        "nNodes": len(codes),
        "windowLen": WINDOW_LEN,
        "nTrainRunsPerClass": N_TRAIN_RUNS_PER_CLASS,
        "nTestRunsPerClass": N_TEST_RUNS_PER_CLASS,
        "nTestPairs": len(y_test),
        "nTestPositive": int(y_test.sum()),
        "classical": {"accuracy": round(classical_accuracy, 4)},
        "cnn": {
            "perSeed": per_seed,
            "meanAccuracy": round(float(np.mean(accuracies)), 4),
            "stdAccuracy": round(float(np.std(accuracies)), 4),
            "ensembleAccuracy": round(cnn_ensemble_accuracy, 4),
        },
        "phenomena": phenomena_results,
        "elapsedSeconds": round(time.time() - t0, 1),
    }
    OUTPUT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nDone in {report['elapsedSeconds']}s, written to {OUTPUT_PATH}", flush=True)
    print(f"Accuracy sur paires simulees -- classique : {classical_accuracy:.4f}, ensemble CNN : {cnn_ensemble_accuracy:.4f}", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
