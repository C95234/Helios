"""Les tirs disruptes sont-ils signales plus souvent que les tirs stables ? Test exact de Fisher
unilateral sur la table 2x2 (signale / non signale) x (disrupte / stable).

Pourquoi un test plutot qu'un seuil sur les taux : avec 10 tirs de chaque sorte, 8/10 contre 3/10
donne p = 0.035 mais 8/10 contre 4/10 donne p = 0.085 -- un ecart d'un seul tir, qui est
exactement la variation d'un tirage Monte-Carlo a l'autre (Journal §15).
"""
from __future__ import annotations

from scipy.stats import fisher_exact


def fisher_discrimination_p(n_hits: int, n_positive: int, n_false_alarms: int, n_negative: int) -> float | None:
    """p-value unilaterale : P(au moins autant de signaux chez les positifs | aucune difference)."""
    if n_positive <= 0 or n_negative <= 0:
        return None
    table = [[n_hits, n_positive - n_hits], [n_false_alarms, n_negative - n_false_alarms]]
    return float(fisher_exact(table, alternative="greater")[1])
