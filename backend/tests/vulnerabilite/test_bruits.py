import numpy as np
import pytest

from app.vulnerabilite.bruits import BinomialeNegative, Gaussien, Poisson, modele_bruit


def test_cout_poisson_nul_au_pas_le_plus_probable_et_positif_ailleurs():
    f = np.array([0.5, 3.0, 20.0, 150.0])
    assert np.allclose(Poisson().cout_pas(f, f), 0.0, atol=1e-12)
    for decalage in (-0.5, 0.5, 2.0, 10.0):
        x = np.maximum(f + decalage, 0.0)
        assert np.all(Poisson().cout_pas(x, f) >= -1e-12)


def test_cout_poisson_en_zero_vaut_la_moyenne():
    # -ln P(0) = F pour une loi de Poisson ; convention 0·ln 0 = 0
    assert Poisson().cout_pas(0.0, 4.0) == pytest.approx(4.0)


def test_cout_poisson_est_moins_log_vraisemblance_relative():
    from scipy.stats import poisson

    f, x = 400, 430
    # −ln P(x) + ln P(f) = x ln(x/f) − x + f + ½ ln(x/f) + O(1/x) : le coût de la note est ce que
    # donne la formule de Stirling sans le terme ½ ln(x/f) (« à la correction de Stirling près »).
    exact = -poisson.logpmf(x, f) + poisson.logpmf(f, f)
    assert Poisson().cout_pas(x, f) + 0.5 * np.log(x / f) == pytest.approx(exact, abs=1e-3)


def test_binomiale_negative_redonne_poisson_quand_phi_vaut_un():
    f = np.array([2.0, 9.0, 40.0])
    x = np.array([1.0, 14.0, 33.0])
    assert np.allclose(BinomialeNegative(1.0).cout_pas(x, f), Poisson().cout_pas(x, f))
    # et par continuité quand φ → 1
    assert np.allclose(BinomialeNegative(1.0 + 1e-7).cout_pas(x, f), Poisson().cout_pas(x, f), rtol=1e-4)


def test_cout_binomiale_negative_nul_au_pas_le_plus_probable_et_positif():
    f = np.array([2.0, 9.0, 40.0])
    bn = BinomialeNegative(3.0)
    assert np.allclose(bn.cout_pas(f, f), 0.0, atol=1e-12)
    assert np.all(bn.cout_pas(f + 5.0, f) > 0) and np.all(bn.cout_pas(np.maximum(f - 1.0, 0.0), f) > 0)


def test_surdispersion_diminue_le_cout_d_un_meme_ecart():
    f, x = 10.0, 25.0
    couts = [BinomialeNegative(phi).cout_pas(x, f) for phi in (1.0, 2.0, 4.0)]
    assert couts[0] > couts[1] > couts[2]


def test_cout_gaussien_variance_constante_et_variable():
    g = Gaussien(sigma2=0.25)
    assert g.cout_pas(1.5, 1.0) == pytest.approx(0.25 / (2 * 0.25))
    gv = Gaussien(sigma2=lambda x: 0.1 * np.asarray(x) ** 2)
    assert gv.cout_pas(3.0, 2.0, niveau=2.0) == pytest.approx(1.0 / (2 * 0.4))


@pytest.mark.parametrize("phi", [1.0, 2.0, 4.0])
def test_simulation_comptages_moyenne_et_dispersion(phi):
    rng = np.random.default_rng(12345)
    bruit = Poisson() if phi == 1.0 else BinomialeNegative(phi)
    tirages = bruit.simuler(np.full(400_000, 20.0), rng)
    assert tirages.mean() == pytest.approx(20.0, rel=0.01)
    assert tirages.var() / tirages.mean() == pytest.approx(phi, rel=0.03)
    assert np.all(tirages >= 0) and np.all(tirages == np.floor(tirages))


def test_simulation_gaussienne_moyenne_et_variance():
    rng = np.random.default_rng(7)
    tirages = Gaussien(sigma2=0.04).simuler(np.full(200_000, 1.5), rng)
    assert tirages.mean() == pytest.approx(1.5, abs=0.005)
    assert tirages.var() == pytest.approx(0.04, rel=0.03)


def test_variance_et_dispersion_declarees():
    assert Poisson().dispersion == 1.0 and BinomialeNegative(2.5).dispersion == 2.5 and Gaussien().dispersion is None
    assert Poisson().variance(6.0) == pytest.approx(6.0)
    assert BinomialeNegative(2.5).variance(6.0) == pytest.approx(15.0)


def test_fabrique_et_validations():
    assert isinstance(modele_bruit("poisson"), Poisson)
    assert modele_bruit("binomiale_negative", phi=3.0).dispersion == 3.0
    assert isinstance(modele_bruit("gaussien", sigma2=2.0), Gaussien)
    with pytest.raises(ValueError, match="inconnu"):
        modele_bruit("laplace")
    with pytest.raises(ValueError, match="φ"):
        BinomialeNegative(0.5)
