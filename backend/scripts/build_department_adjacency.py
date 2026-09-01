"""Construit le graphe d'adjacence des departements francais (metropole) -- une fois, hors ligne.

Source : contours geographiques IGN Admin Express COG (2018), republies sous
Licence Ouverte / Etalab par gregoiredavid/france-geojson
(https://github.com/gregoiredavid/france-geojson). Deux departements sont
consideres voisins si leurs polygones partagent une frontiere (contiguite de
type "rook").

Sortie : app/data/departements_adjacency.json, charge tel quel par le
connecteur geographique -- cahier des charges Helios §6, §5.2.
"""
from __future__ import annotations

import json
from pathlib import Path

import httpx
from shapely.geometry import shape
from shapely.strtree import STRtree

GEOJSON_URL = "https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/departements.geojson"
OUTPUT_PATH = Path(__file__).resolve().parent.parent / "app" / "data" / "departements_adjacency.json"

# Departements metropolitains uniquement (donnees de contours DOM incompletes
# dans la source, et la serie INSEE TAUX-CHOMAGE distingue les DOM a part).
METROPOLITAN_CODES = {f"{i:02d}" for i in range(1, 96)} | {"2A", "2B"}
METROPOLITAN_CODES.discard("20")  # 20 = ancien code Corse, remplace par 2A/2B


def main() -> None:
    print("Telechargement des contours...")
    raw = httpx.get(GEOJSON_URL, timeout=30.0).json()

    features = [f for f in raw["features"] if f["properties"]["code"] in METROPOLITAN_CODES]
    print(f"{len(features)} departements metropolitains retenus")

    codes = [f["properties"]["code"] for f in features]
    names = {f["properties"]["code"]: f["properties"]["nom"] for f in features}
    geometries = [shape(f["geometry"]) for f in features]

    tree = STRtree(geometries)
    adjacency: dict[str, list[str]] = {code: [] for code in codes}

    for i, geom in enumerate(geometries):
        candidate_idx = tree.query(geom)
        for j in candidate_idx:
            j = int(j)
            if j == i:
                continue
            if geom.touches(geometries[j]) or geom.intersects(geometries[j]):
                other_code = codes[j]
                if other_code not in adjacency[codes[i]]:
                    adjacency[codes[i]].append(other_code)

    n_edges = sum(len(v) for v in adjacency.values()) // 2
    isolated = [c for c, neighbors in adjacency.items() if not neighbors]
    print(f"{n_edges} paires de voisins trouvees. Departements isoles (a verifier) : {isolated}")

    output = {
        "source": "IGN Admin Express COG 2018, via gregoiredavid/france-geojson (Licence Ouverte)",
        "url": GEOJSON_URL,
        "n_departments": len(codes),
        "names": names,
        "adjacency": adjacency,
    }
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Ecrit dans {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
