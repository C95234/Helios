"""EXPÉRIMENTAL — V* à deux capteurs affines pour une dérive CUBIQUE (double puits), généralisation de la proposition 14 de la note.

La note traite une dérive quadratique (un état calme, un seuil). Un système à deux états (stade froid, interstadiaire chaud) a une dérive cubique : trois points
fixes, deux stables et une selle entre eux. Hors périmètre de la note : AUCUN résultat de ce module n'est établi par elle ; sa validité n'est étudiée que par simulation
(phase 1c du banc Dansgaard-Oeschger, `docs/vulnerabilite/phase_1c_criteres.md`).

Modèle : x_{t+1} = F(x_t) + σ·ε, F cubique ; capteurs o^k_t = g_k·x_t + b_k + bruit de mesure indépendant. Dans les unités du capteur l (et après standardisation, V* étant
invariant par changement affine d'unités) :
1. P(u) = E[o^l_{t+1} | u_t] cubique, par variables instrumentales : régresseurs (1, o, o², o³) du capteur l, instruments (1, z, z², z³) de l'autre capteur ;
2. rapport des gains g_k/g_l = Cov(o^k_{t+2}, o^l_t)/Cov(o^l_{t+2}, o^l_t) ;
3. variance du bruit de mesure s² = Var(o^l) − Cov(o^l, o^k)·g_l/g_k ; correction des biais : p₀ = β₀ + β₂·s², p₁ = β₁ + 3·β₃·s², p₂ = β₂, p₃ = β₃
   (car E[o²|u] = u² + s² et E[o³|u] = u³ + 3·s²·u) ;
4. variance de la dynamique σ² = [Cov(o^k_{t+1}, o^l_{t+1}) − Cov(o^k_{t+1}, G_t)]·g_l/g_k avec G_t = β·puissances(o^l_t) ;
5. V* = coût minimal (bruit gaussien) pour aller du puits occupé en fin de fenêtre jusqu'à la selle.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .modele import zeros_de_derive
from .vstar import vstar_gaussien

N_NOEUDS = 400


@dataclass(frozen=True)
class DeriveCubique:
    """Coefficients de P(u) = p0 + p1·u + p2·u² + p3·u³ dans les unités standardisées du capteur l, bruit de la dynamique et de mesure."""

    p: tuple[float, float, float, float]
    sigma_dynamique: float
    variance_mesure: float
    rapport_gains: float
    moyenne: float  # moyenne du capteur l utilisée pour la standardisation
    echelle: float  # écart-type du capteur l utilisé pour la standardisation

    def reponse(self, u):
        p0, p1, p2, p3 = self.p
        return p0 + p1 * u + p2 * u**2 + p3 * u**3


def _paires(*tableaux):
    ok = np.ones(tableaux[0].shape, bool)
    for t in tableaux:
        ok &= ~np.isnan(t)
    return ok


def estimer_derive_cubique(O: np.ndarray, l: int = 0, k: int = 1) -> DeriveCubique:
    """Estime la dérive cubique à partir de deux capteurs O[l], O[k] de forme (n_pas, n_unites). Lève ValueError si l'estimation est impossible."""
    ol0, ok0 = np.asarray(O[l], dtype=float), np.asarray(O[k], dtype=float)
    m, s = float(np.nanmean(ol0)), float(np.nanstd(ol0))
    mk, sk = float(np.nanmean(ok0)), float(np.nanstd(ok0))
    if not (s > 0 and sk > 0):
        raise ValueError("Capteur constant : estimation impossible.")
    ol, ok = (ol0 - m) / s, (ok0 - mk) / sk
    x, z, y = ol[:-1], ok[:-1], ol[1:]
    mask = _paires(x, z, y)
    if mask.sum() < 20:
        raise ValueError("Moins de 20 observations complètes : estimation impossible.")
    xs, zs, ys = x[mask], z[mask], y[mask]
    X = np.stack([np.ones_like(xs), xs, xs**2, xs**3], axis=1)
    Z = np.stack([np.ones_like(zs), zs, zs**2, zs**3], axis=1)
    try:
        beta = np.linalg.solve(Z.T @ X, Z.T @ ys)
    except np.linalg.LinAlgError as e:
        raise ValueError("Instruments colinéaires : estimation impossible.") from e
    # rapport des gains (covariances décalées de deux pas)
    a, b, c = ok[2:], ol[2:], ol[:-2]
    mm = _paires(a, b, c)
    if mm.sum() < 10:
        raise ValueError("Pas assez de paires décalées de deux pas.")
    denom = np.cov(b[mm], c[mm])[0, 1]
    if abs(denom) < 1e-12:
        raise ValueError("Rapport des gains non identifiable.")
    rapport = float(np.cov(a[mm], c[mm])[0, 1] / denom)
    if not rapport > 0:
        raise ValueError("Rapport des gains non positif : capteurs de signes opposés ou signal absent.")
    # variance du bruit de mesure du capteur l
    pm = _paires(ol, ok)
    P, Q = ol[pm], ok[pm]
    s2 = float(np.var(P, ddof=1) - np.cov(P, Q)[0, 1] / rapport)
    s2 = max(s2, 0.0)
    p = (beta[0] + beta[2] * s2, beta[1] + 3.0 * beta[3] * s2, beta[2], beta[3])
    # variance de la dynamique
    G = beta[0] + beta[1] * x + beta[2] * x**2 + beta[3] * x**3
    K1, L1 = ok[1:], ol[1:]
    m3 = _paires(G, K1, L1)
    var_dyn = float((np.cov(K1[m3], L1[m3])[0, 1] - np.cov(K1[m3], G[m3])[0, 1]) / rapport)
    if not var_dyn > 0:
        raise ValueError("Variance de la dynamique estimée négative ou nulle.")
    return DeriveCubique(tuple(float(v) for v in p), float(np.sqrt(var_dyn)), s2, rapport, m, s)


