"""Usage (depuis backend/) :  python -m scripts.vulnerabilite_phase_1c_plafond

Plafond du critère de corrélation : corrélation de rang entre le V* VRAI (barrière exacte) et ln du temps d'attente, mêmes séries simulées que la phase 1c
(mêmes graines ; l'estimateur ne consomme aucun tirage). Aucune donnée réelle."""
import numpy as np
from scipy.stats import spearmanr

from app.vulnerabilite.simulation import barriere_double_puits, simuler_double_puits
from scripts.vulnerabilite_phase_1c import GRAINE, N_POINTS, N_SERIES, PAS_FENETRE, SIGMAS, TAILLES, bascules

def main() -> None:
    for sigma in SIGMAS:
        for taille in TAILLES:
            rng = np.random.default_rng([GRAINE, int(sigma * 100), taille])
            rhos, sdv = [], []
            for _ in range(N_SERIES):
                x, O, h = simuler_double_puits(sigma, N_POINTS, rng)
                x, h = x[:, 0], h[:, 0]
                evts = bascules(x)
                v, w = [], []
                for debut in range(0, N_POINTS - taille, PAS_FENETRE):
                    fin = debut + taille
                    suiv = evts[evts >= fin]
                    if not len(suiv):
                        continue
                    vv = barriere_double_puits(h[fin - 1], sigma, float(np.mean(x[fin - 5:fin])))
                    if np.isfinite(vv):
                        v.append(vv)
                        w.append(np.log(suiv[0] - fin + 1))
                if len(v) >= 8 and np.ptp(v) > 0:
                    rhos.append(spearmanr(v, w)[0])
                    sdv.append(np.std(v))
            rhos = np.array(rhos)
            print(f"σ={sigma} fenêtre={taille} : ρ(V* VRAI, ln attente) médian {np.median(rhos):+.2f} ; part des séries ≥ 0,5 : {np.mean(rhos >= 0.5):.0%} ; écart-type de V* vrai {np.median(sdv):.2f}")


if __name__ == "__main__":
    main()
