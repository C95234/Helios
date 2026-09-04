"""Simulateur de synchronisation (Kuramoto) + controle adaptatif -- H4, §5.8.

Module de nature differente de H1-H3 : une DEMONSTRATION DE PRINCIPE en
simulation, jamais un test statistique contre des donnees reelles. Aucun
verdict "confirmee/infirmee" ne doit jamais etre attache a ces resultats.

Modele (N oscillateurs de phase theta_i, frequence propre omega_i) :
    dtheta_i/dt = omega_i + (K/N) * sum_j sin(theta_j - theta_i)

Parametre d'ordre (synchronisation globale, r in [0,1]) :
    r * e^{i*psi} = (1/N) * sum_j e^{i*theta_j}

Couplage adaptatif (RCA, §5.8) : au lieu d'un K global fixe, chaque paire
(i,j) a son propre K_ij(t) qui diminue tant que cette paire reste verrouillee
en phase, avec une lente relaxation vers K_base pour continuer a "sonder" le
couplage plutot que de decoupler definitivement -- fidele a l'esprit du
roman : ne pas supprimer les turbulences locales, empecher seulement leur
synchronisation globale.

Adaptation Helios par rapport au §5.8 : le cahier des charges decrit une
regle proportionnelle a -beta * d|theta_i-theta_j|/dt, activee "quand cet
ecart se reduit trop vite". Prise au pied de la lettre, cette regle ne
declenche que pendant le bref transitoire d'approche du verrouillage : une
fois la paire verrouillee (l'ecart de phase devient quasi constant, sa
derivee tombe a 0), plus rien ne s'oppose a la relaxation vers K_base, et la
paire se reverrouille. Le principe est donc traduit ici par une suppression
active et CONTINUE tant que la paire reste verrouillee, mesuree par la
vitesse angulaire relative |theta_dot_i - theta_dot_j| (proche de 0 = paire
verrouillee, grande = paire libre) plutot que par la derivee de l'ecart de
phase seule -- meme principe (desynchroniser les paires qui s'accrochent),
mecanisme rendu effectif en regime etabli.
"""
from __future__ import annotations

import numpy as np


def critical_coupling(sigma: float = 1.0) -> float:
    """K_c = 2 / (pi * g(0)) pour omega ~ Normal(0, sigma^2) (§5.8)."""
    g0 = 1.0 / (sigma * np.sqrt(2 * np.pi))
    return 2.0 / (np.pi * g0)


def order_parameter(theta: np.ndarray) -> float:
    """r = |mean(e^{i*theta})|."""
    return float(np.abs(np.mean(np.exp(1j * theta))))


def simulate_uncontrolled(
    n: int,
    k: float,
    duration: float,
    dt: float,
    sigma: float = 1.0,
    seed: int | None = None,
    adjacency: np.ndarray | None = None,
) -> dict:
    """Kuramoto standard, couplage global K fixe -- pas de controle.

    `adjacency` (N x N, 0/1, diagonale nulle) restreint le couplage aux
    paires reellement voisines, avec normalisation par le degre plutot que
    par N -- modele Kuramoto sur reseau, cf. `simulate_h4(network="real")`
    qui y passe le reseau reel des departements (§5.8, adaptation). Laisse a
    None : comportement inchange (champ moyen, tous connectes).
    """
    rng = np.random.default_rng(seed)
    omega = rng.normal(0, sigma, size=n)
    theta = rng.uniform(0, 2 * np.pi, size=n)

    if adjacency is not None:
        degree = adjacency.sum(axis=1)
        degree_safe = np.where(degree > 0, degree, 1.0)

    n_steps = int(duration / dt)
    r_series = np.empty(n_steps)

    for step in range(n_steps):
        diffs = theta[None, :] - theta[:, None]  # theta_j - theta_i, shape (i, j)
        if adjacency is None:
            coupling = (k / n) * np.sum(np.sin(diffs), axis=1)
        else:
            coupling = (k / degree_safe) * np.sum(adjacency * np.sin(diffs), axis=1)
        theta = theta + dt * (omega + coupling)
        r_series[step] = order_parameter(theta)

    return {"r": r_series, "omega": omega}


def simulate_adaptive_control(
    n: int,
    k_base: float,
    r_target: float,
    beta: float,
    duration: float,
    dt: float,
    sigma: float = 1.0,
    recovery_rate: float | None = None,
    seed: int | None = None,
    adjacency: np.ndarray | None = None,
) -> dict:
    """Couplage adaptatif par paire : K_ij decroit (multiplicativement) tant
    que la paire (i,j) reste verrouillee en phase, avec relaxation lente vers
    K_base pour continuer a "sonder" le couplage (voir note d'adaptation
    dans le docstring du module).

    `r_target` (r_c dans le cahier des charges) n'entre pas directement dans
    la regle locale -- c'est le RESULTAT emergent vise, pas un seuil dans
    l'equation. beta controle la force de la suppression locale ; plus beta
    est grand, plus une paire verrouillee est decouplee vite.

    `adjacency` (N x N, 0/1, diagonale nulle), si fourni, restreint le
    couplage adaptatif aux paires reellement voisines (les autres restent a
    K_ij=0 en permanence) et normalise par le degre plutot que par N --
    meme reseau reel que celui passe a `simulate_uncontrolled`.
    """
    if recovery_rate is None:
        recovery_rate = beta / 10.0

    rng = np.random.default_rng(seed)
    omega = rng.normal(0, sigma, size=n)
    theta = rng.uniform(0, 2 * np.pi, size=n)
    K = np.full((n, n), k_base, dtype=float)
    np.fill_diagonal(K, 0.0)
    if adjacency is not None:
        K = K * adjacency
        degree = adjacency.sum(axis=1)
        degree_safe = np.where(degree > 0, degree, 1.0)

    n_steps = int(duration / dt)
    r_series = np.empty(n_steps)
    mean_k_series = np.empty(n_steps)

    for step in range(n_steps):
        diffs = theta[None, :] - theta[:, None]  # theta_j - theta_i
        if adjacency is None:
            coupling = (1.0 / n) * np.sum(K * np.sin(diffs), axis=1)
        else:
            coupling = (1.0 / degree_safe) * np.sum(K * np.sin(diffs), axis=1)
        theta_dot = omega + coupling
        theta = theta + dt * theta_dot

        # vitesse angulaire relative |theta_dot_i - theta_dot_j| : proche de 0 <=> paire verrouillee.
        rel_speed = np.abs(theta_dot[:, None] - theta_dot[None, :])
        lock_strength = np.clip(1.0 - rel_speed / sigma, 0.0, 1.0)

        K = K * (1.0 - beta * lock_strength * dt) + recovery_rate * dt * (k_base - K)
        np.clip(K, 0.0, k_base, out=K)
        np.fill_diagonal(K, 0.0)
        if adjacency is not None:
            K = K * adjacency  # les paires non voisines restent decouplees en permanence

        r_series[step] = order_parameter(theta)
        if adjacency is None:
            mean_k_series[step] = float(np.mean(K[~np.eye(n, dtype=bool)]))
        else:
            n_edges = adjacency.sum()
            mean_k_series[step] = float(np.sum(K) / n_edges) if n_edges > 0 else 0.0

    return {"r": r_series, "mean_k": mean_k_series, "omega": omega}
