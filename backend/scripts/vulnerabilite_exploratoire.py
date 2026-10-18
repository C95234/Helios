"""Diagnostics EXPLORATOIRES du banc « épidémies » (non pré-enregistrés), à lire après `vulnerabilite_evaluer.py`.

Usage (depuis backend/) :  python -m scripts.vulnerabilite_exploratoire

Contenu (cahier des charges §6 : diagnostics de la phase 4) : taux de détection θ̂ de chaque canal, dispersion φ̂, estimateurs croisés dans les
deux sens (asymétrie), niveau de R̂ par estimateur (atténuation prévue par la proposition 6), bruit des estimateurs d'une fenêtre à l'autre,
drapeaux de garde-fous. Rien de ceci ne modifie le verdict du pré-enregistrement.
"""
from __future__ import annotations

import json
import sys
import warnings
from pathlib import Path

import numpy as np

from app.vulnerabilite import banc_epidemies as be
from app.vulnerabilite import multicanal as mc
from app.vulnerabilite.garde_fous import evaluer_garde_fous

DEPOT = Path(__file__).resolve().parents[2]


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    warnings.simplefilter("ignore")
    d = be.charger_donnees(DEPOT / "data" / "vulnerabilite", "complete")
    O = np.stack([d.urgences, d.sos])
    sortie: dict = {"statut": "EXPLORATOIRE : non pré-enregistré"}

    # 1. taux de détection et dispersion (période entière, 37 départements regroupés)
    th_u, th_s = mc.taux_detection(O[0], O[1]), mc.taux_detection(O[1], O[0])
    sortie["theta"] = {"urgences": th_u, "sos": th_s, "remarque": "regroupés sur des départements de tailles très différentes ; ordre de grandeur seulement"}
    try:
        e2 = mc.estimer_deux_canaux_avec_dispersion(O, sortie=0, autre=1)
        sortie["dispersion_phi"] = e2.dispersion
    except ValueError as erreur:
        sortie["dispersion_phi"] = str(erreur)

    # 1 bis. taux de détection intra-unité (tolère un taux propre à chaque département, constant dans le temps) : période entière, moitiés, tiers
    def intra(a, b, lo, hi):
        return mc.taux_detection_intra_unite(a[lo:hi], b[lo:hi])

    T = d.urgences.shape[0]
    sortie["theta_intra_unite"] = {
        "periode_entiere": {"urgences": intra(d.urgences, d.sos, 0, T), "sos": intra(d.sos, d.urgences, 0, T)},
        "moities": [{"semaines": [lo, hi], "urgences": intra(d.urgences, d.sos, lo, hi), "sos": intra(d.sos, d.urgences, lo, hi)} for lo, hi in ((0, 52), (52, T))],
        "tiers": [{"semaines": [lo, hi], "urgences": intra(d.urgences, d.sos, lo, hi), "sos": intra(d.sos, d.urgences, lo, hi)} for lo, hi in ((0, 35), (35, 70), (70, T))],
        "simulation_de_reference": {
            "taux_commun": "urgences 0,42 [0,21 ; 0,57] (vrai 0,40)", "taux_propre_a_chaque_departement": "regroupé −24, intra-unité 0,57 [0,32 ; 0,83]",
            "taux_en_derive_dans_le_temps": "regroupé 1,31, intra-unité 1,32 [0,96 ; 1,72], 92 % hors de ]0 ; 1[",
        },
    }
    par_dep = []
    for j in range(d.urgences.shape[1]):
        a, b = d.urgences[:, j:j + 1], d.sos[:, j:j + 1]
        try:
            par_dep.append(mc.taux_detection(a, b))
        except ValueError:
            par_dep.append(float("nan"))
    par_dep = np.array(par_dep)
    sortie["theta_urgences_par_departement_regroupe_dans_chaque_dept"] = {
        "part_dans_0_1": float(np.mean((par_dep > 0) & (par_dep < 1))), "quartiles": np.nanpercentile(par_dep, [25, 50, 75]).tolist(),
        "remarque": "individuellement trop imprécis pour être interprétés (simulation : 28 à 67 % dans ]0 ; 1[ même si le modèle est exact)",
    }

    # 2. R sur la période entière et par fenêtre : niveaux et bruit
    r_tot = {
        "croise_urgences_sortie": mc.pente_croisee(d.urgences, d.sos, effets_unite=True),
        "croise_sos_sortie": mc.pente_croisee(d.sos, d.urgences, effets_unite=True),
        "urgences_seules": mc.pente_naive(d.urgences, d.urgences, effets_unite=True),
        "sos_seul": mc.pente_naive(d.sos, d.sos, effets_unite=True),
    }
    sortie["R_periode_entiere_effets_unite"] = r_tot
    sortie["asymetrie_des_croises"] = r_tot["croise_sos_sortie"] - r_tot["croise_urgences_sortie"]
    r = be.r_par_fenetre(d.urgences, d.sos, be.TAILLE_C1)
    g = be.croissance_eaux(d.eaux, be.TAILLE_C1)
    sortie["R_par_fenetre_12_semaines"] = {
        k: {"mediane": float(np.nanmedian(v)), "ecart_type": float(np.nanstd(v)), "min": float(np.nanmin(v)), "max": float(np.nanmax(v)), "n_nan": int(np.isnan(v).sum())}
        for k, v in r.items()
    }
    sortie["correlations_de_rang_entre_estimateurs"] = {
        "croise_urgences": be._spearman(r["croise"], r["urgences"]), "croise_sos": be._spearman(r["croise"], r["sos"]), "urgences_sos": be._spearman(r["urgences"], r["sos"]),
    }
    sortie["rho_avec_g_si_deux_canaux_sont_combines"] = {
        "somme_des_deux_canaux_naif": be._spearman(be.r_par_fenetre(d.urgences + d.sos, d.urgences + d.sos, be.TAILLE_C1)["urgences"], g)
    }
    sortie["g_croissance_eaux"] = {"mediane": float(np.nanmedian(g)), "ecart_type": float(np.nanstd(g))}

    # 3. drapeaux de garde-fous (période entière)
    e = mc.estimer_multicanal(O, sortie=0, instrument=1, calibrage=1)
    dr = evaluer_garde_fous(phi=e.phi, c=e.c, R=e.R, n_unites=len(d.departements), theta=min(th_u, th_s), ecart_croise=sortie["asymetrie_des_croises"])
    sortie["multicanal_periode_entiere_regroupe"] = {"R": e.R, "c": e.c, "m_bas": e.m_bas, "phi": e.phi, "theta": e.theta, "drapeaux": dr.liste(),
                                                      "remarque": "c et Φ̂ dépendent de l'échelle des comptes : unités de tailles différentes, non interprétables (exploratoire)"}
    chemin = DEPOT / "docs" / "vulnerabilite" / "resultats_exploratoires.json"
    chemin.write_text(json.dumps(sortie, ensure_ascii=False, indent=2, default=float), encoding="utf-8")
    print(json.dumps(sortie, ensure_ascii=False, indent=1, default=float))


if __name__ == "__main__":
    main()
