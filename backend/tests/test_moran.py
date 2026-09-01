import numpy as np
import pytest

from app.stats.moran import morans_i, permutation_test


def test_morans_i_matches_hand_computed_chain_example():
    # Chaine 1-2-3-4 (contiguite simple), valeurs = gradient parfait [1,2,3,4].
    # Calcul a la main : xbar=2.5, deviations=[-1.5,-0.5,0.5,1.5], S0=6 (3 aretes x2),
    # numerateur = 2*(0.75 - 0.25 + 0.75) = 2.5, denominateur = 5.0
    # I = (4/6) * (2.5/5.0) = 1/3
    values = np.array([1.0, 2.0, 3.0, 4.0])
    weights = np.array(
        [
            [0, 1, 0, 0],
            [1, 0, 1, 0],
            [0, 1, 0, 1],
            [0, 0, 1, 0],
        ],
        dtype=float,
    )
    assert morans_i(values, weights) == pytest.approx(1 / 3, abs=1e-9)


def test_checkerboard_pattern_gives_strong_negative_autocorrelation():
    # Grille 4x4, damier parfait (+1/-1) : chaque voisin rook a la valeur opposee.
    n = 4
    grid = np.indices((n, n)).sum(axis=0) % 2
    values = np.where(grid == 0, 1.0, -1.0).flatten()

    weights = np.zeros((n * n, n * n))
    for r in range(n):
        for c in range(n):
            i = r * n + c
            for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                rr, cc = r + dr, c + dc
                if 0 <= rr < n and 0 <= cc < n:
                    weights[i, rr * n + cc] = 1

    i_value = morans_i(values, weights)
    assert i_value < -0.9  # damier parfait -> autocorrelation negative quasi maximale


def test_smooth_gradient_gives_strong_positive_autocorrelation():
    n = 4
    values = np.indices((n, n))[1].flatten().astype(float)  # gradient horizontal

    weights = np.zeros((n * n, n * n))
    for r in range(n):
        for c in range(n):
            i = r * n + c
            for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                rr, cc = r + dr, c + dc
                if 0 <= rr < n and 0 <= cc < n:
                    weights[i, rr * n + cc] = 1

    assert morans_i(values, weights) > 0.5


def test_permutation_test_null_mean_matches_theoretical_expectation():
    # Sous H0 (permutation), E[I] = -1/(N-1) -- propriete theorique classique de l'indice de Moran.
    rng = np.random.default_rng(0)
    n = 20
    values = rng.normal(size=n)
    weights = (rng.random((n, n)) < 0.3).astype(float)
    np.fill_diagonal(weights, 0)
    weights = np.maximum(weights, weights.T)  # symetrise

    result = permutation_test(values, weights, n_permutations=2000, seed=1)
    expected_null_mean = -1 / (n - 1)
    assert result["null_mean"] == pytest.approx(expected_null_mean, abs=0.05)
