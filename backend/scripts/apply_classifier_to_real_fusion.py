"""§2.4 du cahier des charges "banc d'essai IA vs statistiques" : applique
le classifieur entraine sur les modeles SIMULES (nœud-col, Kuramoto) a la
batterie curatee de tirs REELS MAST deja utilisee pour le domaine Fusion
(routers/fusion.py), et compare son verdict a celui deja publie
(`precursor`, results/fusion.json).

Meme architecture que H1 (§2.1, CnnLstmClassifier) -- un tir MAST donne un
courant plasma, une serie temporelle brute, exactement la forme d'entree
que le classifieur attend, contrairement a H2/H3 qui demandent une
architecture spatiale differente (§2.2/§2.3, scripts separes).

Adaptation Helios (mêmes principes que pour H1, §2.1) :
- Fenetre de 60 points glissee (stride 5, comme a l'entrainement) sur la
  fenetre pre-quench (ou pre-fin-de-tir pour un tir stable) deja isolee
  par `detect_quench` -- meme logique que routers/fusion.py, reutilisee
  directement plutot que redupliquee.
- Chaque fenetre centree-reduite par SA PROPRE moyenne/ecart-type (le
  courant plasma en kA n'a aucun rapport d'echelle avec les quantites
  simulees vues a l'entrainement).
- Ensemble des 10 modeles deja entraines (§1.1), rechargé depuis les
  checkpoints, jamais ré-entraîné.

Calcul hors-ligne. Sortie : JSON dans
frontend/src/data/results/ia_vs_stats_real_fusion.json
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

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.connectors.mast import MastDataUnavailable, fetch_signal  # noqa: E402
from app.ml_benchmark import CnnLstmClassifier, build_dataset  # noqa: E402
from app.stats.quench import detect_quench  # noqa: E402

OUTPUT_PATH = (
    Path(__file__).resolve().parent.parent.parent
    / "frontend"
    / "src"
    / "data"
    / "results"
    / "ia_vs_stats_real_fusion.json"
)
CURATED_SHOTS_PATH = Path(__file__).resolve().parent.parent / "app" / "data" / "mast_shots.json"
CHECKPOINT_DIR = Path(__file__).resolve().parent.parent / "app" / "data" / "ia_vs_stats_ensemble"

WINDOW_LEN = 60
REAL_STRIDE = 5
N_SEEDS = 10
N_TRAIN_SADDLE = 10
N_TRAIN_KURAMOTO = 10
FIT_EPOCHS = 25
FIT_BATCH_SIZE = 256
TRAIN_SEED0_BASE = 10_000
MAX_ANALYSIS_POINTS = 400  # meme borne que routers/fusion.py


def train_or_load_ensemble() -> list[CnnLstmClassifier]:
    models = []
    all_checkpoints_exist = all((CHECKPOINT_DIR / f"seed_{i}.pt").exists() for i in range(N_SEEDS))
    if all_checkpoints_exist:
        print(f"  {N_SEEDS} checkpoints deja entraines trouves, rechargement...", flush=True)
        for seed_idx in range(N_SEEDS):
            cnn = CnnLstmClassifier(window_len=WINDOW_LEN, seed=seed_idx)
            cnn.load(str(CHECKPOINT_DIR / f"seed_{seed_idx}.pt"))
            models.append(cnn)
        return models

    print("  Aucun checkpoint complet trouve, entrainement depuis zero...", flush=True)
    for seed_idx in range(N_SEEDS):
        t0 = time.time()
        train_seed0 = TRAIN_SEED0_BASE + seed_idx * 1_000
        X_train, y_train = build_dataset(N_TRAIN_SADDLE, N_TRAIN_KURAMOTO, train_seed0, WINDOW_LEN, 5)
        cnn = CnnLstmClassifier(window_len=WINDOW_LEN, seed=seed_idx)
        losses = cnn.fit(X_train, y_train, epochs=FIT_EPOCHS, batch_size=FIT_BATCH_SIZE, seed=seed_idx)
        print(f"  modele {seed_idx} : loss {losses[0]:.4f} -> {losses[-1]:.4f} ({time.time()-t0:.1f}s)", flush=True)
        models.append(cnn)
    return models


def ensemble_predict(models: list[CnnLstmClassifier], windows: np.ndarray) -> np.ndarray:
    probs = np.stack([m.predict_proba(windows) for m in models])
    return probs.mean(axis=0)


def _fetch_current_signal(shot_id: int) -> tuple[np.ndarray, np.ndarray]:
    """Meme repli que routers/fusion.py : `amc/plasma_current` prefere a
    `efm/plasma_current_x` (reconstruction EFIT, echoue souvent au quench)."""
    try:
        return fetch_signal(shot_id, "amc", "time"), fetch_signal(shot_id, "amc", "plasma_current")
    except MastDataUnavailable:
        return fetch_signal(shot_id, "efm", "time"), fetch_signal(shot_id, "efm", "plasma_current_x")


def analyze_shot(shot_id: int, disrupted_published: bool, models: list[CnnLstmClassifier]) -> dict:
    try:
        time_arr, current = _fetch_current_signal(shot_id)
    except MastDataUnavailable as exc:
        return {"shot_id": shot_id, "error": str(exc)}

    quench = detect_quench(time_arr, current)
    if quench["t_peak"] is None:
        return {"shot_id": shot_id, "error": "pas de vrai courant plasma detecte"}

    cutoff = quench["t_quench"] if quench["disrupted"] else float(quench["time"][-1])
    pre_mask = quench["time"] < cutoff
    pre_current = pd.Series(quench["current"][pre_mask])
    if len(pre_current) > MAX_ANALYSIS_POINTS:
        pre_current = pre_current.iloc[-MAX_ANALYSIS_POINTS:].reset_index(drop=True)

    values = pre_current.to_numpy(dtype=np.float32)
    if len(values) < WINDOW_LEN + 4:
        return {"shot_id": shot_id, "error": f"fenetre pre-quench trop courte ({len(values)} points)"}

    window_ends = list(range(WINDOW_LEN, len(values) + 1, REAL_STRIDE))
    raw_windows = np.stack([values[end - WINDOW_LEN : end] for end in window_ends])
    means = raw_windows.mean(axis=1, keepdims=True)
    stds = raw_windows.std(axis=1, keepdims=True) + 1e-8
    normalized = (raw_windows - means) / stds

    probs = ensemble_predict(models, normalized)
    flags = probs > 0.5
    n_flagged = int(flags.sum())

    return {
        "shot_id": shot_id,
        "disrupted_published": disrupted_published,
        "n_windows": len(window_ends),
        "n_flagged": n_flagged,
        "flagged_fraction": round(n_flagged / len(window_ends), 4),
        "mean_probability": round(float(probs.mean()), 4),
        "max_probability": round(float(probs.max()), 4),
        "cnn_detects_anything": n_flagged > 0,
    }


async def main():
    t0 = time.time()
    print(f"=== Chargement de l'ensemble ({N_SEEDS} modeles, memes graines que §1) ===", flush=True)
    models = train_or_load_ensemble()

    shots_meta = json.loads(CURATED_SHOTS_PATH.read_text(encoding="utf-8"))["shots"]
    print(f"=== Analyse de la batterie MAST curatee ({len(shots_meta)} tirs) ===", flush=True)
    results = []
    for entry in shots_meta:
        r = analyze_shot(entry["shot_id"], entry["disrupted"], models)
        results.append(r)
        if "error" in r:
            print(f"  tir {entry['shot_id']} (disrupte={entry['disrupted']}): {r['error']}", flush=True)
        else:
            print(
                f"  tir {entry['shot_id']} (disrupte={entry['disrupted']}): {r['n_flagged']}/{r['n_windows']} "
                f"fenetres flaguees ({r['flagged_fraction']*100:.1f}%), proba moyenne={r['mean_probability']}",
                flush=True,
            )

    valid = [r for r in results if "error" not in r]
    disrupted = [r for r in valid if r["disrupted_published"]]
    stable = [r for r in valid if not r["disrupted_published"]]
    n_disrupted_flagged = sum(1 for r in disrupted if r["cnn_detects_anything"])
    n_stable_flagged = sum(1 for r in stable if r["cnn_detects_anything"])

    report = {
        "refreshedAt": date.today().isoformat(),
        "nSeeds": N_SEEDS,
        "windowLen": WINDOW_LEN,
        "stride": REAL_STRIDE,
        "shots": results,
        "summary": {
            "nShotsAnalyzed": len(valid),
            "nDisrupted": len(disrupted),
            "nStable": len(stable),
            "nDisruptedWithCnnFlag": n_disrupted_flagged,
            "nStableWithCnnFlag": n_stable_flagged,
        },
        "elapsedSeconds": round(time.time() - t0, 1),
    }
    OUTPUT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nDone in {report['elapsedSeconds']}s, written to {OUTPUT_PATH}", flush=True)
    print(f"Disruptes flagues par le CNN : {n_disrupted_flagged}/{len(disrupted)} -- Stables flagues (faux positifs potentiels) : {n_stable_flagged}/{len(stable)}", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
