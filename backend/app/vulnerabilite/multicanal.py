"""Estimation à partir de canaux d'observation sous-déclarés et éventuellement sous boucle de surveillance
(note, section 3 et propositions 6 à 10).

Résultats démontrés dans la note (hypothèse 2 : amincissement binomial, canaux indépendants conditionnellement
à y, l'observation ne modifie pas la dynamique) :
- un seul canal fait paraître la population plus sûre qu'elle ne l'est (prop. 6) ;
- estimateur croisé de R par variable instrumentale (prop. 7) ; une asymétrie entre les deux estimateurs croisés
  désigne le canal sous boucle de surveillance (corollaire) ;
- taux de détection θ identifié sans le connaître (prop. 8) ; dérive quadratique par moments factoriels ;
- dispersion φ identifiée par canaux croisés (prop. 10).

Les tableaux de données ont la forme (n_canaux, n_pas, n_unites) ; les NaN (après coupure) sont ignorés.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .estimation import _phi_ou_cas_limite
from .modele import zeros_de_derive
from .vstar import vstar_gaussien


def _masque(*tableaux: np.ndarray) -> np.ndarray:
    ok = np.ones(tableaux[0].shape, bool)
    for t in tableaux:
        ok &= ~np.isnan(t)
    return ok


def pente_naive(sortie: np.ndarray, entree: np.ndarray) -> float:
    """Pente MCO de o_{t+1} sur o_t (estimateur « naïf » d'un seul canal), avec constante."""
    x = entree[:-1].ravel()
    y = sortie[1:].ravel()
    ok = ~np.isnan(x) & ~np.isnan(y)
    A = np.stack([np.ones(ok.sum()), x[ok]], axis=1)
    return float(np.linalg.lstsq(A, y[ok], rcond=None)[0][1])


def _retirer_moyenne_par_instant(v: np.ndarray) -> np.ndarray:
    """Soustrait à chaque instant (ligne) la moyenne transversale des unités observées."""
    return v - np.nanmean(v, axis=1, keepdims=True)


def pente_croisee(sortie: np.ndarray, instrument: np.ndarray, effets_temporels: bool = False) -> float:
    """R̂ = Cov(o^l_{t+1}, o^k_t) / Cov(o^l_t, o^k_t) : régression à variable instrumentale (proposition 7),
    le canal `instrument` (k) instrumentant le canal `sortie` (l). Cas linéaire (c = 0).

    `effets_temporels=True` : covariances calculées après retrait, à chaque instant, de la moyenne transversale
    (la proposition 7 exige μ constant ou des effets fixes temporels).
    """
    x, z, y = sortie[:-1], instrument[:-1], sortie[1:]
    ok = ~np.isnan(x) & ~np.isnan(z) & ~np.isnan(y)
    if effets_temporels:
        ok &= ok.sum(axis=1, keepdims=True) >= 3
        x, z, y = (_retirer_moyenne_par_instant(np.where(ok, v, np.nan)) for v in (x, z, y))
    x, z, y = x[ok], z[ok], y[ok]
    if x.size < 3:
        raise ValueError("Moins de 3 observations complètes : estimation impossible.")
    return float(np.cov(y, z)[0, 1] / np.cov(x, z)[0, 1])


@dataclass(frozen=True)
class DiagnosticAsymetrie:
    """Les deux estimateurs croisés coïncident si aucun canal n'a de boucle ; sinon l'écart désigne le canal
    dont l'estimateur « en sortie » est gonflé."""

    r_l_depuis_k: float  # sortie l, instrument k
    r_k_depuis_l: float  # sortie k, instrument l
    ecart: float
    canal_suspect: int | None  # indice (0 = l, 1 = k) du canal sous boucle, None si écart sous le seuil
    seuil: float


def diagnostic_asymetrie(o_l: np.ndarray, o_k: np.ndarray, seuil: float = 0.10) -> DiagnosticAsymetrie:
    """Diagnostic de boucle de surveillance (corollaire de la prop. 7).

    `seuil` : écart absolu de R̂ au-delà duquel on déclare une asymétrie. Valeur PROVISOIRE (la note ne fixe
    pas de seuil) : à figer dans le pré-enregistrement avant toute évaluation sur données réelles.
    """
    r_lk = pente_croisee(o_l, o_k)
    r_kl = pente_croisee(o_k, o_l)
    ecart = r_kl - r_lk
    suspect = None
    if abs(ecart) > seuil:
        # un estimateur dont le canal « en sortie » est sous boucle est gonflé
        suspect = 1 if ecart > 0 else 0
    return DiagnosticAsymetrie(r_lk, r_kl, float(ecart), suspect, seuil)


def taux_detection(o_a: np.ndarray, o_b: np.ndarray) -> float:
    """θ^a = 1 − [Var(o^a) − Cov(o^a, o^b)·E o^a / E o^b] / E o^a (proposition 8, canaux sans boucle).

    Valable quelle que soit la loi de y. Port exact du script : variance à ddof = 0, covariance à ddof = 1
    (écart négligeable à effectifs usuels).
    """
    a = o_a.ravel()
    b = o_b.ravel()
    ok = ~np.isnan(a) & ~np.isnan(b)
    a, b = a[ok], b[ok]
    return float(1.0 - (a.var() - np.cov(a, b)[0, 1] * a.mean() / b.mean()) / a.mean())


def derive_instrumentee(
    o_sortie: np.ndarray,
    o_instrument: np.ndarray,
    effets_temporels: bool = False,
) -> tuple[float, float, float]:
    """(β₀, β₁, β₂) de o_{t+1} = β₀ + β₁·o_t + β₂·o_t(o_t − 1), par variables instrumentales : régresseurs
    (1, o_t, o_t(o_t − 1)), instruments (1, z_t, z_t(z_t − 1)) avec z = autre canal (moments factoriels,
    proposition 8). Lève une erreur si le système est singulier.

    `effets_temporels=True` : retire à chaque instant la moyenne transversale de chaque variable (y_{t+1}, x_t,
    x_t(x_t−1), z_t, z_t(z_t−1)) ; la constante n'est alors pas identifiée (β₀ = NaN). Retire les chocs communs,
    mais aussi une vague réellement nationale.
    """
    x = o_sortie[:-1]
    z = o_instrument[:-1]
    y = o_sortie[1:]
    ok = ~np.isnan(x) & ~np.isnan(z) & ~np.isnan(y)
    if ok.sum() < 3:
        raise ValueError("Moins de 3 observations complètes : estimation impossible.")
    if effets_temporels:
        colonnes = []
        for v in (y, x, x * (x - 1), z, z * (z - 1)):
            w = np.where(ok, v, np.nan)
            colonnes.append(_retirer_moyenne_par_instant(w)[ok & (ok.sum(axis=1, keepdims=True) >= 3)])
        yd, xd, x2d, zd, z2d = colonnes
        X = np.stack([xd, x2d], axis=1)
        Z = np.stack([zd, z2d], axis=1)
        try:
            b = np.linalg.solve(Z.T @ X, Z.T @ yd)
        except np.linalg.LinAlgError as e:
            raise ValueError("Instruments colinéaires : estimation impossible.") from e
        return float("nan"), float(b[0]), float(b[1])
    x, z, y = x[ok], z[ok], y[ok]
    X = np.stack([np.ones_like(x), x, x * (x - 1)], axis=1)
    Z = np.stack([np.ones_like(z), z, z * (z - 1)], axis=1)
    try:
        b = np.linalg.solve(Z.T @ X, Z.T @ y)
    except np.linalg.LinAlgError as e:
        raise ValueError("Instruments colinéaires : estimation impossible.") from e
    return float(b[0]), float(b[1]), float(b[2])


@dataclass(frozen=True)
class EstimationMulticanal:
    """Paramètres en unités VRAIES (non observées) : μ, a, c, R, m₋ et Φ, sans connaître aucun taux de détection."""

    mu: float
    a: float
    c: float
    R: float
    m_bas: float
    theta: float
    phi: float
    dispersion: float = float("nan")


def estimer_multicanal(O: np.ndarray, sortie: int, instrument: int, calibrage: int, effets_temporels: bool = False) -> EstimationMulticanal:
    """Φ̂ en unités vraies à partir de canaux sous-déclarés (proposition 8).

    `sortie` : canal dont on ajuste la dérive ; `instrument` : canal qui l'instrumente ; `calibrage` : canal qui sert
    à identifier le taux de détection de `sortie`. La note montre que si le canal de calibrage est sous boucle de
    surveillance, θ̂ est faussé et l'on obtient une fausse alerte ; avec trois canaux dont deux indépendants,
    instrumenter par le canal surveillé reste robuste (voir les tests).
    """
    b0, b1, b2 = derive_instrumentee(O[sortie], O[instrument], effets_temporels)
    theta = taux_detection(O[sortie], O[calibrage])
    c = b2 * theta
    a = b1 - c
    m_bas = float(np.nanmean(O[sortie]) / theta)
    R = a + 2.0 * c * m_bas
    return EstimationMulticanal(b0 / theta, a, c, R, m_bas, theta, _phi_ou_cas_limite(R, c, m_bas))


def estimer_deux_canaux_avec_dispersion(O: np.ndarray, sortie: int = 1, autre: int = 0) -> EstimationMulticanal:
    """Φ̂ et φ̂ à partir de deux canaux sans boucle (propositions 8 et 10).

    φ = [Cov(o^k_{t+1}, o^l_{t+1}) − Cov(o^k_{t+1}, G_t)] / (θ^k θ^l E y_{t+1}) avec G_t la dérive instrumentée.
    Le bruit de mesure disparaît : seul le bruit de la dynamique est mesuré. Φ̂ est alors Φ_Poisson / φ̂ (prop. 3 iv).
    """
    l, k = sortie, autre
    b0, b1, b2 = derive_instrumentee(O[l], O[k])
    theta_l = taux_detection(O[l], O[k])
    theta_k = theta_l * np.nanmean(O[k]) / np.nanmean(O[l])
    c = b2 * theta_l
    a = b1 - c
    m_bas = float(np.nanmean(O[l]) / theta_l)
    R = a + 2.0 * c * m_bas
    G = b0 + b1 * O[l][:-1] + b2 * O[l][:-1] * (O[l][:-1] - 1)
    o_k1, o_l1 = O[k][1:], O[l][1:]
    m = _masque(G, o_k1, o_l1)
    A, B, Gm = o_k1[m], o_l1[m], G[m]
    numerateur = np.cov(A, B)[0, 1] - np.cov(A, Gm)[0, 1]
    dispersion = float(numerateur / (theta_k * theta_l * np.nanmean(o_l1) / theta_l))
    base = _phi_ou_cas_limite(R, c, m_bas)
    phi = base / dispersion if (c > 0 and R < 1 and dispersion > 0) else (0.0 if R >= 1 else float("inf"))
    return EstimationMulticanal(b0 / theta_l, a, c, R, m_bas, float(theta_l), float(phi), dispersion)


# ---------------------------------------------------------------------------------------------------------
# Signaux continus : capteurs affines (proposition 14, scripts `g3`)
# ---------------------------------------------------------------------------------------------------------


def _quadratique_ols(ol: np.ndarray):
    u = ol[:-1].ravel()
    v = ol[1:].ravel()
    ok = ~np.isnan(u) & ~np.isnan(v)
    return u[ok], v[ok]


def estimer_vstar_un_capteur(ol: np.ndarray) -> float:
    """V* « naïf » à partir d'un seul capteur : ajustement quadratique par MCO, bruit = écart-type des résidus.

    Le bruit de mesure est pris pour du bruit de dynamique : la note montre une surestimation de 5 à 15 fois
    (donc des temps d'attente surestimés de plusieurs ordres de grandeur). Renvoie +∞ si aucun seuil n'est détecté.
    """
    u, v = _quadratique_ols(ol)
    X = np.stack([np.ones_like(u), u, u * u], axis=1)
    b = np.linalg.lstsq(X, v, rcond=None)[0]
    sigma = float(np.std(v - X @ b))
    F = lambda z: b[0] + b[1] * z + b[2] * z * z  # noqa: E731
    racines = zeros_de_derive(F, np.nanmin(ol) - 5 * abs(np.nanstd(ol)), np.nanmax(ol) + 20 * np.nanstd(ol))
    if len(racines) < 2:
        return float("inf")
    return vstar_gaussien(F, sigma, racines[0], racines[1])


def estimer_vstar_deux_capteurs(O: np.ndarray, l: int = 0, k: int = 1) -> float:
    """V* dans les unités du capteur `l`, à partir de deux capteurs affines indépendants (proposition 14), sans
    connaître ni gains, ni décalages, ni bruits de mesure :

    1. dérive quadratique par variables instrumentales (régresseurs 1, o_t, o_t² ; instruments 1, z_t, z_t²) ;
    2. rapport des gains g_k/g_l = Cov(o^k_{t+1}, o^l_{t−1}) / Cov(o^l_{t+1}, o^l_{t−1}) ;
    3. bruit de mesure η_l²·g_l² = Var(o^l) − Cov(o^l, o^k)·g_l/g_k, qui corrige la constante de la dérive ;
    4. bruit dynamique g_l²σ² = [Cov(o^k_{t+1}, o^l_{t+1}) − Cov(o^k_{t+1}, G_t)]·g_l/g_k.

    Renvoie NaN si l'estimation échoue (moins de 2 points fixes, bruit dynamique estimé ≤ 0).
    """
    ol, ok_ = O[l], O[k]
    u = ol[:-1].ravel()
    z = ok_[:-1].ravel()
    v = ol[1:].ravel()
    m = ~np.isnan(u) & ~np.isnan(z) & ~np.isnan(v)
    u, z, v = u[m], z[m], v[m]
    X = np.stack([np.ones_like(u), u, u * u], axis=1)
    Z = np.stack([np.ones_like(z), z, z * z], axis=1)
    try:
        b = np.linalg.solve(Z.T @ X, Z.T @ v)
    except np.linalg.LinAlgError:
        return float("nan")
    A, B, C = ok_[2:].ravel(), ol[2:].ravel(), ol[:-2].ravel()
    mm = ~np.isnan(A) & ~np.isnan(B) & ~np.isnan(C)
    rapport = np.cov(A[mm], C[mm])[0, 1] / np.cov(B[mm], C[mm])[0, 1]
    P, Q = ol.ravel(), ok_.ravel()
    mm2 = ~np.isnan(P) & ~np.isnan(Q)
    eta2 = P[mm2].var() - np.cov(P[mm2], Q[mm2])[0, 1] / rapport
    b0 = b[0] + b[2] * eta2
    G = b[0] + b[1] * ol[:-1] + b[2] * ol[:-1] ** 2
    K1, L1 = ok_[1:], ol[1:]
    mm3 = ~np.isnan(G) & ~np.isnan(K1) & ~np.isnan(L1)
    s2 = (np.cov(K1[mm3], L1[mm3])[0, 1] - np.cov(K1[mm3], G[mm3])[0, 1]) / rapport
    F = lambda w: b0 + b[1] * w + b[2] * w * w  # noqa: E731
    lo, hi = np.nanmin(ol), np.nanmax(ol)
    etendue = hi - lo
    racines = zeros_de_derive(F, lo - 3 * etendue, hi + 10 * etendue)
    if len(racines) < 2 or not s2 > 0:
        return float("nan")
    return vstar_gaussien(F, float(np.sqrt(max(s2, 1e-12))), racines[0], racines[1])
