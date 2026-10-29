"""Phase 1c du banc Dansgaard-Oeschger : applique le critère figé dans docs/vulnerabilite/phase_1c_criteres.md (étiquette `phase1c-criteres-v1`).

Usage (depuis backend/) :  python -m scripts.vulnerabilite_phase_1c

AUCUNE donnée réelle. Écrit docs/vulnerabilite/phase_1c_resultats.json et phase_1c_resultats.md.
"""
from __future__ import annotations

import json
import sys
import time
import warnings
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr

from app.vulnerabilite.derive_cubique import v_etoile_fenetre
from app.vulnerabilite.simulation import barriere_double_puits, simuler_double_puits

DEPOT = Path(__file__).resolve().parents[2]
GRAINE = 20261028
SIGMAS = (0.55, 0.65)
TAILLES = (100, 200, 400)
N_SERIES = 30
N_POINTS = 2400
PAS_FENETRE = 50
SEUIL_RHO, PART_SERIES, PART_FINI, BORNES_RAPPORT = 0.5, 0.90, 0.70, (0.5, 1.5)


def bascules(x: np.ndarray) -> np.ndarray:
    """Indices des changements d'état (x < −0,3 ↔ x > 0,3), avec hystérésis, dans les deux sens."""
    etat, sortie = (-1 if x[0] < 0 else 1), []
    for i, v in enumerate(x):
        if etat < 0 and v > 0.3:
            etat = 1
            sortie.append(i)
        elif etat > 0 and v < -0.3:
            etat = -1
            sortie.append(i)
    return np.array(sortie)


def serie(sigma: float, rng: np.random.Generator, taille: int) -> dict:
    x, O, h = simuler_double_puits(sigma, N_POINTS, rng)
    x, h = x[:, 0], h[:, 0]
    evts = bascules(x)
    lignes = []
    for debut in range(0, N_POINTS - taille, PAS_FENETRE):
        fin = debut + taille
        suivants = evts[evts >= fin]
        if not len(suivants):
            continue
        v_est = v_etoile_fenetre(O[:, debut:fin, :])
        v_vrai = barriere_double_puits(h[fin - 1], sigma, float(np.mean(x[fin - 5:fin])))
        w = x[debut:fin]
        lignes.append((v_est, v_vrai, np.corrcoef(w[:-1], w[1:])[0, 1], np.var(w), np.log(suivants[0] - fin + 1)))
    return {"n_bascules": int(len(evts)), "lignes": np.array(lignes) if lignes else np.empty((0, 5))}


def evaluer(series: list[dict]) -> dict:
    rhos, rhos_ac, rhos_var, n_fen, n_fini, rapports = [], [], [], 0, 0, []
    for s in series:
        L = s["lignes"]
        if not len(L):
            rhos.append(np.nan)
            continue
        fini = np.isfinite(L[:, 0])
        n_fen += len(L)
        n_fini += int(fini.sum())
        ok = np.isfinite(L[:, 0]) & np.isfinite(L[:, 1]) & (L[:, 1] > 0)
        rapports += list(L[ok, 0] / L[ok, 1])
        rhos.append(spearmanr(L[fini, 0], L[fini, 4])[0] if fini.sum() >= 8 and np.ptp(L[fini, 0]) > 0 else np.nan)
        rhos_ac.append(spearmanr(L[:, 2], L[:, 4])[0])
        rhos_var.append(spearmanr(L[:, 3], L[:, 4])[0])
    rhos = np.array(rhos)
    part_series = float(np.mean(np.where(np.isfinite(rhos), rhos >= SEUIL_RHO, False)))
    part_fini = n_fini / n_fen if n_fen else 0.0
    rapport = float(np.median(rapports)) if rapports else float("nan")
    return {
        "part_series_rho_ge_0_5": part_series, "rho_median": float(np.nanmedian(rhos)) if np.isfinite(rhos).any() else float("nan"),
        "part_fenetres_v_fini": part_fini, "rapport_median_est_sur_vrai": rapport, "n_fenetres": n_fen,
        "rho_ac1_median": float(np.nanmedian(rhos_ac)), "rho_variance_median": float(np.nanmedian(rhos_var)),
        "c1_correlation": part_series >= PART_SERIES, "c2_estimabilite": part_fini >= PART_FINI,
        "c3_exactitude": bool(np.isfinite(rapport) and BORNES_RAPPORT[0] <= rapport <= BORNES_RAPPORT[1]),
    }


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    warnings.simplefilter("ignore")
    rng = np.random.default_rng(GRAINE)
    resultats = {}
    t0 = time.time()
    for sigma in SIGMAS:
        for taille in TAILLES:
            series = []
            rng_local = np.random.default_rng([GRAINE, int(sigma * 100), taille])  # un flux par combinaison : résultats indépendants de l'ordre d'exécution
            for _ in range(N_SERIES):
                series.append(serie(sigma, rng_local, taille))
            e = evaluer(series)
            e["n_bascules_moyen"] = float(np.mean([s["n_bascules"] for s in series]))
            e["reussi"] = bool(e["c1_correlation"] and e["c2_estimabilite"] and e["c3_exactitude"])
            resultats[f"sigma_{sigma}_fenetre_{taille}"] = e
            print(f"σ={sigma} fenêtre={taille} : séries ρ≥0,5 {e['part_series_rho_ge_0_5']:.0%} (ρ médian {e['rho_median']:.2f}) ; V* fini {e['part_fenetres_v_fini']:.0%} ; "
                  f"rapport médian {e['rapport_median_est_sur_vrai']:.2f} ; AC1 {e['rho_ac1_median']:+.2f}, variance {e['rho_variance_median']:+.2f} -> {'RÉUSSI' if e['reussi'] else 'échec'} ({time.time() - t0:.0f} s)", flush=True)
    passe = any(r["reussi"] for r in resultats.values())
    sortie = {"graine": GRAINE, "criteres": {"rho": SEUIL_RHO, "part_series": PART_SERIES, "part_fini": PART_FINI, "rapport": BORNES_RAPPORT}, "combinaisons": resultats, "passage_aux_donnees_reelles": passe}
    (DEPOT / "docs" / "vulnerabilite" / "phase_1c_resultats.json").write_text(json.dumps(sortie, ensure_ascii=False, indent=2), encoding="utf-8")
    lignes = ["| σ | Fenêtre (points) | Bascules par série | Séries avec ρ ≥ 0,5 | ρ médian | V\\* fini | Rapport médian V\\* estimé / vrai | ρ AC1 | ρ variance | Réussi |", "|---|---|---|---|---|---|---|---|---|---|"]
    for cle, e in resultats.items():
        _, s, _, t = cle.split("_")
        lignes.append(f"| {s} | {t} | {e['n_bascules_moyen']:.1f} | {e['part_series_rho_ge_0_5']:.0%} | {e['rho_median']:.2f} | {e['part_fenetres_v_fini']:.0%} | {e['rapport_median_est_sur_vrai']:.2f} | "
                      f"{e['rho_ac1_median']:+.2f} | {e['rho_variance_median']:+.2f} | {'oui' if e['reussi'] else 'non'} |")
    (DEPOT / "docs" / "vulnerabilite" / "phase_1c_resultats.md").write_text("\n".join(lignes) + "\n", encoding="utf-8")
    print("\nPASSAGE AUX DONNÉES RÉELLES :", "OUI" if passe else "NON (arrêt)")


if __name__ == "__main__":
    main()
