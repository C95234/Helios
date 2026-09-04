"""Tests pour le module loi de puissance / criticite auto-organisee (H5, §5.9).

Verifie des PROPRIETES connues de la methode (Clauset, Shalizi & Newman,
2009), pas des valeurs figees : la MLE retrouve un exposant connu, le test
de plausibilite accepte une vraie loi de puissance et rejette un imposteur,
la comparaison de modeles favorise le bon modele selon les donnees.
"""
import numpy as np
import pytest

from app.stats.power_law import (
    bootstrap_plausibility,
    compare_to_alternatives,
    fit_power_law,
)


def sample_power_law(n: int, alpha: float, xmin: float, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    u = rng.random(n)
    return xmin * (1.0 - u) ** (-1.0 / (alpha - 1.0))


def test_fit_power_law_recovers_known_exponent():
    x = sample_power_law(n=5000, alpha=2.5, xmin=1.0, seed=1)
    result = fit_power_law(x)
    assert result["alpha"] == pytest.approx(2.5, abs=0.1)
    assert result["xmin"] < 1.3  # doit retrouver un xmin proche du vrai xmin=1.0
    assert result["n_tail"] > 1000


def test_fit_power_law_rejects_too_small_sample():
    with pytest.raises(ValueError):
        fit_power_law(np.array([1.0, 2.0, 3.0]))


def test_fit_power_law_ignores_non_positive_values():
    x = sample_power_law(n=2000, alpha=3.0, xmin=1.0, seed=2)
    x_with_junk = np.concatenate([x, np.array([0.0, -1.0, -5.0])])
    result = fit_power_law(x_with_junk)
    assert result["n_total"] == len(x)  # les valeurs non positives sont exclues avant comptage


def test_bootstrap_plausibility_accepts_true_power_law():
    x = sample_power_law(n=2000, alpha=2.5, xmin=1.0, seed=3)
    fit = fit_power_law(x)
    result = bootstrap_plausibility(x, fit["alpha"], fit["xmin"], n_synthetic=100, seed=3)
    assert result["p_value"] is not None
    assert result["p_value"] > 0.1
    assert result["plausible_at_0_1"] is True


def test_bootstrap_plausibility_rejects_exponential_disguised_as_power_law():
    # xmin force a une valeur basse (garde ~2500/3000 points) : sans cette
    # contrainte, la recherche automatique de xmin se rabat sur une toute
    # petite queue ou presque n'importe quelle distribution ressemble
    # localement a une loi de puissance (limite connue de la methode, voir
    # le docstring de fit_power_law) -- pas ce qu'on veut tester ici.
    rng = np.random.default_rng(4)
    x = rng.exponential(scale=1.0, size=3000) + 0.1  # support strictement positif
    fit = fit_power_law(x, xmin_candidates=[0.5])
    result = bootstrap_plausibility(x, fit["alpha"], fit["xmin"], n_synthetic=100, seed=4)
    assert result["p_value"] is not None
    assert result["p_value"] < 0.1
    assert result["plausible_at_0_1"] is False


def test_compare_to_alternatives_favors_power_law_on_power_law_data():
    x = sample_power_law(n=3000, alpha=2.5, xmin=1.0, seed=5)
    fit = fit_power_law(x)
    comparison = compare_to_alternatives(x, fit["xmin"], fit["alpha"])
    assert comparison["lognormal"]["r"] > 0
    assert comparison["exponential"]["r"] > 0


def test_compare_to_alternatives_favors_lognormal_on_lognormal_data():
    # xmin force (garde ~1500/3000 points, meme raison que le test precedent)
    # : sur une toute petite queue, la log-normale a sigma=1 ressemble
    # localement a une loi de puissance -- exactement la limite de la
    # methode que l'etape de comparaison doit reveler sur un echantillon
    # suffisant, pas sur quelques dizaines de points.
    rng = np.random.default_rng(6)
    x = rng.lognormal(mean=0.0, sigma=1.0, size=3000)
    fit = fit_power_law(x, xmin_candidates=[1.0])
    comparison = compare_to_alternatives(x, fit["xmin"], fit["alpha"])
    # La loi de puissance ne doit PAS l'emporter nettement sur la log-normale
    # quand les donnees sont, par construction, log-normales.
    assert comparison["lognormal"]["r"] < 0
    assert comparison["lognormal"]["favors_power_law"] is not True
