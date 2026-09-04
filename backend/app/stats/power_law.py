"""Loi de puissance et criticite auto-organisee -- cahier des charges Helios
§5.9, H5.

Methode de Clauset, Shalizi & Newman (2009) : estimation par maximum de
vraisemblance (§5.9.1), puis test de plausibilite par bootstrap
semi-parametrique et comparaison a des modeles alternatifs (§5.9.2) --
jamais un simple ajustement visuel sur un graphe log-log (§5.9, cadrage
honnete : Touboul & Destexhe 2010 montrent que ce dernier produit
regulierement des faux positifs).

Point de rigueur necessaire (pas une simplification) : la comparaison aux
modeles alternatifs (`compare_to_alternatives`) ajuste la log-normale et
l'exponentielle EN TRONQUANT a xmin (support x >= xmin), pas par leur MLE
non tronquee -- sinon la loi de puissance gagne artificiellement presque
toujours, meme sur des donnees generees log-normales : une MLE non
tronquee appliquee seulement a la moitie superieure d'une distribution
sous-estime sa dispersion et biaise la comparaison. Verifie par
`test_compare_to_alternatives_favors_lognormal_on_lognormal_data`.
"""
from __future__ import annotations

import numpy as np
from scipy import optimize, stats

MIN_TAIL_SIZE = 15  # trop peu de points pour une MLE d'exposant fiable en dessous de ce seuil


def _alpha_mle(tail: np.ndarray, xmin: float) -> float:
    """alpha_hat = 1 + n / sum(ln(x_i / xmin)) -- §5.9.1, derivee fermee de la log-vraisemblance."""
    n = len(tail)
    return 1.0 + n / np.sum(np.log(tail / xmin))


def _power_law_ks(tail: np.ndarray, alpha: float, xmin: float) -> float:
    """Statistique de Kolmogorov-Smirnov entre CDF empirique et CDF du modele
    de loi de puissance continue P(X<=x) = 1 - (x/xmin)^(-(alpha-1))."""
    x_sorted = np.sort(tail)
    n = len(x_sorted)
    empirical_cdf = np.arange(1, n + 1) / n
    model_cdf = 1.0 - (x_sorted / xmin) ** (-(alpha - 1.0))
    return float(np.max(np.abs(empirical_cdf - model_cdf)))


def fit_power_law(
    x: np.ndarray,
    xmin_candidates: np.ndarray | None = None,
    max_candidates: int = 100,
    min_tail_size: int = MIN_TAIL_SIZE,
) -> dict:
    """Estime (alpha, xmin) par MLE -- §5.9.1, avec xmin choisi (raffinement
    standard de Clauset et al., necessaire car le §5.9.1 suppose xmin deja
    connu) parmi les valeurs distinctes de x comme celui qui MINIMISE la
    distance de Kolmogorov-Smirnov entre le modele ajuste et les donnees.

    Mise en garde connue de la methode (pas cachee, documentee dans
    l'interface, §5.9 cadrage honnete) : cette recherche automatique de xmin
    peut se rabattre sur un xmin eleve qui ne garde qu'une petite queue de
    donnees, sur laquelle presque n'importe quelle distribution a queue
    lourde ressemble localement a une loi de puissance -- d'ou l'obligation
    de l'etape de comparaison a des modeles alternatifs (§5.9.2 etape 5) sur
    un nombre de points suffisant plutot que de se fier au seul test de
    plausibilite. `xmin_candidates` permet de forcer une recherche restreinte
    (ex. imposer un xmin bas pour garder assez de points en comparaison).
    """
    x = np.asarray(x, dtype=float)
    x = x[x > 0]
    if len(x) < min_tail_size:
        raise ValueError(f"Echantillon trop petit ({len(x)} points, minimum {min_tail_size}).")

    if xmin_candidates is not None:
        candidates = np.asarray(xmin_candidates, dtype=float)
    else:
        candidates = np.unique(x)
        if len(candidates) > max_candidates:
            idx = np.linspace(0, len(candidates) - 1, max_candidates).astype(int)
            candidates = candidates[idx]

    best = None
    for xmin in candidates:
        tail = x[x >= xmin]
        if len(tail) < min_tail_size:
            continue
        alpha = _alpha_mle(tail, xmin)
        if alpha <= 1.0:
            continue
        d = _power_law_ks(tail, alpha, xmin)
        if best is None or d < best["ks_statistic"]:
            best = {"alpha": alpha, "xmin": float(xmin), "ks_statistic": d, "n_tail": len(tail)}

    if best is None:
        raise ValueError("Aucun xmin candidat ne permet un ajustement fiable (echantillon trop petit ou degenere).")
    best["n_total"] = len(x)
    return best


