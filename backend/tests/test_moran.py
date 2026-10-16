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


def test_permutation_test_p_value_never_exactly_zero():
    # Meme bug que celui trouve par Bruce Stephenson dans la contribution ewstools
    # (Journal §9) : sans plancher, p = #{null >= observed}/M peut tomber exactement
    # a 0 sur un champ tres structure. Reproduit ici sur un gradient net (le meme
    # type de champ que celui utilise dans la revue externe).
    n = 8
    values = np.arange(n, dtype=float)
    weights = np.zeros((n, n))
    for i in range(n - 1):
        weights[i, i + 1] = weights[i + 1, i] = 1

    result = permutation_test(values, weights, n_permutations=500, seed=0)
    assert result["p_value"] > 0.0
    assert result["p_value"] == pytest.approx(1 / 501, abs=1e-9) or result["p_value"] >= 1 / 501


# -- Defauts trouves par la revue de Thomas Bury sur ewstools (PR #482, 2e tour),
# -- presents a l'identique dans cette implementation avant correction.

from fractions import Fraction  # noqa: E402

from app.lyapunov_precedence import morans_i_instant  # noqa: E402


def _rook_weights(n):
    weights = np.zeros((n * n, n * n))
    for r in range(n):
        for c in range(n):
            for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                rr, cc = r + dr, c + dc
                if 0 <= rr < n and 0 <= cc < n:
                    weights[r * n + c, rr * n + cc] = 1
    return weights


@pytest.mark.parametrize("value", [3.0, 0.1, 0.23, -0.7, 1e6 + 0.1])
@pytest.mark.parametrize("side", [3, 10])
def test_morans_i_constant_field_is_nan(value, side):
    # Une constante non exactement representable (0.1, 0.23...) laisse une moyenne
    # arrondie : chaque ecart est le meme petit nombre non nul, et un test exact
    # `denominator == 0` renvoie I = 1.0 (un faux signal, pas un champ constant).
    assert np.isnan(morans_i(np.full(side * side, value), _rook_weights(side)))


@pytest.mark.parametrize("side", [3, 10])
def test_morans_i_constant_field_is_nan_for_all_two_decimal_constants(side):
    weights = _rook_weights(side)
    for c in np.arange(1, 200) / 100:
        assert np.isnan(morans_i(np.full(side * side, round(c, 2)), weights)), c


def test_morans_i_tiny_but_real_variation_is_still_computed():
    # Garde-fou contre une tolerance trop large : 1e-12 de variation relative est
    # tres au-dessus de la resolution flottante (~1e-16).
    values = 1000.0 * (1 + 1e-12 * np.random.default_rng(0).normal(size=100))
    assert np.isfinite(morans_i(values, _rook_weights(10)))


def test_morans_i_rejects_self_weights_and_nonfinite_weights():
    values = np.random.default_rng(2).normal(size=9)
    weights = _rook_weights(3)
    with pytest.raises(ValueError, match="diagonale"):
        morans_i(values, weights + np.eye(9))
    bad = weights.copy()
    bad[0, 1] = np.nan
    with pytest.raises(ValueError, match="finies"):
        morans_i(values, bad)


def _exact_morans_i(values, weights):
    n = len(values)
    mean = Fraction(int(sum(values)), n)
    dev = [Fraction(int(v)) - mean for v in values]
    num = sum(dev[i] * dev[j] for i, j in zip(*np.nonzero(weights)))
    return Fraction(n, int(weights.sum())) * num / sum(d * d for d in dev)


@pytest.mark.parametrize("field_seed", [0, 11, 13])
def test_permutation_test_counts_exact_ties(field_seed):
    # Champ binaire : beaucoup de permutations ont EXACTEMENT le meme I que l'observe mais
    # sortent un cran flottant plus bas -- un `>=` exact les perdait et sous-estimait la
    # p-value (~0.01 ici). Reference : memes permutations, en arithmetique rationnelle.
    weights = _rook_weights(10)
    field = np.random.default_rng(field_seed).integers(0, 2, 100).astype(float)
    observed = _exact_morans_i(field, weights)
    rng = np.random.default_rng(1)
    n_ge = sum(_exact_morans_i(rng.permutation(field), weights) >= observed for _ in range(100))
    expected = float(Fraction(1 + n_ge, 101))
    assert permutation_test(field, weights, n_permutations=100, seed=1)["p_value"] == expected


def test_permutation_test_accepts_a_shared_generator():
    # Un Generator passe tel quel : deux appels successifs tirent des permutations differentes.
    values = np.random.default_rng(0).normal(size=9)
    weights = _rook_weights(3)
    rng = np.random.default_rng(5)
    a = permutation_test(values, weights, n_permutations=30, seed=rng)
    b = permutation_test(values, weights, n_permutations=30, seed=rng)
    assert (a["null_mean"], a["null_std"]) != (b["null_mean"], b["null_std"])


def test_morans_i_instant_constant_field_is_nan_not_zero():
    # Copie de morans_i utilisee par la simulation : un champ constant est INDEFINI
    # (nan), pas "autocorrelation nulle" (0.0).
    assert np.isnan(morans_i_instant(np.full(9, 0.23), _rook_weights(3)))
    assert np.isnan(morans_i_instant(np.full(9, 3.0), _rook_weights(3)))
