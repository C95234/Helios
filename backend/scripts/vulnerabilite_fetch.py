"""Téléchargement des données brutes du banc « épidémies » (module vulnérabilité, phase 2).

Usage (depuis backend/) :  python -m scripts.vulnerabilite_fetch

Pour chaque fichier : télécharge depuis data.gouv.fr (URL lue dans l'API du jeu), enregistre la date, la taille et la
somme SHA-256 dans `data/vulnerabilite/manifeste.json` (commité), écrit le fichier dans `data/vulnerabilite/raw/`
(hors git). Un fichier brut déjà présent n'est JAMAIS réécrit ni modifié : si son empreinte ne correspond plus au
manifeste, le script s'arrête avec une erreur.
"""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import httpx

RACINE = Path(__file__).resolve().parents[2] / "data" / "vulnerabilite"
BRUT = RACINE / "raw"
MANIFESTE = RACINE / "manifeste.json"

#: (identifiant du jeu data.gouv.fr, titre exact de la ressource, rôle)
FICHIERS = [
    ("5e74ecf52eb7514f2d3b8845", "sursaud-covid-quot-dep-2025-01-01-18h00.csv", "comptes quotidiens urgences et SOS Médecins, par département"),
    ("5e74ecf52eb7514f2d3b8845", "metadonnee-urgenceshos-sosmedecins-covid19-quot-dep.csv", "métadonnées des champs"),
    ("5e74ecf52eb7514f2d3b8845", "code-tranches-dage.csv", "codes des classes d'âge"),
    ("5ee9df5003284f565d561278", "table-indicateurs-open-data-dep-serie.csv", "indicateurs de suivi par département (référence de R pour C1)"),
]


def sha256(chemin: Path) -> str:
    h = hashlib.sha256()
    with chemin.open("rb") as f:
        for bloc in iter(lambda: f.read(1 << 20), b""):
            h.update(bloc)
    return h.hexdigest()


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    BRUT.mkdir(parents=True, exist_ok=True)
    manifeste = json.loads(MANIFESTE.read_text(encoding="utf-8")) if MANIFESTE.exists() else {"fichiers": []}
    connus = {f["nom"]: f for f in manifeste["fichiers"]}
    with httpx.Client(timeout=120, follow_redirects=True) as client:
        for jeu, titre, role in FICHIERS:
            cible = BRUT / titre
            if cible.exists():
                if titre in connus and sha256(cible) == connus[titre]["sha256"]:
                    print(f"= {titre} : déjà présent, empreinte conforme au manifeste.")
                    continue
                raise SystemExit(f"{titre} existe mais ne correspond pas au manifeste : on ne l'écrase pas. Vérifier à la main.")
            meta = client.get(f"https://www.data.gouv.fr/api/1/datasets/{jeu}/").raise_for_status().json()
            ressources = [r for r in meta["resources"] if r["title"] == titre]
            if len(ressources) != 1:
                raise SystemExit(f"Ressource {titre!r} introuvable (ou ambiguë) dans le jeu {jeu}.")
            url = ressources[0]["url"]
            partiel = cible.with_suffix(cible.suffix + ".part")
            with client.stream("GET", url) as reponse:
                reponse.raise_for_status()
                attendu = int(reponse.headers.get("content-length", 0))
                with partiel.open("wb") as f:
                    for bloc in reponse.iter_bytes(1 << 20):
                        f.write(bloc)
            taille = partiel.stat().st_size
            if attendu and taille != attendu:
                partiel.unlink()
                raise SystemExit(f"{titre} : taille reçue {taille} ≠ annoncée {attendu}. Téléchargement abandonné.")
            partiel.rename(cible)
            entree = {
                "nom": titre, "jeu_data_gouv": jeu, "role": role, "url": url,
                "telecharge_le": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "taille_octets": taille, "sha256": sha256(cible),
                "titre_du_jeu": meta["title"], "licence": meta.get("license"),
                "derniere_modification_source": ressources[0].get("last_modified"),
            }
            manifeste["fichiers"].append(entree)
            MANIFESTE.write_text(json.dumps(manifeste, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"+ {titre} : {taille / 1e6:.2f} Mo, sha256 {entree['sha256'][:16]}…")


if __name__ == "__main__":
    main()