def _sample_synthetic(x: np.ndarray, alpha: float, xmin: float, n: int, rng: np.random.Generator) -> np.ndarray:
    """Bootstrap semi-parametrique CSN : chaque point synthetique reprend, avec
    la meme probabilite que dans les donnees reelles, soit un tirage de la loi
    de puissance ajustee (x >= xmin, par inversion de CDF), soit un
    rééchantillonnage (avec remise) de la partie empirique reelle x < xmin."""
    below = x[x < xmin]
    p_tail = np.mean(x >= xmin)
    draws_tail = rng.random(n) < p_tail

    synthetic = np.empty(n)
    n_tail = int(draws_tail.sum())
    if n_tail > 0:
        u = rng.random(n_tail)
        synthetic[draws_tail] = xmin * (1.0 - u) ** (-1.0 / (alpha - 1.0))
    n_below = n - n_tail
    if n_below > 0:
        if len(below) == 0:
            # aucune donnee reelle sous xmin (xmin = min(x)) -- degenere en tout-loi-de-puissance
            u = rng.random(n_below)
            synthetic[~draws_tail] = xmin * (1.0 - u) ** (-1.0 / (alpha - 1.0))
        else:
            synthetic[~draws_tail] = rng.choice(below, size=n_below, replace=True)
    return synthetic


def bootstrap_plausibility(
    x: np.ndarray,
    alpha: float,
    xmin: float,
    n_synthetic: int = 200,
    max_candidates: int = 40,
    min_tail_size: int = MIN_TAIL_SIZE,
    seed: int | None = None,
) -> dict:
    """Test de plausibilite par bootstrap -- §5.9.2 etapes 3-4 : genere
    `n_synthetic` jeux de donnees a partir du modele ajuste lui-meme,
    reajuste (alpha, xmin) sur chacun, et compare leur propre distance de
    Kolmogorov-Smirnov D_synth a D_obs. p elevee (> 0,1 par convention) =
    modele plausible ; p faible le rejette (meme logique que le test par
    permutation du cours de statistiques, §5 du cahier des charges)."""
    x = np.asarray(x, dtype=float)
    x = x[x > 0]
    observed = _power_law_ks(x[x >= xmin], alpha, xmin)

    rng = np.random.default_rng(seed)
    d_synthetic = np.empty(n_synthetic)
    n_failed = 0
    for i in range(n_synthetic):
        synthetic = _sample_synthetic(x, alpha, xmin, len(x), rng)
        try:
            fit = fit_power_law(synthetic, max_candidates=max_candidates, min_tail_size=min_tail_size)
            d_synthetic[i] = fit["ks_statistic"]
        except ValueError:
            d_synthetic[i] = np.nan
            n_failed += 1

    valid = d_synthetic[~np.isnan(d_synthetic)]
    p_value = float(np.mean(valid >= observed)) if len(valid) > 0 else None

    return {
        "ks_statistic_observed": observed,
        "p_value": p_value,
        "n_synthetic": n_synthetic,
        "n_failed": n_failed,
        "plausible_at_0_1": bool(p_value is not None and p_value > 0.1),
    }


def _lognormal_truncated_logpdf(tail: np.ndarray, mu: float, sigma: float, xmin: float) -> np.ndarray:
    """Densite de la log-normale(mu, sigma) conditionnee a X >= xmin (renormalisee
    par sa fonction de survie en xmin), pour une comparaison de vraisemblance
    equitable avec la loi de puissance (dont le support est deja x >= xmin)."""
    log_survival = stats.norm.logsf(np.log(xmin), loc=mu, scale=sigma)
    return stats.norm.logpdf(np.log(tail), loc=mu, scale=sigma) - np.log(tail) - log_survival


