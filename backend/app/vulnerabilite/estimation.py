"""Estimation de (μ, a, c) et de l'indice Φ à partir de comptages (note, section 2).

Estimateur : régression pondérée (poids 1/F̂, deux itérations) de y_{t+1,i} sur (1, y_{t,i}, y_{t,i}²),
regroupée sur toutes les unités et tous les pas. On en tire ĉ, m̂₋ (niveau moyen calme), R̂ = â + 2ĉ·m̂₋,
ŝ* = (1 − R̂)/ĉ, puis Φ̂ par la forme close. Si ĉ ≤ 0, Φ̂ = +∞ (pas de seuil détecté) ; si R̂ ≥ 1, Φ̂ = 0.

Reprend `core.fit` et `core.fit_fe` de la note. Les séries peuvent contenir des NaN (après coupure).
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .modele import phi_poisson

_PLANCHER_POIDS = 0.5  # plancher de la moyenne ajustée dans les poids (scripts de la note)


@dataclass(frozen=True)
class Ajustement:
    """Résultat d'un ajustement. `mu` vaut NaN pour l'ajustement à effets fixes temporels (non identifié)."""

    mu: float
    a: float
    c: float
    R: float
    m_bas: float
    phi: float

    @property
    def s_etoile(self) -> float:
        """ŝ* = (1 − R̂)/ĉ ; NaN si ĉ ≤ 0."""
        return (1.0 - self.R) / self.c if self.c > 0 else float("nan")


def _phi_ou_cas_limite(R: float, c: float, m_bas: float) -> float:
    if c > 0 and R < 1:
        return phi_poisson(R, c, m_bas, controle_a=False)
    return 0.0 if R >= 1 else float("inf")


def _paires_valides(X: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    x = X[:-1].ravel()
    y = X[1:].ravel()
    ok = ~np.isnan(x) & ~np.isnan(y)
    return x[ok], y[ok]


def ajuster(X: np.ndarray, ponderer: bool = True, niveau_calme: float | None = None) -> Ajustement:
    """Ajuste y_{t+1} = μ + a·y_t + c·y_t² sur X de forme (n_pas, n_unites).

    `niveau_calme` : m₋ imposé ; par défaut la moyenne de toutes les valeurs observées (comme la note,
    adaptée à des séries coupées avant l'embrasement ; sur données réelles, le définir explicitement).
    """
    X = np.asarray(X, dtype=float)
    x, y = _paires_valides(X)
    if x.size < 3:
        raise ValueError("Moins de 3 paires (y_t, y_{t+1}) observées : ajustement impossible.")
    A = np.stack([np.ones_like(x), x, x * x], axis=1)
    poids = np.ones_like(x)
    for _ in range(2 if ponderer else 1):
        racine = np.sqrt(poids)
        b = np.linalg.lstsq(A * racine[:, None], y * racine, rcond=None)[0]
        poids = 1.0 / np.clip(A @ b, _PLANCHER_POIDS, None)
    mu, a, c = (float(v) for v in b)
    m_bas = float(np.nanmean(X)) if niveau_calme is None else float(niveau_calme)
    R = a + 2.0 * c * m_bas
    return Ajustement(mu=mu, a=a, c=c, R=R, m_bas=m_bas, phi=_phi_ou_cas_limite(R, c, m_bas))


def ajuster_effets_temporels(X: np.ndarray, niveau_calme: float | None = None) -> Ajustement:
    """Effets fixes temporels : y_{t+1,i} = α_t + a·y_{t,i} + c·y_{t,i}² ; on retire la moyenne transversale
    de y_{t+1}, y_t et y_t² à chaque instant (retire les chocs communs, mais aussi une vague réellement nationale).
    """
    X = np.asarray(X, dtype=float)
    x_t, y_t = X[:-1], X[1:]
    ok = ~np.isnan(x_t) & ~np.isnan(y_t)
    lignes = []
    for t in range(x_t.shape[0]):
        m = ok[t]
        if m.sum() < 3:
            continue
        xt, yt = x_t[t, m], y_t[t, m]
        lignes.append(np.stack([yt - yt.mean(), xt - xt.mean(), xt * xt - (xt * xt).mean()], axis=1))
    if not lignes:
        raise ValueError("Aucun instant avec au moins 3 unités observées : ajustement impossible.")
    M = np.vstack(lignes)
    a, c = (float(v) for v in np.linalg.lstsq(M[:, 1:], M[:, 0], rcond=None)[0])
    m_bas = float(np.nanmean(X)) if niveau_calme is None else float(niveau_calme)
    R = a + 2.0 * c * m_bas
    return Ajustement(mu=float("nan"), a=a, c=c, R=R, m_bas=m_bas, phi=_phi_ou_cas_limite(R, c, m_bas))


def couper_au_premier_depassement(X: np.ndarray, seuil: float, marge: int = 0) -> np.ndarray:
    """Règle de coupure fondée sur les seules données observées : chaque série est coupée au premier
    passage de y au-dessus de `seuil` (le pas de franchissement est retiré), moins `marge` pas.

    Règle (note, section 2) : couper HAUT, au moins au niveau du seuil estimé m̂₊ = m̂₋ + ŝ*. Une coupure trop
    basse retire les excursions qui renseignent sur c et fait paraître la population plus sûre qu'elle ne l'est.
    """
    X = np.array(X, dtype=float, copy=True)
    for i in range(X.shape[1]):
        franchis = np.where(X[:, i] >= seuil)[0]
        if franchis.size:
            X[max(int(franchis[0]) - marge, 0):, i] = np.nan
    return X


def couper_niveau_glissant(X: np.ndarray, k: float = 6.0, lissage: float = 0.9, niveau_initial: float = 3.0) -> np.ndarray:
    """Coupure à `k` fois la moyenne récente de chaque unité (scénarios de dérive et de chocs de la note).

    La moyenne récente est une moyenne exponentielle (coefficient `lissage`), mise à jour après chaque pas ;
    une unité coupée n'est plus observée. Le pas de franchissement est retiré.
    """
    X = np.asarray(X, dtype=float)
    n_pas, n_unites = X.shape
    sortie = np.full_like(X, np.nan)
    vivant = np.ones(n_unites, bool)
    recente = np.full(n_unites, float(niveau_initial))
    for t in range(n_pas):
        y = X[t]
        evenement = vivant & (y >= k * np.maximum(recente, 1))
        vivant &= ~evenement
        sortie[t, vivant] = y[vivant]
        recente = lissage * recente + (1 - lissage) * np.nan_to_num(y, nan=0.0)
    return sortie


def ajuster_en_coupant_iterativement(
    X: np.ndarray,
    k_initial: float = 4.0,
    niveau_calme: float | None = None,
    n_iterations_max: int = 5,
) -> tuple[Ajustement, float]:
    """EXPÉRIMENTAL (suggéré par la note, non validé par elle) : coupe à k·m₋, ajuste, puis relève la coupure
    tant qu'elle est sous le seuil estimé m̂₊ = m̂₋ + ŝ*. Retourne (ajustement, seuil de coupure final).
    """
    X = np.asarray(X, dtype=float)
    m_bas = float(np.nanmean(X)) if niveau_calme is None else float(niveau_calme)
    seuil = k_initial * m_bas
    ajust = ajuster(couper_au_premier_depassement(X, seuil), niveau_calme=m_bas)
    for _ in range(n_iterations_max):
        if not (ajust.c > 0 and ajust.R < 1):
            break
        m_haut = m_bas + ajust.s_etoile
        if seuil >= m_haut:
            break
        seuil = m_haut
        ajust = ajuster(couper_au_premier_depassement(X, seuil), niveau_calme=m_bas)
    return ajust, float(seuil)


def ajuster_fenetres(X: np.ndarray, taille: int = 60, pas: int = 20, effets_temporels: bool = False) -> list[Ajustement | None]:
    """Ajustement sur fenêtres glissantes de `taille` pas, décalées de `pas` ; None si la fenêtre est inexploitable."""
    X = np.asarray(X, dtype=float)
    ajusteur = ajuster_effets_temporels if effets_temporels else ajuster
    resultats = []
    for debut in range(0, X.shape[0] - taille + 1, pas):
        try:
            resultats.append(ajusteur(X[debut:debut + taille]))
        except ValueError:
            resultats.append(None)
    return resultats
