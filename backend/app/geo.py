"""Reseau territorial reel (departements) et grille de controle -- cahier des charges Helios §5.2, H2.

Le reseau reel est charge depuis app/data/departements_adjacency.json,
derive une fois hors ligne des contours IGN (voir scripts/build_department_adjacency.py).
La grille de controle est une grille reguliere de meme taille (contiguite
"rook", 4 voisins) -- exactement la comparaison que H2 demande (§5.5) :
topologie reelle heterogene contre grille idealisee.
"""
from __future__ import annotations

import json
import math
from functools import lru_cache
from pathlib import Path

import numpy as np

ADJACENCY_PATH = Path(__file__).resolve().parent / "data" / "departements_adjacency.json"


@lru_cache(maxsize=1)
def load_department_network() -> dict:
    with open(ADJACENCY_PATH, encoding="utf-8") as f:
        return json.load(f)


def department_weight_matrix(codes: list[str], adjacency: dict[str, list[str]]) -> np.ndarray:
    index = {code: i for i, code in enumerate(codes)}
    n = len(codes)
    w = np.zeros((n, n))
    for code, neighbors in adjacency.items():
        if code not in index:
            continue
        for neighbor in neighbors:
            if neighbor in index:
                w[index[code], index[neighbor]] = 1
    return w


def knn_weight_matrix(x: np.ndarray, y: np.ndarray, k: int) -> np.ndarray:
    """Matrice de poids par k plus proches voisins geometriques -- utilisee
    pour un reseau de capteurs physiques (ex. sondes magnetiques MAST, §7ter)
    plutot qu'un decoupage administratif : pas de notion de "frontiere
    commune", seulement une position (x, y) par noeud. w_ij=1 si j est parmi
    les k plus proches voisins de i (relation non symetrique en general,
    symetrisee ici par OU logique -- w_ij=1 si i voisin de j OU j voisin de
    i -- pour rester une matrice de poids utilisable telle quelle par
    `stats/moran.py`, qui ne suppose pas la symetrie mais s'attend a une
    matrice coherente avec S0 = somme des poids)."""
    coords = np.column_stack([x, y])
    n = len(coords)
    dist = np.linalg.norm(coords[:, None, :] - coords[None, :, :], axis=-1)
    np.fill_diagonal(dist, np.inf)
    w = np.zeros((n, n))
    nearest = np.argsort(dist, axis=1)[:, :k]
    for i in range(n):
        w[i, nearest[i]] = 1
    return np.maximum(w, w.T)


def regular_grid_weight_matrix(n: int) -> tuple[np.ndarray, tuple[int, int]]:
    """Grille reguliere rectangulaire la plus carree possible pour n cellules, contiguite rook."""
    rows = int(math.floor(math.sqrt(n)))
    while n % rows != 0:
        rows -= 1
    cols = n // rows

    w = np.zeros((n, n))
    for r in range(rows):
        for c in range(cols):
            i = r * cols + c
            for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                rr, cc = r + dr, c + dc
                if 0 <= rr < rows and 0 <= cc < cols:
                    w[i, rr * cols + cc] = 1
    return w, (rows, cols)
