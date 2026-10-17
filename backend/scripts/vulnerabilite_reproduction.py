"""Recalcule avec le module `app.vulnerabilite` les chiffres clés de la note « Vulnérabilité d'une contagion sociale »
(v3.1) et écrit un tableau Markdown : valeur de la note, valeur du module, tolérance du cahier des charges.

Usage (depuis backend/) :  python -m scripts.vulnerabilite_reproduction > ../docs/vulnerabilite/reproduction_tableau.md

Durée : environ 10 minutes (simulations Monte-Carlo, 147 V* exacts, bootstrap). Graines identiques à celles des
scripts de la note ; les résultats sont donc comparables ligne à ligne. Aucun appel réseau.
"""
from __future__ import annotations

import sys
import time

import numpy as np
from scipy.integrate import quad

from app.vulnerabilite import estimation as est
from app.vulnerabilite import modele as m
from app.vulnerabilite import multicanal as mc
from app.vulnerabilite.bruits import BinomialeNegative
from app.vulnerabilite.incertitude import bootstrap_unites
from app.vulnerabilite.observation import CanauxAmincis, CapteursAffines
from app.vulnerabilite.reaction import decomposer_reaction
from app.vulnerabilite.simulation import (
    couper_avant_embrasement,
    simuler_gaussien_capteurs,
    simuler_multicanal,
    simuler_reaction,
    simuler_societe_chocs_communs,
    simuler_unites,
    temps_avant_embrasement,
    temps_avant_embrasement_gaussien,
)
from app.vulnerabilite.vstar import temps_moyen_exact_poisson, vstar_gaussien, vstar_poisson

R0, ML = 0.6, 3.0
LIGNES: list[tuple[str, str, str, str]] = []


def ligne(nom: str, note: str, module: str, tolerance: str) -> None:
    LIGNES.append((nom, note, module, tolerance))
    print(f"| {nom} | {note} | {module} | {tolerance} |", flush=True)


