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
