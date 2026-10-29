"""Étude de faisabilité par simulation (AUCUNE donnée réelle) pour un banc de type Dansgaard-Oeschger :
une seule série longue (≈ 2 400 points de 20 ans), deux capteurs affines, bascules induites par le bruit entre deux états.
Question : l'estimateur de V* à deux capteurs (proposition 14, estimé sur fenêtres glissantes) peut-il renseigner sur le temps d'attente avant la bascule suivante ?

Usage (depuis backend/) :  python -m scripts.vulnerabilite_faisabilite_do
"""
from __future__ import annotations

import sys
import warnings

import numpy as np
from scipy.stats import spearmanr

from app.vulnerabilite import multicanal as mc

PAS = 20  # années par point observé
N_POINTS = 2400  # 48 000 ans
SOUS_PAS = 20  # sous-pas d'intégration par point observé


def simuler(rng, sigma=0.65, derive_h=0.15, bruit_mesure=0.25, gains=(1.0, 0.7), decalages=(0.0, 0.3)):
    """Double puits dx = (x − x³ + h(t)) dt + σ dW ; l'observation est faite tous les 0,2 unités de temps (= 20 ans) ; h(t) = condition aux limites lente."""
    dt = 0.2 / SOUS_PAS
    t = np.arange(N_POINTS * SOUS_PAS) * dt
    h = derive_h * np.sin(2 * np.pi * t / 120.0 + rng.uniform(0, 2 * np.pi))
    x = np.empty(N_POINTS * SOUS_PAS)
    x[0] = -1.0
    bruit = rng.standard_normal(len(x)) * sigma * np.sqrt(dt)
    for i in range(1, len(x)):
        x[i] = x[i - 1] + (x[i - 1] - x[i - 1] ** 3 + h[i - 1]) * dt + bruit[i]
    obs = x[SOUS_PAS - 1::SOUS_PAS]
    O = np.stack([g * obs + b + g * bruit_mesure * rng.standard_normal(N_POINTS) for g, b in zip(gains, decalages)])
    return obs, O


def bascules(obs):
    """Indices des passages de l'état froid (x < −0,3) à l'état chaud (x > 0,3), avec hystérésis."""
    etat, sortie = -1, []
    for i, v in enumerate(obs):
        if etat < 0 and v > 0.3:
            etat = 1
            sortie.append(i)
        elif etat > 0 and v < -0.3:
            etat = -1
    return sortie


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    warnings.simplefilter("ignore")
    rng = np.random.default_rng(20261018)
    taille = 100  # points par fenêtre (2 000 ans)
    lignes = []
    n_total = n_estimables = 0
    for graine in range(4):
        obs, O = simuler(rng)
        evts = np.array(bascules(obs))
        for debut in range(0, N_POINTS - taille - 1, 25):
            fin = debut + taille
            suivants = evts[evts > fin]
            if not len(suivants):
                continue
            n_total += 1
            Ow = O[:, debut:fin, None]
            try:
                v = mc.estimer_vstar_deux_capteurs(Ow, 0, 1)
            except (ValueError, np.linalg.LinAlgError):
                v = np.nan
            x = obs[debut:fin]
            ac1 = np.corrcoef(x[:-1], x[1:])[0, 1]
            n_estimables += int(np.isfinite(v) and v < 99)
            lignes.append((v, ac1, np.var(x), np.log(suivants[0] - fin + 1)))
    L = np.array(lignes)
    print(f"{len(evts)} bascules dans la dernière série ; {n_total} fenêtres ; V* estimable (fini) dans {n_estimables} ({n_estimables / n_total:.0%})")
    ok = np.isfinite(L[:, 0]) & (L[:, 0] < 99)
    for nom, j in (("V* à deux capteurs", 0), ("AC1", 1), ("variance", 2)):
        m = ok if j == 0 else np.ones(len(L), bool)
        r = spearmanr(L[m, j], L[m, 3])[0]
        print(f"Spearman({nom}, ln temps avant la bascule suivante) = {r:+.2f}  (n = {m.sum()})")
    print("Médiane de V* estimé :", np.nanmedian(L[ok, 0]) if ok.any() else "—", "| attendu de l'ordre de la barrière ΔU/(σ²/2) =", round(0.25 / (0.65**2 / 2), 2))


if __name__ == "__main__":
    main()
