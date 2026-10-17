import numpy as np
import pytest

from app.vulnerabilite import multicanal as mc


def _unites_heterogenes(R=0.6, N=37, T=60, graine=0, theta=(0.4, 0.6)):
    """Dynamique linéaire y_{t+1} ~ Poisson(μ_i + R·y_t) avec des flux μ_i très différents d'une unité à l'autre
    (niveaux moyens de 3 à 150), observée par deux canaux amincis indépendants."""
    rng = np.random.default_rng(graine)
    mu = np.geomspace(1.2, 60.0, N)  # niveau moyen μ_i/(1−R) : de 3 à 150
    y = mu / (1 - R)
    O = np.zeros((2, T, N))
    for t in range(T):
        y = rng.poisson(mu + R * y).astype(float)
        for k in range(2):
            O[k, t] = rng.binomial(y.astype(int), theta[k])
    return O


def test_sans_effets_d_unite_la_pente_regroupee_est_biaisee_vers_un():
    pente = np.median([mc.pente_croisee(O[0], O[1]) for O in (_unites_heterogenes(graine=g) for g in range(10))])
    assert pente > 0.85  # persistance des niveaux entre unités, pas dynamique (vrai R = 0,6)


def test_avec_effets_d_unite_on_retrouve_r():
    R_croise = [mc.pente_croisee(O[0], O[1], effets_unite=True) for O in (_unites_heterogenes(graine=g) for g in range(10))]
    assert np.median(R_croise) == pytest.approx(0.6, abs=0.05)
    naif = np.median([mc.pente_naive(O[0], O[0], effets_unite=True) for O in (_unites_heterogenes(graine=g) for g in range(10))])
    assert naif < 0.5  # sous-déclaration : le canal seul divise le R apparent, même en intra-unité


def test_effets_d_unite_et_temporels_combinables():
    O = _unites_heterogenes(graine=3)
    r = mc.pente_croisee(O[0], O[1], effets_temporels=True, effets_unite=True)
    assert r == pytest.approx(0.6, abs=0.1)


def test_effets_d_unite_donnent_la_meme_pente_naive_que_les_moindres_carres_avec_dummies():
    O = _unites_heterogenes(graine=4)[0]
    x, y = O[:-1], O[1:]
    N = O.shape[1]
    A = np.hstack([x.reshape(-1, 1), np.kron(np.ones((x.shape[0], 1)), np.eye(N))])
    beta = np.linalg.lstsq(A, y.reshape(-1), rcond=None)[0][0]
    # y.reshape(-1) parcourt (t, i) ; A aussi : colonne de dummies d'unité pour chaque i
    assert mc.pente_naive(O, O, effets_unite=True) == pytest.approx(beta, rel=1e-9)
