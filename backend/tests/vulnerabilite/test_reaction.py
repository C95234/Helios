import numpy as np
import pytest

from app.vulnerabilite.reaction import DecompositionReaction, decomposer_reaction
from app.vulnerabilite.simulation import simuler_reaction


def _repetitions(a, kappa, rho, mu, reps=20):
    return [decomposer_reaction(simuler_reaction(a, kappa, rho, mu, 100, 400, np.random.default_rng(i))[0]) for i in range(reps)]


def test_equilibre_de_la_societe_qui_reagit():
    X, y_etoile = simuler_reaction(1.05, 0.02, 0.2, 2.0, 100, 400, np.random.default_rng(0))
    # équilibre : y* = μ + (a − κ·y*)·y*
    assert 2.0 + (1.05 - 0.02 * y_etoile) * y_etoile == pytest.approx(y_etoile)
    assert X.shape == (400, 100) and X.mean() == pytest.approx(y_etoile, rel=0.05)


def test_statut_experimental_et_donnees_incompletes():
    d = decomposer_reaction(simuler_reaction(1.05, 0.02, 0.2, 2.0, 50, 300, np.random.default_rng(1))[0])
    assert isinstance(d, DecompositionReaction) and d.statut == "EXPERIMENTAL"
    X = simuler_reaction(1.05, 0.02, 0.2, 2.0, 10, 50, np.random.default_rng(1))[0]
    X[3, 2] = np.nan
    with pytest.raises(ValueError, match="sans NaN"):
        decomposer_reaction(X)


def test_societe_explosive_tenue_par_sa_reaction():
    """Cahier : A ≈ 0,82 et a ≈ 1,03 (± 0,05) ; la société paraît calme (AC1 ≈ 0,76) mais est intrinsèquement
    explosive (a > 1). Graines de `t8` : 20 répétitions, 100 unités × 400 pas."""
    d = _repetitions(1.05, 0.02, 0.2, 2.0)
    assert np.median([x.A for x in d]) == pytest.approx(0.82, abs=0.05)
    assert np.median([x.a for x in d]) == pytest.approx(1.03, abs=0.05)
    assert np.median([x.ac1_naive for x in d]) == pytest.approx(0.76, abs=0.03)
    assert np.median([x.a for x in d]) > 1.0 > np.median([x.ac1_naive for x in d])
    assert np.median([x.rho for x in d]) == pytest.approx(0.24, abs=0.05)  # vrai : 0,20
    assert np.median([x.B_rho for x in d]) == pytest.approx(0.051, abs=0.01)  # vrai : 0,045
    assert not any(x.fragile for x in d)


def test_reaction_lente_estimation_fragile_a_queue_large():
    d = _repetitions(0.95, 0.01, 0.1, 2.0)
    a = np.array([x.a for x in d])
    assert np.median(a) == pytest.approx(0.92, abs=0.05)  # vrai : 0,95
    assert np.percentile(a, 90) > 3.0  # queue large : la note rapporte un décile 90 à 7,9


def test_sans_reaction_a_n_est_pas_identifiable():
    d = _repetitions(0.70, 0.0, 0.1, 3.6)
    assert np.median([x.A for x in d]) == pytest.approx(0.70, abs=0.03)
    assert abs(np.median([x.B_rho for x in d])) < 0.01
    a = np.array([x.a for x in d])
    assert np.percentile(a, 90) - np.percentile(a, 10) > 1.0  # note : de −1,56 à 4,11
    assert sum(x.fragile for x in d) >= len(d) // 2  # drapeau levé la plupart du temps
