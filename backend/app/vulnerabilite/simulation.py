"""Simulateurs de la note (comptages à contagion complexe, chocs communs, temps avant embrasement).

Reprend `core.py`, `t2`, `t6` de la note. Les simulations renvoient les séries COMPLÈTES ; la coupure
« protocole de la note » (qui utilise la vérité terrain) est une fonction à part, distincte de la règle de
coupure fondée sur les seules données observées (`estimation.couper_au_premier_depassement`).
Les flux aléatoires sont consommés comme dans les scripts de la note : à graine égale, mêmes tirages.
"""
from __future__ import annotations

import numpy as np

from .bruits import Poisson
from .modele import params_depuis_inflammabilite, reponse_moyenne

_PLAFOND = 1e5  # plafond de la moyenne simulée (scripts de la note)


def simuler_unites(
    a: float,
    mu: float,
    c: float,
    n_unites: int,
    n_pas: int,
    rng: np.random.Generator,
    y0: float = 3.0,
    bruit=None,
    mu_t=None,
    a_t=None,
    c_t=None,
) -> np.ndarray:
    """`n_unites` unités indépendantes, `n_pas` pas ; renvoie X de forme (n_pas, n_unites), sans coupure.

    `mu_t`, `a_t`, `c_t` : trajectoires de paramètres (un par pas) pour les scénarios à dérive lente.
    """
    bruit = bruit or Poisson()
    y = np.full(n_unites, float(round(y0)))
    X = np.empty((n_pas, n_unites))
    for t in range(n_pas):
        aa = a_t[t] if a_t is not None else a
        mm = mu_t[t] if mu_t is not None else mu
        cc = c_t[t] if c_t is not None else c
        moyenne = np.clip(reponse_moyenne(y, aa, mm, cc), 0, _PLAFOND)
        y = bruit.simuler(moyenne, rng)
        X[t] = y
    return X


def couper_avant_embrasement(X: np.ndarray, m_haut: float, marge: int = 5) -> np.ndarray:
    """Protocole de la note : chaque série est coupée `marge` pas avant son premier passage au seuil `m_haut`.

    Utilise la vérité terrain (m₊ connu) : réservé aux tests sur données simulées. Comme dans les scripts,
    les `marge` derniers pas des séries qui ne s'embrasent jamais sont aussi retirés.
    """
    X = np.array(X, dtype=float, copy=True)
    n_pas, n_unites = X.shape
    for i in range(n_unites):
        franchis = np.where(X[:, i] >= m_haut)[0]
        arret = int(franchis[0]) if franchis.size else n_pas
        X[max(arret - marge, 0):, i] = np.nan
    return X


def temps_avant_embrasement(
    R: float,
    c: float,
    m_bas: float,
    n: int = 400,
    t_max: int = 200_000,
    seed: int = 0,
) -> np.ndarray:
    """Temps du premier passage de y au-dessus de 2·m₊ + 5, depuis l'état calme ; NaN si censuré à `t_max`."""
    a, mu, _, m_haut = params_depuis_inflammabilite(R, c, m_bas)
    rng = np.random.default_rng(seed)
    y = np.full(n, float(round(m_bas)))
    T = np.full(n, np.nan)
    vivant = np.ones(n, bool)
    seuil = 2 * m_haut + 5
    for t in range(1, t_max + 1):
        y[vivant] = rng.poisson(np.maximum(reponse_moyenne(y[vivant], a, mu, c), 0))
        touche = vivant & (y >= seuil)
        T[touche] = t
        vivant &= ~touche
        if not vivant.any():
            break
    return T


def simuler_societe_chocs_communs(
    amplitude: float,
    rng: np.random.Generator,
    R: float = 0.6,
    c: float = 0.01,
    m_bas: float = 3.0,
    n_unites: int = 100,
    n_pas: int = 300,
    k_coupure: float = 6.0,
) -> np.ndarray:
    """Société soumise à des chocs communs persistants (cycle médiatique), scénario de la note (script `t6`).

    Le flux d'étincelles est multiplié par exp(amplitude·(t/T)·e_t − …), e_t étant un AR(1) de coefficient 0,8
    commun à toutes les unités. Chaque unité est coupée au premier dépassement de `k_coupure` fois sa moyenne
    récente (règle fondée sur les données observées).
    """
    a, mu, _, _ = params_depuis_inflammabilite(R, c, m_bas)
    y = np.full(n_unites, 3.0)
    X = np.full((n_pas, n_unites), np.nan)
    e = 0.0
    vivant = np.ones(n_unites, bool)
    moyenne_recente = np.full(n_unites, 3.0)
    for t in range(n_pas):
        e = 0.8 * e + rng.normal(0, 1)
        flux = mu * np.exp(amplitude * (t / n_pas) * e - 0.5 * (amplitude * t / n_pas) ** 2 / (1 - 0.64))
        y = rng.poisson(np.clip(flux + a * y + c * y * y, 0, _PLAFOND)).astype(float)
        evenement = vivant & (y >= k_coupure * np.maximum(moyenne_recente, 1))
        vivant &= ~evenement
        X[t, vivant] = y[vivant]
        moyenne_recente = 0.9 * moyenne_recente + 0.1 * y
    return X
