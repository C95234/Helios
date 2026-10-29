"""Définition automatique d'un « démarrage de vague » (cahier §5, point 2), fixée AVANT toute évaluation.

Règle (sur une série hebdomadaire nationale S_t, par exemple la somme des urgences COVID des départements étudiés) :
la semaine t est un démarrage si
1. la médiane des `fenetre_calme` semaines précédentes est au moins `plancher` (sinon le niveau est trop bas pour juger) ;
2. S_t ≥ `facteur` × cette médiane ;
3. la croissance se confirme : S_{t+1} > S_t, …, jusqu'à `confirmation` semaines de croissance stricte consécutives ;
4. aucun démarrage n'a été déclaré dans les `refractaire` semaines précédentes (même vague).

La règle utilise des semaines postérieures à t (confirmation) pour DATER l'événement ; les indicateurs évalués en
phase 4 n'utilisent, eux, que les semaines antérieures au démarrage.
"""
from __future__ import annotations

import numpy as np

FACTEUR = 1.5
FENETRE_CALME = 8
CONFIRMATION = 2
REFRACTAIRE = 8
PLANCHER = 20.0


def detecter_demarrages(
    serie,
    facteur: float = FACTEUR,
    fenetre_calme: int = FENETRE_CALME,
    confirmation: int = CONFIRMATION,
    refractaire: int = REFRACTAIRE,
    plancher: float = PLANCHER,
) -> list[int]:
    """Indices (0-based) des semaines de démarrage dans `serie` (valeurs hebdomadaires, sans NaN)."""
    S = np.asarray(serie, dtype=float)
    if np.isnan(S).any():
        raise ValueError("La série nationale ne doit pas contenir de NaN.")
    demarrages: list[int] = []
    for t in range(fenetre_calme, len(S) - confirmation):
        mediane = float(np.median(S[t - fenetre_calme:t]))
        if mediane < plancher or S[t] < facteur * mediane:
            continue
        if not all(S[t + k + 1] > S[t + k] for k in range(confirmation)):
            continue
        if demarrages and t - demarrages[-1] <= refractaire:
            continue
        demarrages.append(t)
    return demarrages
