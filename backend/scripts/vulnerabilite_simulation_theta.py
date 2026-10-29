"""Simulation (aucune donnée réelle) : quelles violations de l'hypothèse 2 donnent un taux de détection estimé hors de ]0 ; 1[ ?

Usage (depuis backend/) :  python -m scripts.vulnerabilite_simulation_theta > ../docs/vulnerabilite/simulation_theta.md

37 départements × 105 semaines, trois vagues nationales, tailles de 40 à 300 ; urgences (taux vrai 0,4) et SOS Médecins (0,6) ; 100 répétitions par scénario.
Compare l'estimateur regroupé de la proposition 8 (valable pour des unités identiques) et l'estimateur intra-unité (moments dans chaque unité, puis sommés).
"""
from __future__ import annotations

import sys

import numpy as np

from app.vulnerabilite.multicanal import taux_detection, taux_detection_intra_unite

T, N, REPETITIONS, GRAINE = 105, 37, 100, 20261018


def vrai(rng, R=0.8, amplitude=4.0):
    t = np.arange(T)
    vague = sum(np.exp(-0.5 * ((t - c) / 5.0) ** 2) for c in (14, 45, 80))
    taille = np.exp(rng.uniform(np.log(40), np.log(300), N))
    y = taille.copy()
    v = np.zeros((T, N))
    for i in range(T):
        y = rng.poisson(taille * (1 + amplitude * vague[i]) * (1 - R) + R * y).astype(float)
        v[i] = y
    return v.astype(int)


def binom(rng, v, p):
    return rng.binomial(v, np.clip(p, 0, 1)).astype(float)


SCENARIOS = {
    "Taux constants et indépendants": lambda rng, v: (binom(rng, v, 0.4), binom(rng, v, 0.6)),
    "Taux propre à chaque département (0,2 à 0,8)": lambda rng, v: (binom(rng, v, rng.uniform(0.2, 0.8, N)), binom(rng, v, rng.uniform(0.2, 0.8, N))),
    "Taux de SOS en baisse de 50 % dans le temps": lambda rng, v: (binom(rng, v, 0.4), binom(rng, v, 0.6 * np.linspace(1, 0.5, T)[:, None])),
    "50 % des patients SOS passent ensuite aux urgences": lambda rng, v: (lambda s: (binom(rng, v, 0.4) + binom(rng, s.astype(int), 0.5), s))(binom(rng, v, 0.6)),
    "90 % des patients SOS passent ensuite aux urgences": lambda rng, v: (lambda s: (binom(rng, v, 0.4) + binom(rng, s.astype(int), 0.9), s))(binom(rng, v, 0.6)),
}
for sd in (0.15, 0.3):
    SCENARIOS[f"Facteur de codage hebdomadaire commun au pays (écart-type {int(100 * sd)} %)"] = (
        lambda sd: lambda rng, v: (lambda c: (binom(rng, v, 0.4 * c), binom(rng, v, 0.6 * c)))(np.exp(rng.normal(0, sd, T) - sd * sd / 2)[:, None]))(sd)
for sd in (0.15, 0.3):
    SCENARIOS[f"Facteur de codage propre à chaque département-semaine (écart-type {int(100 * sd)} %)"] = (
        lambda sd: lambda rng, v: (lambda c: (binom(rng, v, 0.4 * c), binom(rng, v, 0.6 * c)))(np.exp(rng.normal(0, sd, (T, N)) - sd * sd / 2)))(sd)


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    rng = np.random.default_rng(GRAINE)
    print("| Scénario simulé | θ̄ intra-unité, urgences (vrai 0,4) : médiane [5ᵉ ; 95ᵉ centile] | θ̂ regroupé, urgences : médiane | θ̄ intra-unité, SOS (vrai 0,6) : médiane |")
    print("|---|---|---|---|")
    for nom, fabrique in SCENARIOS.items():
        ti, tr, ts = [], [], []
        for _ in range(REPETITIONS):
            ou, os_ = fabrique(rng, vrai(rng))
            ti.append(taux_detection_intra_unite(ou, os_))
            ts.append(taux_detection_intra_unite(os_, ou))
            tr.append(taux_detection(ou, os_))
        q = np.percentile(ti, [5, 50, 95])
        print(f"| {nom} | {q[1]:.2f} [{q[0]:.2f} ; {q[2]:.2f}] | {np.median(tr):.2f} | {np.median(ts):.2f} |")


if __name__ == "__main__":
    main()
