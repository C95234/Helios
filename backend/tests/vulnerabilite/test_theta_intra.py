import numpy as np
import pytest

from app.vulnerabilite import multicanal as mc

T, N = 105, 37


def _vrai(rng, R=0.8, amplitude=4.0):
    t = np.arange(T)
    vague = sum(np.exp(-0.5 * ((t - c) / 5.0) ** 2) for c in (14, 45, 80))
    taille = np.exp(rng.uniform(np.log(40), np.log(300), N))
    y = taille.copy()
    v = np.zeros((T, N))
    for i in range(T):
        y = rng.poisson(taille * (1 + amplitude * vague[i]) * (1 - R) + R * y).astype(float)
        v[i] = y
    return v.astype(int)


def _mediane(scenario, reps=25):
    rng = np.random.default_rng(5)
    regroupe, intra = [], []
    for _ in range(reps):
        v = _vrai(rng)
        ou, os_ = scenario(rng, v)
        regroupe.append(mc.taux_detection(ou.astype(float), os_.astype(float)))
        intra.append(mc.taux_detection_intra_unite(ou.astype(float), os_.astype(float)))
    return float(np.median(regroupe)), float(np.median(intra))


def test_theta_commun_les_deux_estimateurs_sont_sans_biais():
    r, i = _mediane(lambda rng, v: (rng.binomial(v, 0.4), rng.binomial(v, 0.6)))
    assert r == pytest.approx(0.4, abs=0.06) and i == pytest.approx(0.4, abs=0.08)


def test_theta_propre_a_chaque_unite_l_estimateur_regroupe_s_effondre_pas_l_intra_unite():
    """Signature observée sur données réelles (θ̂ regroupé très négatif) : taux de détection différents d'un département à l'autre."""
    r, i = _mediane(lambda rng, v: (rng.binomial(v, rng.uniform(0.2, 0.8, N)), rng.binomial(v, rng.uniform(0.2, 0.8, N))))
    assert r < -5.0
    assert 0.0 < i < 1.0


def test_derive_du_taux_dans_le_temps_sort_des_bornes_pour_les_deux():
    derive = np.linspace(1.0, 0.5, T)[:, None]
    r, i = _mediane(lambda rng, v: (rng.binomial(v, 0.4), rng.binomial(v, 0.6 * derive)))
    assert r > 1.0 and i > 1.0


def test_validation_et_unites_ecartees():
    X = np.full((20, 3), np.nan)
    with pytest.raises(ValueError, match="Aucune unité"):
        mc.taux_detection_intra_unite(X, X)
    rng = np.random.default_rng(0)
    v = _vrai(rng)[:, :5]
    a, b = rng.binomial(v, 0.5).astype(float), rng.binomial(v, 0.5).astype(float)
    a[:, 0] = np.nan  # une unité sans donnée est écartée
    assert np.isfinite(mc.taux_detection_intra_unite(a, b))