def _fit_lognormal_tail(tail: np.ndarray, xmin: float) -> tuple[float, float]:
    """MLE de la log-normale TRONQUEE a xmin (support x >= xmin) par optimisation
    numerique -- pas de forme fermee pour la log-normale tronquee, contrairement
    a l'exponentielle decalee (`_fit_exponential_tail`). Point de depart : la MLE
    non tronquee (biaisee mais un bon point de depart pour l'optimiseur)."""
    log_tail = np.log(tail)
    mu0, sigma0 = np.mean(log_tail), max(np.std(log_tail), 1e-3)

    def neg_log_likelihood(params: np.ndarray) -> float:
        mu, log_sigma = params
        sigma = np.exp(log_sigma)  # reparametrisation : sigma > 0 sans contrainte explicite
        ll = _lognormal_truncated_logpdf(tail, mu, sigma, xmin)
        if not np.all(np.isfinite(ll)):
            return 1e10
        return -float(np.sum(ll))

    result = optimize.minimize(neg_log_likelihood, x0=[mu0, np.log(sigma0)], method="Nelder-Mead")
    mu_hat, log_sigma_hat = result.x
    return float(mu_hat), float(np.exp(log_sigma_hat))


def _fit_exponential_tail(tail: np.ndarray, xmin: float) -> float:
    """MLE de l'exponentielle decalee (support x >= xmin) : lambda = 1 / moyenne(x - xmin)."""
    shifted_mean = np.mean(tail - xmin)
    return 1.0 / shifted_mean if shifted_mean > 0 else np.inf


def _power_law_logpdf(tail: np.ndarray, alpha: float, xmin: float) -> np.ndarray:
    return np.log(alpha - 1.0) - np.log(xmin) - alpha * np.log(tail / xmin)


def _vuong_test(log_l_power_law: np.ndarray, log_l_alt: np.ndarray) -> dict:
    """Test du rapport de vraisemblance normalise de Vuong (1989), recommande
    par Clauset et al. (2009) pour departager la loi de puissance d'un modele
    alternatif non emboîté. R > 0 favorise la loi de puissance ; le signe
    n'est interpretable que si le resultat est significatif (p < 0,05)."""
    n = len(log_l_power_law)
    diff = log_l_power_law - log_l_alt
    r = float(np.sum(diff))
    sigma = float(np.std(diff))
    if sigma == 0 or n == 0:
        return {"r": r, "p_value": None, "favors_power_law": None}
    z = r / (sigma * np.sqrt(n))
    p_value = float(2 * stats.norm.sf(abs(z)))
    favors_power_law = bool(p_value < 0.05 and z > 0) if p_value is not None else None
    return {"r": r, "z": z, "p_value": p_value, "favors_power_law": favors_power_law}


def compare_to_alternatives(x: np.ndarray, xmin: float, alpha: float) -> dict:
    """Compare le modele de loi de puissance a une log-normale et une
    exponentielle sur la meme queue x >= xmin -- §5.9.2 etape 5, obligatoire
    avant tout verdict : un ajustement "acceptable" au test de plausibilite
    ne veut rien dire si une alternative s'ajuste aussi bien ou mieux."""
    x = np.asarray(x, dtype=float)
    tail = x[(x > 0) & (x >= xmin)]

    log_l_power_law = _power_law_logpdf(tail, alpha, xmin)

    mu, sigma_ln = _fit_lognormal_tail(tail, xmin)
    log_l_lognormal = _lognormal_truncated_logpdf(tail, mu, sigma_ln, xmin)

    rate = _fit_exponential_tail(tail, xmin)
    log_l_exponential = np.log(rate) - rate * (tail - xmin) if np.isfinite(rate) else np.full(len(tail), -np.inf)

    return {
        "lognormal": {
            "mu": mu,
            "sigma": sigma_ln,
            **_vuong_test(log_l_power_law, log_l_lognormal),
        },
        "exponential": {
            "rate": float(rate),
            **_vuong_test(log_l_power_law, log_l_exponential),
        },
    }