def points_fixes_double_puits(d: DeriveCubique, bas: float = -6.0, haut: float = 6.0):
    """(puits gauche, selle, puits droit) si la dérive a trois points fixes avec deux stables encadrant une selle instable ; None sinon."""
    racines = zeros_de_derive(d.reponse, bas, haut, 20001)
    if len(racines) != 3:
        return None
    r1, r2, r3 = racines

    def pente(r):
        p0, p1, p2, p3 = d.p
        return p1 + 2 * p2 * r + 3 * p3 * r * r

    if abs(pente(r1)) < 1 and pente(r2) > 1 and abs(pente(r3)) < 1:
        return r1, r2, r3
    return None


def vstar_double_puits(d: DeriveCubique, etat_standardise: float, n_noeuds: int = N_NOEUDS) -> float:
    """V* depuis le puits le plus proche de `etat_standardise` (état en fin de fenêtre, en unités standardisées du capteur l) jusqu'à la selle.
    NaN si la dérive n'a pas la structure d'un double puits. Si le puits occupé est le puits droit, on réfléchit l'axe (w → −w) : V* est inchangé."""
    pts = points_fixes_double_puits(d)
    if pts is None:
        return float("nan")
    r1, r2, r3 = pts
    if etat_standardise < r2:
        m_bas, m_haut, haut, bas = r1, r2, r2 + (r3 - r2), r1 - 2.0 * (r2 - r1)
        F = d.reponse
    else:
        m_bas, m_haut, haut, bas = -r3, -r2, -r2 + (r2 - r1), -r3 - 2.0 * (r3 - r2)
        F = lambda w: -d.reponse(-np.asarray(w))  # noqa: E731
    try:
        return vstar_gaussien(F, d.sigma_dynamique, m_bas, m_haut, bas=bas, haut=haut, n_noeuds=n_noeuds)
    except ValueError:
        return float("nan")


def v_etoile_fenetre(O: np.ndarray, l: int = 0, k: int = 1, n_derniers: int = 5) -> float:
    """V* d'une fenêtre : estime la dérive, prend l'état moyen des `n_derniers` derniers points du capteur l, calcule V*. NaN si l'estimation échoue."""
    try:
        d = estimer_derive_cubique(O, l, k)
    except ValueError:
        return float("nan")
    fin = np.nanmean(np.asarray(O[l], dtype=float)[-n_derniers:])
    return vstar_double_puits(d, (fin - d.moyenne) / d.echelle)
