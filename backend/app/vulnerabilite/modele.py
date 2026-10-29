"""Le modèle de contagion complexe et ses grandeurs (note, sections 1 et 7).

F(y) = μ + a·y + c·y² : moyenne conditionnelle du pas suivant. Deux points fixes m₋ (calme, stable) et
m₊ (seuil, instable) ; étincelle critique s* = m₊ − m₋ ; inflammabilité R = F'(m₋) ; identité R = 1 − c·s*.
L'indice Φ approche le logarithme du temps moyen avant embrasement spontané.

Statuts : voir la note. Les identités (points fixes, R = 1 − c s*, barrière c s*³/6, formes closes de Φ)
sont démontrées ; la loi des temps (prop. 4) est une approximation vérifiée numériquement.
"""
from __future__ import annotations

from typing import Callable

import numpy as np
from scipy.integrate import quad
from scipy.optimize import brentq

#: Constante de la loi des temps E[T] ≈ C·2π/(1−R)·e^Φ (note, prop. 4 : ln C = 1,21 ± 0,37, soit C ≈ 3,4).
CONSTANTE_KRAMERS = 3.4


def reponse_moyenne(y, a: float, mu: float, c: float):
    """F(y) = μ + a·y + c·y²."""
    return mu + a * y + c * y * y


def params_depuis_inflammabilite(R: float, c: float, m_bas: float) -> tuple[float, float, float, float]:
    """(R, c, m₋) → (a, μ, s*, m₊).

    Raises:
        ValueError: hors du domaine du modèle (c ≤ 0, R ≥ 1, m₋ ≤ 0), ou si a < 0 (contagion simple négative).
    """
    if not c > 0:
        raise ValueError("La courbure c doit être strictement positive (c = 0 : pas de seuil fini).")
    if not R < 1:
        raise ValueError("L'inflammabilité R doit être inférieure à 1 (sinon il n'y a plus d'état calme).")
    if not m_bas > 0:
        raise ValueError("Le niveau calme m₋ doit être strictement positif.")
    s_etoile = (1.0 - R) / c
    a = R - 2.0 * c * m_bas
    if a < -1e-12:
        raise ValueError(f"Paramètres inadmissibles : a = R − 2·c·m₋ = {a:.4g} < 0.")
    a = max(a, 0.0)  # borne a = 0 atteinte à l'arrondi près (ex. R = 0,6, c = 0,1, m₋ = 3)
    mu = c * m_bas * (m_bas + s_etoile)
    return a, mu, s_etoile, m_bas + s_etoile


def points_fixes(a: float, mu: float, c: float) -> tuple[float, float] | None:
    """(m₋, m₊), ou None si Δ = (1−a)² − 4cμ < 0 (embrasement certain)."""
    delta = (1.0 - a) ** 2 - 4.0 * c * mu
    if delta < 0:
        return None
    racine = np.sqrt(delta)
    return ((1.0 - a) - racine) / (2.0 * c), ((1.0 - a) + racine) / (2.0 * c)


def inflammabilite(a: float, c: float, m_bas: float) -> float:
    """R = F'(m₋) = a + 2·c·m₋."""
    return a + 2.0 * c * m_bas


def identite_inflammabilite(c: float, s_etoile: float) -> float:
    """R = 1 − c·s* (proposition 2)."""
    return 1.0 - c * s_etoile


def barriere_additive(c: float, s_etoile: float) -> float:
    """ΔU = c·s*³/6, barrière de potentiel pour un bruit additif."""
    return c * s_etoile**3 / 6.0


def phi_poisson(R: float, c: float, m_bas: float, controle_a: bool = True) -> float:
    """Φ en forme close pour un bruit de Poisson : (1−a)·s* − 2μ·ln(m₊/m₋) (proposition 3 (i)).

    `controle_a=False` autorise a < 0 : c'est ce qu'exige l'estimation, où (R̂, ĉ, m̂₋) sont des
    estimations bruitées et où la note calcule quand même Φ̂ par la même formule (scripts `core.phi`).
    """
    if controle_a:
        a, mu, s_etoile, m_haut = params_depuis_inflammabilite(R, c, m_bas)
    else:
        if not (c > 0 and R < 1 and m_bas > 0):
            raise ValueError("Φ n'est défini que pour c > 0, R < 1 et m₋ > 0.")
        s_etoile = (1.0 - R) / c
        a = R - 2.0 * c * m_bas
        mu = c * m_bas * (m_bas + s_etoile)
        m_haut = m_bas + s_etoile
    return (1.0 - a) * s_etoile - 2.0 * mu * np.log(m_haut / m_bas)