def societe(c, N, T, graine):
    a, mu, _, mp = m.params_depuis_inflammabilite(R0, c, ML)
    return couper_avant_embrasement(simuler_unites(a, mu, c, N, T, np.random.default_rng(graine), y0=ML), mp, 5)


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    debut = time.time()
    print("| Test | Note (v3.1) | Module | Tolérance du cahier |")
    print("|---|---|---|---|")

    # Φ forme close
    a, mu, _, _ = m.params_depuis_inflammabilite(R0, 0.02, ML)
    ligne("Φ, R=0,6 c=0,02 m₋=3 : forme close / intégrale numérique", "4,78", f"{m.phi_poisson(R0, 0.02, ML):.6f} / {m.phi_numerique(a, mu, 0.02):.6f}", "1e-6")

    # cécité
    ac1, fano = [], []
    for c in (0.01, 0.02, 0.03):
        a, mu, _, mp = m.params_depuis_inflammabilite(R0, c, ML)
        X = simuler_unites(a, mu, c, 3000, 150, np.random.default_rng(1), y0=ML)
        Z = X[50:, ~(X >= mp).any(axis=0)]
        ac1.append(np.mean([np.corrcoef(z[:-1], z[1:])[0, 1] for z in Z.T[:500]]))
        fano.append(np.mean(Z.var(axis=0) / Z.mean(axis=0)))
    ligne("Cécité : AC1 pour c = 0,01 / 0,02 / 0,03 (R=0,6)", "0,58 / 0,61 / 0,60", " / ".join(f"{v:.2f}" for v in ac1), "0,60 ± 0,04")
    ligne("Cécité : dispersion (variance/moyenne) pour les mêmes c", "1,56 / 1,67 / 1,62 (théorie 1,56)", " / ".join(f"{v:.2f}" for v in fano), "identiques entre eux")

    # estimation 100x200
    for c, nom_note in ((0.01, "11,0"), (0.02, "5,0"), (0.03, "3,9")):
        v = [min(est.ajuster(societe(c, 100, 200, r * 7 + int(c * 1000) + 300)).phi, 99) for r in range(100)]
        ligne(f"Estimation 100×200 : Φ̂ médian, Φ = {m.phi_poisson(R0, c, ML):.2f}", nom_note, f"{np.median(v):.2f}", "± 15 % (Φ = 11,5 et 4,8)")

    # coupure
    for c in (0.01, 0.02, 0.03):
        a, mu, _, _ = m.params_depuis_inflammabilite(R0, c, ML)
        for k, note in ((4, {0.01: "35,1", 0.02: "9,6", 0.03: "5,2"}), (6, {0.01: "12,5", 0.02: "4,9", 0.03: "2,8"})):
            v = [est.ajuster(est.couper_au_premier_depassement(simuler_unites(a, mu, c, 100, 200, np.random.default_rng(r), y0=ML), k * ML)).phi for r in range(100)]
            ligne(f"Coupure à {k} × niveau calme : Φ̂ médian, Φ = {m.phi_poisson(R0, c, ML):.2f}", note[c], f"{np.median(v):.2f}", "4× : > 1,5 Φ ; 6× : ± 10 %")

    # chocs communs
    avec, sans = [], []
    for i in range(30):
        X = simuler_societe_chocs_communs(0.6, np.random.default_rng(i))
        avec.append(min(est.ajuster_effets_temporels(X[240:300]).phi, 30))
        sans.append(min(est.ajuster(X[240:300]).phi, 30))
    ligne("Chocs communs croissants (Φ = 11,5) : Φ̂ avec effets fixes temporels", "11,3", f"{np.median(avec):.2f}", "± 20 %")
    ligne("Chocs communs croissants : Φ̂ sans effets fixes (plafonné à 30)", "> 30", f"{np.median(sans):.2f}", "—")

    # croisé linéaire
    res = {"naif1": [], "naif2": [], "c21": [], "c12": []}
    for i in range(50):
        obs = CanauxAmincis((0.3, 0.4), canal_sous_boucle=0, intensite_boucle=0.5, forme_boucle="lineaire")
        O = simuler_multicanal(0.6, 1.2, 0.0, 100, 200, np.random.default_rng(i), obs, y0=3.0)[1]
        res["naif1"].append(mc.pente_naive(O[0], O[0]))
        res["naif2"].append(mc.pente_naive(O[1], O[1]))
        res["c21"].append(mc.pente_croisee(O[1], O[0]))
        res["c12"].append(mc.pente_croisee(O[0], O[1]))
    md = {k: np.median(v) for k, v in res.items()}
    ligne("Estimateur croisé, cas linéaire, boucle η=0,5 : croisé 2←1 / croisé 1←2", "0,60 / 0,83", f"{md['c21']:.2f} / {md['c12']:.2f}", "0,60 ± 0,03")
    ligne("Même cas : R̂ naïf du canal sous boucle / du canal indépendant", "0,71 / 0,31", f"{md['naif1']:.2f} / {md['naif2']:.2f}", "naïf ≈ 0,71")

    # multicanal quadratique
    c = 0.006
    a, mu, _, mp = m.params_depuis_inflammabilite(R0, c, 20.0)
    out = {"naïf": [], "2 canaux": [], "3 canaux (instr. 1)": [], "3 canaux (instr. 3)": []}
    for eta in (0.0, 1.0):
        for k in out:
            out[k] = []
        for i in range(40):
            obs = CanauxAmincis((0.4, 0.5, 0.6), canal_sous_boucle=0, intensite_boucle=eta, forme_boucle="centree", niveau_reference=20.0)
            O = simuler_multicanal(a, mu, c, 100, 200, np.random.default_rng(i), obs, y0=20.0, m_haut=mp)[1]
            out["naïf"].append(min(est.ajuster(O[1]).phi, 99))
            out["2 canaux"].append(min(mc.estimer_multicanal(O, 1, 0, 0).phi, 99))
            out["3 canaux (instr. 1)"].append(min(mc.estimer_multicanal(O, 1, 0, 2).phi, 99))
            out["3 canaux (instr. 3)"].append(min(mc.estimer_multicanal(O, 1, 2, 2).phi, 99))
        note = {0.0: ("35,8", "12,8", "12,7", "11,5"), 1.0: ("36,7", "4,4", "10,5", "11,5")}[eta]
        ligne(f"Multicanal quadratique, Φ = 12,17, boucle η={eta:g} : naïf / 2 canaux / 3 canaux instr. 1 / instr. 3", " / ".join(note),
              " / ".join(f"{np.median(out[k]):.1f}" for k in out), "instr. 3 : 11,5 ± 20 %")

    # dispersion
    for dispersion, note in ((1.0, "1,00"), (2.0, "2,00"), (4.0, "3,78")):
        bruit = None if dispersion == 1.0 else BinomialeNegative(dispersion)
        a, mu, _, mp = m.params_depuis_inflammabilite(0.6, 0.008, 20.0)
        v = []
        for i in range(30):
            O = simuler_multicanal(a, mu, 0.008, 100, 200, np.random.default_rng(100 * i + 8 + int(dispersion)), CanauxAmincis((0.5, 0.6)), bruit=bruit, y0=20.0, m_haut=mp)[1]
            v.append(mc.estimer_deux_canaux_avec_dispersion(O).dispersion)
        ligne(f"Dispersion φ = {dispersion:g} : φ̂ médian (deux canaux)", note, f"{np.median(v):.2f}", "1 et 2 : ± 0,1")

    # réaction
    for nom, (a_, k_, r_, m_), note in (("Réaction : société explosive tenue (A / a)", (1.05, 0.02, 0.2, 2.0), "0,82 / 1,03"),):
        d = [decomposer_reaction(simuler_reaction(a_, k_, r_, m_, 100, 400, np.random.default_rng(i))[0]) for i in range(20)]
        ligne(nom, note, f"{np.median([x.A for x in d]):.2f} / {np.median([x.a for x in d]):.2f}", "± 0,05")

    # bootstrap
    a, mu, _, _ = m.params_depuis_inflammabilite(R0, 0.02, ML)
    couvre = []
    for i in range(60):
        rng = np.random.default_rng(1000 + i)
        X = est.couper_au_premier_depassement(simuler_unites(a, mu, 0.02, 100, 200, rng, y0=ML), 6 * ML)
        iv = bootstrap_unites(X, lambda Z: est.ajuster(Z).phi, 200, rng)
        couvre.append(iv.bas <= m.phi_poisson(R0, 0.02, ML) <= iv.haut)
    ligne("Bootstrap par unités, 100×200 : couverture de l'intervalle à 90 %", "90 %", f"{100 * np.mean(couvre):.0f} %", "82–97 %")

    # loi des temps
    lignes = []
    for R in (0.4, 0.6, 0.8):
        for ml in (1.0, 3.0, 8.0):
            for c in np.geomspace(0.01, 0.5, 12):
                try:
                    phi = m.phi_poisson(R, c, ml)
                except ValueError:
                    continue
                if not 1.0 < phi < 11.0:
                    continue
                T = temps_avant_embrasement(R, c, ml, n=300, t_max=150_000, seed=int(1000 * c + 10 * R + ml))
                if np.isnan(T).mean() > 0.05:
                    continue
                lignes.append((phi, np.log(np.nanmean(T))))
    phi_, lnt = np.array(lignes).T
    ligne("Loi des temps : pente de ln E[T] en Φ (nombre de jeux, corrélation)", "1,04 (22, 0,92)", f"{np.polyfit(phi_, lnt, 1)[0]:.2f} ({len(lignes)}, {np.corrcoef(phi_, lnt)[0, 1]:.2f})", "0,8–1,3")

    # V* Poisson
    lignes = []
    for R in (0.3, 0.5, 0.6, 0.7, 0.8):
        for ml in (2.0, 4.0, 8.0, 15.0):
            for c in np.geomspace(0.003, 0.3, 18):
                try:
                    a, mu, _, mp = m.params_depuis_inflammabilite(R, c, ml)
                except ValueError:
                    continue
                if mu <= 0 or mp > 400 or not 0.5 < m.phi_poisson(R, c, ml) < 25:
                    continue
                lignes.append((R, vstar_poisson(a, mu, c), np.log(temps_moyen_exact_poisson(a, mu, c, ml, mp))))
    R_, V_, lt_ = np.array(lignes).T
    y = lt_ - np.log(2 * np.pi / (1 - R_))
    ligne("V* Poisson contre temps exacts : pente (jeux, écart-type résiduel, corrélation)", "1,03 (147, 0,28, 0,9993)",
          f"{np.polyfit(V_, y, 1)[0]:.3f} ({len(lignes)}, {np.std(y - np.polyval(np.polyfit(V_, y, 1), V_)):.3f}, {np.corrcoef(V_, y)[0, 1]:.4f})", "0,9–1,15")

    # identité générale
    ecarts = []
    for h in (0.2, 0.3, 0.36, 0.38):
        k = 0.3
        r = m.ecart_identite_generale(lambda x, h=h: x + k * (h - (x**3 - x)), lambda x: 1 - k * (3 * x * x - 1), lambda x: -6 * k * x)
        ecarts.append((r["s_etoile"], r["ecart"]))
    ligne("Identité λ = 1 − c s*, double puits cubique : écart pour s* = 0,67 / 0,45 / 0,24 / 0,11", "0,135 / 0,060 / 0,017 / 0,003",
          " / ".join(f"{e:.3f}" for _, e in ecarts), "< 0,005 pour s* = 0,11")

    # V* gaussien quadratique
    lig = []
    for mu_ in (0.02, 0.05, 0.08):
        F = lambda x, mu_=mu_: mu_ + 0.4 * x + x * x
        mb, mh = m.zeros_de_derive(F, -3, 3)[:2]
        lam, seuil = 0.4 + 2 * mb, mh + 2 * (mh - mb)
        for sigma in np.geomspace(0.03, 0.3, 8):
            if not 1.0 < 2 * quad(lambda x: -(F(x) - x), mb, mh)[0] / sigma**2 < 14:
                continue
            T = temps_avant_embrasement_gaussien(F, sigma, mb, seuil, seed=int(sigma * 1000))
            if np.isnan(T).mean() > 0.05:
                continue
            lig.append((lam, vstar_gaussien(F, sigma, mb, mh, bas=mb - 1.5, haut=seuil + 0.5, n_noeuds=1500), np.log(np.nanmean(T))))
    lam_, V_, lt_ = np.array(lig).T
    ligne("V* gaussien contre temps simulés, application quadratique : pente", "0,98 (18 cas, deux familles)", f"{np.polyfit(V_, lt_ - np.log(2 * np.pi / (1 - lam_)), 1)[0]:.3f} ({len(lig)} cas, famille quadratique seule)", "0,85–1,1")

    # capteurs
    F = lambda x: 0.05 + 0.4 * x + x * x
    m0, mp0 = m.zeros_de_derive(F, -2, 2)[:2]
    for sigma, note in ((0.08, "3,94 / 17,65 (V* vrai 3,32)"),):
        capteurs = CapteursAffines((2.0, 0.5), (1.0, -3.0), bruit_mesure=sigma)
        un, deux = [], []
        for i in range(30):
            O = simuler_gaussien_capteurs(F, sigma, m0, mp0, 50, 300, np.random.default_rng(i), capteurs)
            un.append(min(mc.estimer_vstar_un_capteur(O[0]), 99))
            deux.append(min(mc.estimer_vstar_deux_capteurs(O), 99))
        ligne("Capteurs affines, bruit de mesure = bruit dynamique : V* deux capteurs / un capteur", note,
              f"{np.nanmedian(deux):.2f} / {np.median(un):.2f} (V* vrai {vstar_gaussien(F, sigma, m0, mp0):.2f})", "≈ 3,9 ± 20 % (un capteur ≈ 17,7)")

    print(f"\n_Durée de calcul : {time.time() - debut:.0f} s._", file=sys.stderr)


if __name__ == "__main__":
    main()
