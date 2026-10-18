"""Exécute le pré-enregistrement du banc « épidémies » sur les données réelles (module vulnérabilité, phase 4).

Usage (depuis backend/) :  python -m scripts.vulnerabilite_evaluer [--graine 20261018]

Écrit docs/vulnerabilite/resultats_epidemies.json (ou resultats_epidemies_graine_<g>.json si la graine n'est pas celle par défaut).
Ce script applique `app.vulnerabilite.banc_epidemies.executer_tout` tel quel : aucun paramètre du pré-enregistrement ne se règle ici.
Le code et ce script sont commités (étiquette `evaluation-v1-code`) AVANT la première exécution sur données réelles.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from app.vulnerabilite import banc_epidemies as be

DEPOT = Path(__file__).resolve().parents[2]
GRAINE_PAR_DEFAUT = 20261018


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser()
    parser.add_argument("--graine", type=int, default=GRAINE_PAR_DEFAUT)
    args = parser.parse_args()
    racine = DEPOT / "data" / "vulnerabilite"
    complet = be.charger_donnees(racine, "complete")
    partiel = be.charger_donnees(racine, "partielle")
    resultat = be.executer_tout(complet, partiel, graine=args.graine)
    nom = "resultats_epidemies.json" if args.graine == GRAINE_PAR_DEFAUT else f"resultats_epidemies_graine_{args.graine}.json"
    sortie = DEPOT / "docs" / "vulnerabilite" / nom
    sortie.write_text(json.dumps(resultat, ensure_ascii=False, indent=2, default=float), encoding="utf-8")
    c1, c3 = resultat["C1_prime"], resultat["C3_canaux_melanges"]
    print(f"Décision : {resultat['decision']}")
    print(f"C1′ : réussi = {c1['reussi']} ; ρ croisé {c1['rho_croise']:.3f}, urgences {c1['rho_urgences']:.3f}, SOS {c1['rho_sos']:.3f} ; "
          f"Δ = {c1['delta']:.3f} IC90 [{c1['ic90_delta'][0]:.3f} ; {c1['ic90_delta'][1]:.3f}]")
    print(f"C3 (ii) : propre = {c3['propre']} ; médiane Δ placebo {c3['delta_placebo_mediane']:.3f}, p95 {c3['delta_placebo_p95']:.3f}")
    print(f"Résultats écrits dans {sortie}")


if __name__ == "__main__":
    main()