def phi_surdispersion(R: float, c: float, m_bas: float, dispersion: float) -> float:
    """Φ_φ = Φ_Poisson / φ (proposition 3 (iv))."""
    if not dispersion > 0:
        raise ValueError("La dispersion φ doit être strictement positive.")
    return phi_poisson(R, c, m_bas) / dispersion


def phi_gaussien(c: float, s_etoile: float, sigma2: float) -> float:
    """Φ = c·s*³/(3σ²) pour un bruit additif de variance σ² (proposition 3 (ii))."""
    return c * s_etoile**3 / (3.0 * sigma2)


def phi_numerique(
    a: float,
    mu: float,
    c: float,
    variance: Callable[[float], float] = lambda m: m,
) -> float:
    """Φ = 2·∫ −f(m)/v(m) dm entre m₋ et m₊, par quadrature (f = F − id). v(m) = m par défaut (Poisson)."""
    pts = points_fixes(a, mu, c)
    if pts is None:
        raise ValueError("Pas d'état calme : Δ < 0.")
    m_bas, m_haut = pts
    valeur, _ = quad(lambda m: -2.0 * (reponse_moyenne(m, a, mu, c) - m) / variance(m), m_bas, m_haut)
    return valeur


def phi_petit_c(R: float, c: float) -> float:
    """Premier terme de Φ quand c → 0 à (R, m₋) fixés : (1−R)²/c (proposition 3 (iii))."""
    return (1.0 - R) ** 2 / c


def loi_pres_du_pli(lam: float, c: float, sigma2: float) -> float:
    """V* ≈ (1−λ)³ / (3·c²·σ²) près d'un pli, bruit à variance à peu près constante (corollaire CG)."""
    return (1.0 - lam) ** 3 / (3.0 * c * c * sigma2)


def temps_moyen_predit(R: float, phi: float, constante: float = CONSTANTE_KRAMERS) -> float:
    """E[T] ≈ C·2π/(1−R)·e^Φ (proposition 4)."""
    return constante * 2.0 * np.pi / (1.0 - R) * np.exp(phi)


def zeros_de_derive(reponse: Callable[[np.ndarray], np.ndarray], bas: float, haut: float, n: int = 40001) -> list[float]:
    """Points fixes de `reponse` (zéros de F − id) sur [bas, haut], par balayage puis méthode de Brent."""
    xs = np.linspace(bas, haut, n)
    valeurs = reponse(xs) - xs
    # zéro exactement sur la grille : on le garde une fois ; changement de signe strict ailleurs
    # (un `sign(a) != sign(b)` compterait deux fois un zéro tombé sur un nœud)
    racines = [float(xs[i]) for i in np.where(valeurs == 0.0)[0]]
    indices = np.where(valeurs[:-1] * valeurs[1:] < 0)[0]
    racines += [brentq(lambda x: float(reponse(np.asarray(x)) - x), xs[i], xs[i + 1]) for i in indices]
    return sorted(racines)


def ecart_identite_generale(
    reponse: Callable[[np.ndarray], np.ndarray],
    derivee: Callable[[np.ndarray], np.ndarray],
    derivee_seconde: Callable[[np.ndarray], np.ndarray],
    bas: float = -4.0,
    haut: float = 4.0,
) -> dict:
    """Identité générale près d'un pli (proposition PG1) : λ = F'(m₋) = 1 − c·s* + O(s*²), c = F''(m₋)/2.

    Retourne s*, λ exact, c et l'écart |λ − (1 − c·s*)|. L'écart décroît comme s*².
    """
    racines = zeros_de_derive(reponse, bas, haut)
    if len(racines) < 2:
        raise ValueError("Pas de bistabilité dans l'intervalle donné.")
    m_bas, m_haut = racines[0], racines[1]
    lam = float(derivee(np.asarray(m_bas)))
    if not (abs(lam) < 1.0 and float(derivee(np.asarray(m_haut))) > 1.0):
        raise ValueError("Configuration inattendue : m₋ n'est pas stable ou m₊ n'est pas instable.")
    s_etoile = m_haut - m_bas
    c = float(derivee_seconde(np.asarray(m_bas))) / 2.0
    return {"s_etoile": s_etoile, "lambda": lam, "c": c, "ecart": abs(lam - (1.0 - c * s_etoile))}
