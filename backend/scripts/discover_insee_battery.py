"""Decouvre une batterie large de series INSEE officielles, une fois, hors ligne.

Cahier des charges Helios : retour utilisateur explicite pour "un maximum de
sources par phenomene, pas juste 10". INSEE publie une FAMILLE d'enquetes de
conjoncture (menages, industrie, services, batiment, commerce...), chacune
avec plusieurs indicateurs synthetiques mensuels comparables (CVS) -- pas
seulement l'enquete menages deja utilisee.

Ce script interroge chaque dataflow de conjoncture EN BLOC (un seul appel
renvoie toutes les series du secteur, comme pour TAUX-CHOMAGE), filtre sur :
- frequence mensuelle (les series trimestrielles n'ont pas assez de points
  sur une fenetre de quelques mois)
- donnees CVS (corrigees des variations saisonnieres -- comparables)
- serie active (pas "Serie arretee")
- indicateur SYNTHETIQUE/large (climat des affaires, indicateur de surprise,
  retournement conjoncturel, confiance...) -- pas les centaines de questions
  granulaires par sous-secteur (ex. "difficultes de recrutement des
  techniciens dans la fabrication de machines"), qui seraient redondantes
  entre elles et n'ajouteraient pas de signal independant reel.

Sortie : app/data/insee_battery.json, charge par phenomena.py.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import httpx

OUTPUT_PATH = Path(__file__).resolve().parent.parent / "app" / "data" / "insee_battery.json"

DATAFLOWS = {
    "ENQ-CONJ-MENAGES": "Ménages",
    "ENQ-CONJ-SERV": "Services",
    "ENQ-CONJ-ACT-IND": "Industrie",
    "ENQ-CONJ-IND-BAT": "Bâtiment",
    "ENQ-CONJ-ART-BAT": "Artisanat du bâtiment",
    "ENQ-CONJ-COM-DET": "Commerce de détail",
    "ENQ-CONJ-COM-GROS": "Commerce de gros",
    "ENQ-CONJ-TP": "Travaux publics",
}

SYNTHETIC_PATTERNS = re.compile(
    r"climat des affaires|indicateur synth[ée]tique|indicateur de surprise|"
    r"retournement conjoncturel|confiance des m[ée]nages",
    re.IGNORECASE,
)

SERIES_RE = re.compile(r"<Series ([^>]+)/?>")
ATTR_RE = re.compile(r'(\w+)="([^"]*)"')


def parse_series_attrs(raw: str) -> list[dict]:
    return [dict(ATTR_RE.findall(attrs)) for attrs in SERIES_RE.findall(raw)]


def main() -> None:
    battery: list[dict] = []
    seen_idbanks: set[str] = set()

    with httpx.Client(timeout=60.0) as client:
        for dataflow, sector in DATAFLOWS.items():
            print(f"Interrogation de {dataflow} ({sector})...")
            try:
                resp = client.get(f"https://bdm.insee.fr/series/sdmx/data/{dataflow}", params={"lastNObservations": 1})
                resp.raise_for_status()
            except httpx.HTTPError as exc:
                print(f"  echec : {exc}")
                continue

            all_series = parse_series_attrs(resp.text)
            print(f"  {len(all_series)} series au total dans ce dataflow")

            kept = 0
            for s in all_series:
                title = s.get("TITLE_FR", "")
                idbank = s.get("IDBANK", "")
                freq = s.get("FREQ", "")
                if not idbank or idbank in seen_idbanks:
                    continue
                if freq != "M":
                    continue
                if "arrêtée" in title.lower() or "arretee" in title.lower():
                    continue
                if "CVS" not in title and "cvs" not in title.lower():
                    continue
                if not SYNTHETIC_PATTERNS.search(title):
                    continue
                battery.append({"idbank": idbank, "title": title, "sector": sector})
                seen_idbanks.add(idbank)
                kept += 1
            print(f"  {kept} series synthetiques mensuelles CVS retenues")

    print(f"\nTotal batterie : {len(battery)} series distinctes")
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(battery, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Ecrit dans {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
