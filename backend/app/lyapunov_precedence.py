"""Precedence variance/Moran sur un reseau d'oscillateurs approchant une
bifurcation -- cahier des charges §5.6bis a §5.6quinquies, §7bis.

Ce module N'EST PAS expose par l'API produit : c'est l'outil de recherche
qui a precede et motive H3 (§5.6), reproductible comme test de
non-regression (§7bis point 5) et reutilisable pour l'etendre a un reseau
reel et a des donnees historiques reelles (§7bis, "instructions pour la
suite").

Partie retenue ici : la validation Monte-Carlo sur un vrai basculement
(§5.6quater/quinquies -- bifurcation noeud-col, couplage diffusif et non
diffusif). C'est celle que le cahier des charges designe lui-meme comme la
plus solide (la partie lineaire stationnaire §5.6bis/ter ne fait
qu'approcher l'instabilite sans jamais vraiment basculer).

Adaptation Helios -- calibration non specifiee par le cahier des charges :
le document donne le modele (equation, N=40, beta=0.6, sigma=1, mu de -2
a au-dela de 0, seuil de detection a 3 ecarts-types) et le RESULTAT
(basculement vers t=406, precedence 80%/90%), mais pas le pas de temps, la
fenetre de detection, ni le point de reference de la ligne de base. Avec
sigma=1 tel quel et un pas d'integration Euler-Maruyama simple, le bruit
fait basculer le systeme tres tot (des t~230), bien avant l'approche
theorique de la bifurcation (t=400) : soit le sigma documente suit une
autre convention d'echelle, soit une autre methode d'integration est
utilisee. Calibre ici empiriquement (sigma=0.2, dt=0.01) pour retrouver un
temps de basculement moyen proche de celui documente (~404 contre ~406) --
voir `scripts/lyapunov_precedence_check.py` pour le detail de cette
calibration. L'indice de Moran, tres bruite instant par instant (calcule
sur un seul pas de temps), est lisse par une moyenne glissante avant la
detection de seuil -- sans ce lissage la precedence mesuree est nettement
plus faible et plus instable d'une realisation a l'autre.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

ESCAPE_THRESHOLD = 8.0  # |x_i| au-dela duquel on considere le noeud "echappe"


def ring_weights(n: int) -> np.ndarray:
    W = np.zeros((n, n))
    for i in range(n):
        W[i, (i + 1) % n] = 1
        W[i, (i - 1) % n] = 1
    return W


def laplacian(W: np.ndarray) -> np.ndarray:
    return np.diag(W.sum(axis=1)) - W


def random_irregular_weights(n: int, seed: int, extra_edge_fraction: float = 0.3) -> np.ndarray:
    """Reseau irregulier aleatoire connexe, degre moyen legerement superieur a
    l'anneau : cycle hamiltonien aleatoire (garantit la connexite par
    construction, jamais defaite ensuite) + aretes supplementaires aleatoires
    pour rendre le degre heterogene."""
    rng = np.random.default_rng(seed)
    order = rng.permutation(n)
    W = np.zeros((n, n))
    for i in range(n):
        a, b = order[i], order[(i + 1) % n]
        W[a, b] = W[b, a] = 1
    n_extra = int(n * extra_edge_fraction)
    added = 0
    attempts = 0
    while added < n_extra and attempts < n_extra * 20:
        attempts += 1
        i, j = rng.integers(0, n, size=2)
        if i != j and W[i, j] == 0:
            W[i, j] = W[j, i] = 1
            added += 1
    return W


def morans_i_instant(x: np.ndarray, W: np.ndarray) -> float:
    n = len(x)
    dev = x - x.mean()
    s0 = W.sum()
    den = np.sum(dev ** 2)
    if den == 0 or s0 == 0:
        return 0.0
    num = np.sum(W * np.outer(dev, dev))
    return (n / s0) * (num / den)


def simulate_saddle_node(
    W: np.ndarray,
    beta: float = 0.6,
    sigma: float = 0.2,
    dt: float = 0.01,
    t_max: float = 500.0,
    mu0: float = -2.0,
    mu_rate: float = 0.005,
    coupling: str = "diffusive",
    seed: int = 0,
) -> dict:
    """Bifurcation noeud-col par noeud, couplee sur le reseau de poids W, avec bruit.

    coupling="diffusive" : dx_i = (mu(t) + x_i^2 - beta*(Lx)_i) dt + sigma dW_i (§5.6quater)
    coupling="contagion"  : dx_i = (mu(t) + x_i^2 + beta*sum_j W_ij*tanh(x_j-x_i)) dt + sigma dW_i (§5.6quinquies)
    """
    n = W.shape[0]
    L = laplacian(W)
    rng = np.random.default_rng(seed)
    x = -np.sqrt(-mu0) * np.ones(n) + rng.normal(0, 0.05, n)
    n_steps = int(t_max / dt)

    xbar_hist = np.empty(n_steps)
    moran_hist = np.empty(n_steps)
    t_escape = None
    steps_run = n_steps

    for k in range(n_steps):
        t = k * dt
        mu = mu0 + mu_rate * t
        if coupling == "diffusive":
            coupling_term = -beta * (L @ x)
        else:
            diffs = x[None, :] - x[:, None]  # x_j - x_i
            coupling_term = beta * np.sum(W * np.tanh(diffs), axis=1)
        dx = (mu + x ** 2 + coupling_term) * dt + sigma * np.sqrt(dt) * rng.normal(0, 1, n)
        x = x + dx
        xbar_hist[k] = x.mean()
        moran_hist[k] = morans_i_instant(x, W)
        if np.any(np.abs(x) > ESCAPE_THRESHOLD):
            t_escape = t
            steps_run = k + 1
            break

    xbar_hist, moran_hist = xbar_hist[:steps_run], moran_hist[:steps_run]
    times = np.arange(steps_run) * dt
    return {"times": times, "xbar": xbar_hist, "moran_instant": moran_hist, "t_escape": t_escape}


def detect_precedence(
    times: np.ndarray,
    xbar: np.ndarray,
    moran_instant: np.ndarray,
    dt: float,
    window_time: float = 8.0,
    baseline_time: float = 150.0,
    k_sigma: float = 3.0,
) -> dict:
    """Variance glissante de xbar + indice de Moran lisse (moyenne glissante,
    necessaire vu son bruit d'echantillonnage instant par instant), seuil a
    k_sigma ecarts-types au-dessus d'une ligne de base prise avant t=baseline_time
    (loin de la bifurcation) -- §5.6quater : "detection par franchissement de
    seuil (3 ecarts-types au-dessus de la ligne de base)"."""
    window = max(2, int(window_time / dt))
    var_series = pd.Series(xbar).rolling(window, min_periods=2).var(ddof=1).to_numpy()
    moran_series = pd.Series(moran_instant).rolling(window, min_periods=2).mean().to_numpy()
    baseline_idx = min(int(baseline_time / dt), len(times) - 5)

    def crossing(series):
        baseline = series[:baseline_idx]
        baseline = baseline[~np.isnan(baseline)]
        if len(baseline) < 5:
            return None
        thresh = baseline.mean() + k_sigma * baseline.std()
        tail = series[baseline_idx:]
        above = np.where(~np.isnan(tail) & (tail > thresh))[0]
        return times[baseline_idx + above[0]] if len(above) else None

    return {"t_var": crossing(var_series), "t_moran": crossing(moran_series)}


def run_precedence_batch(
    W: np.ndarray, coupling: str, n_reps: int = 40, seed0: int = 1000, **sim_kwargs
) -> dict:
    """Reproduit le protocole §5.6quater/quinquies sur le reseau de poids W :
    n_reps realisations Monte-Carlo independantes, comptage de la precedence
    variance -> Moran parmi les realisations qui basculent reellement."""
    records = []
    for i in range(n_reps):
        sim = simulate_saddle_node(W, coupling=coupling, seed=seed0 + i, **sim_kwargs)
        prec = detect_precedence(sim["times"], sim["xbar"], sim["moran_instant"], dt=sim_kwargs.get("dt", 0.01))
        records.append({"seed": seed0 + i, "t_escape": sim["t_escape"], **prec})

    tipped = [r for r in records if r["t_escape"] is not None]
    valid = [r for r in tipped if r["t_var"] is not None and r["t_moran"] is not None]
    n_precedence = sum(1 for r in valid if r["t_var"] < r["t_moran"])
    advance_var = float(np.mean([r["t_escape"] - r["t_var"] for r in valid])) if valid else None
    advance_moran = float(np.mean([r["t_escape"] - r["t_moran"] for r in valid])) if valid else None

    return {
        "coupling": coupling,
        "n_reps": n_reps,
        "n_tipped": len(tipped),
        "n_valid": len(valid),
        "n_precedence": n_precedence,
        "precedence_rate": n_precedence / len(valid) if valid else None,
        "advance_var": advance_var,
        "advance_moran": advance_moran,
        "records": records,
    }
