"""§2.1 du cahier des charges "banc d'essai IA vs statistiques" : applique le
classifieur entraine sur les modeles SIMULES (nœud-col, Kuramoto) aux memes
episodes REELS deja utilises pour H1, et compare son verdict a celui deja
publie pour l'indicateur statistique (H1_PHENOMENA).

Question posee, dans les deux sens honnetement : un classifieur qui a appris
une signature dynamique sur des modeles simules generalise-t-il a une serie
sociale reelle (attention Wikipedia) -- ou est-ce que la difference de
domaine (echelle, bruit, nature du signal) le rend inutilisable tel quel ?
Aucune reponse presumee avant le calcul.

Adaptation Helios (differences honnetement documentees par rapport au
protocole sur donnees simulees, necessaires par la nature meme des donnees
reelles) :
- Le CNN attend une fenetre de 60 points DEJA a l'echelle des series
  d'entrainement (normalisees par la moyenne/ecart-type GLOBAL du jeu
  d'entrainement). Une serie Wikipedia (des dizaines de milliers de vues/jour)
  n'a evidemment pas cette echelle -- chaque fenetre de 60 jours est donc
  centree-reduite par SA PROPRE moyenne/ecart-type avant d'etre presentee au
  reseau, pour lui donner une chance de reconnaitre une FORME plutot qu'une
  valeur absolue hors de son domaine d'entrainement.
- Stride de 1 jour (pas 5 comme sur les trajectoires simulees) : les series
  reelles sont bien plus courtes (136 a 944 jours contre 7500 pas simules),
  un stride de 5 donnerait trop peu de fenetres pour un phenomene court.
- Pas de filtre de persistance (§ CONSECUTIVE_REQUIRED sur donnees simulees) :
  calibrer un tel filtre pour des fenetres quotidiennes tres chevauchantes
  demanderait son propre travail de calibration, non fait ici -- le taux de
  fenetres individuellement positives est rapporte tel quel, sans lissage.
- Ensemble des 10 modeles CNN-LSTM entraines ici (§1.1, architecture adaptee
  de Bury et al.) plutot qu'un seul : probabilite moyenne des 10 seeds pour
  le verdict par fenetre -- coherent avec la logique d'ensemble de Bury et
  al. eux-memes, reprise pour tout le banc d'essai.

Calcul hors-ligne. Sortie : JSON dans
frontend/src/data/results/ia_vs_stats_real_h1.json
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

from app.connectors.wikipedia import WikipediaPageviewsConnector  # noqa: E402
from app.ml_benchmark import CnnLstmClassifier, build_dataset  # noqa: E402
from app.phenomena import PHENOMENA  # noqa: E402

OUTPUT_PATH = (
    Path(__file__).resolve().parent.parent.parent
    / "frontend"
    / "src"
    / "data"
    / "results"
    / "ia_vs_stats_real_h1.json"
)

WINDOW_LEN = 60
REAL_STRIDE = 1
N_SEEDS = 10
N_TRAIN_SADDLE = 10
N_TRAIN_KURAMOTO = 10
FIT_EPOCHS = 25
FIT_BATCH_SIZE = 256
TRAIN_SEED0_BASE = 10_000  # memes graines que le run principal (§1), pour rejouer les memes modeles

# Verdict H1 deja publie (nSocSig/nSoc, outcome) -- frontend/src/data/results/h1.json,
# recopie ici pour comparaison sans dependre du frontend depuis un script backend.
H1_PUBLISHED = {
    "gilets_jaunes_2018": {"n_soc_sig": 3, "n_soc": 3, "outcome": "against"},
    "confinement_2020": {"n_soc_sig": 0, "n_soc": 3, "outcome": "against"},
    "chomage_recent": {"n_soc_sig": 1, "n_soc": 3, "outcome": "against"},
    "attentats_2015": {"n_soc_sig": 2, "n_soc": 3, "outcome": "favorable"},
    "reforme_retraites_2023": {"n_soc_sig": 2, "n_soc": 3, "outcome": "against"},
    "attentat_nice_2016": {"n_soc_sig": 2, "n_soc": 3, "outcome": "against"},
}


CHECKPOINT_DIR = Path(__file__).resolve().parent.parent / "app" / "data" / "ia_vs_stats_ensemble"


def train_ensemble() -> list[CnnLstmClassifier]:
    """Recharge les 10 modeles deja entraines par train_and_compare_classifier.py
    (§1.1) si leurs checkpoints existent -- evite un second entrainement complet
    (~40 minutes) pour rejouer exactement le meme ensemble sur les donnees reelles.
    Sinon, entraine depuis zero (memes graines/hyperparametres)."""
    models = []
    all_checkpoints_exist = all((CHECKPOINT_DIR / f"seed_{i}.pt").exists() for i in range(N_SEEDS))
    if all_checkpoints_exist:
        print(f"  {N_SEEDS} checkpoints deja entraines trouves ({CHECKPOINT_DIR}), rechargement...", flush=True)
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
    """Probabilite moyenne des N_SEEDS modeles sur un lot de fenetres deja normalisees."""
    probs = np.stack([m.predict_proba(windows) for m in models])
    return probs.mean(axis=0)


async def analyze_phenomenon(key: str, models: list[CnnLstmClassifier], wiki: WikipediaPageviewsConnector) -> dict:
    spec = PHENOMENA[key]
    combined = await wiki.fetch_combined(spec["wiki_articles"], spec["start"], spec["end"])
    if combined.empty or len(combined) < WINDOW_LEN + 4:
        return {"key": key, "label": spec["label"], "error": f"Serie sociale trop courte ({len(combined)} points)."}

    dates = combined["date"].dt.strftime("%Y-%m-%d").tolist()
    values = combined["valeur"].to_numpy(dtype=np.float32)

    window_ends = list(range(WINDOW_LEN, len(values) + 1, REAL_STRIDE))
    raw_windows = np.stack([values[end - WINDOW_LEN : end] for end in window_ends])
    # Centrage-reduction PAR FENETRE (voir docstring du module) -- chaque fenetre
    # a sa propre moyenne/ecart-type, contrairement a la normalisation globale
    # du jeu d'entrainement synthetique.
    means = raw_windows.mean(axis=1, keepdims=True)
    stds = raw_windows.std(axis=1, keepdims=True) + 1e-8
    normalized = (raw_windows - means) / stds

    probs = ensemble_predict(models, normalized)
    flags = probs > 0.5
    n_flagged = int(flags.sum())
    flagged_dates = [dates[window_ends[i] - 1] for i in range(len(flags)) if flags[i]]

    published = H1_PUBLISHED.get(key)

    return {
        "key": key,
        "label": spec["label"],
        "n_windows": len(window_ends),
        "n_flagged": n_flagged,
        "flagged_fraction": round(n_flagged / len(window_ends), 4),
        "first_flagged_date": flagged_dates[0] if flagged_dates else None,
        "last_flagged_date": flagged_dates[-1] if flagged_dates else None,
        "mean_probability": round(float(probs.mean()), 4),
        "max_probability": round(float(probs.max()), 4),
        "cnn_detects_anything": n_flagged > 0,
        "h1_published": published,
    }


async def main():
    t0 = time.time()
    print(f"=== Entrainement de l'ensemble ({N_SEEDS} modeles, memes graines que §1) ===", flush=True)
    models = train_ensemble()

    print("=== Analyse des episodes reels de H1 (attention Wikipedia) ===", flush=True)
    wiki = WikipediaPageviewsConnector()
    results = []
    for key in PHENOMENA:
        r = await analyze_phenomenon(key, models, wiki)
        results.append(r)
        if "error" in r:
            print(f"  {key}: {r['error']}", flush=True)
        else:
            print(
                f"  {key}: {r['n_flagged']}/{r['n_windows']} fenetres flaguees "
                f"({r['flagged_fraction']*100:.1f}%), proba moyenne={r['mean_probability']}, "
                f"H1 publie: {r['h1_published']}",
                flush=True,
            )

    report = {
        "refreshedAt": date.today().isoformat(),
        "nSeeds": N_SEEDS,
        "windowLen": WINDOW_LEN,
        "stride": REAL_STRIDE,
        "phenomena": results,
        "elapsedSeconds": round(time.time() - t0, 1),
    }
    OUTPUT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nDone in {report['elapsedSeconds']}s, written to {OUTPUT_PATH}", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
