import numpy as np
import pytest

from app.vulnerabilite import estimation as est
from app.vulnerabilite import modele as m
from app.vulnerabilite import multicanal as mc
from app.vulnerabilite.bruits import BinomialeNegative
from app.vulnerabilite.observation import CanauxAmincis, CapteursAffines
from app.vulnerabilite.simulation import simuler_multicanal

# ---------------------------------------------------------------------------------------------------------
# Copies de référence des simulateurs de la note (scripts t7, t7b, t9), pour vérifier la fidélité du portage
# ---------------------------------------------------------------------------------------------------------


def _ref_t7_sim(eta, rng, R=0.6, mu=1.2, N=100, T=200, th1=0.3, th2=0.4):
    y = np.full(N, 3.0)
    o1p = np.zeros(N)
    O1 = np.zeros((T, N))
    O2 = np.zeros((T, N))
    for t in range(T):
        y = rng.poisson(mu + R * y).astype(float)
        th = np.minimum(0.95, th1 * (1 + eta * o1p))
        o1 = rng.binomial(y.astype(int), th)
        o2 = rng.binomial(y.astype(int), th2)
        o1p = o1
        O1[t], O2[t] = o1, o2
    return O1, O2


def _ref_t7b_sim(c, eta, rng, N=100, T=200, R0=0.6, ml=20.0, th=(0.4, 0.5, 0.6)):
    a, mu, s, mp = m.params_depuis_inflammabilite(R0, c, ml)
    y = np.full(N, ml)
    o1p = np.full(N, th[0] * ml)
    O = np.full((3, T, N), np.nan)
    alive = np.ones(N, bool)
    for t in range(T):
        y = rng.poisson(np.clip(mu + a * y + c * y * y, 0, 1e6)).astype(float)
        t1 = np.minimum(0.95, th[0] * (1 + eta * (o1p / (th[0] * ml) - 1)).clip(0.05))
        o = [rng.binomial(y.astype(int), t1), rng.binomial(y.astype(int), th[1]), rng.binomial(y.astype(int), th[2])]
        o1p = o[0]
        alive &= ~(y >= mp)
        for k in range(3):
            O[k, t, alive] = o[k][alive]
    return O


def _sim_lineaire(eta, graine):
    obs = CanauxAmincis((0.3, 0.4), canal_sous_boucle=0 if eta else None, intensite_boucle=eta, forme_boucle="lineaire")
    _, O = simuler_multicanal(0.6, 1.2, 0.0, 100, 200, np.random.default_rng(graine), obs, y0=3.0)
    return O


def _sim_quadratique(c, eta, graine, N=100, T=200, R0=0.6, ml=20.0, bruit=None, taux=(0.4, 0.5, 0.6)):
    a, mu, _, mp = m.params_depuis_inflammabilite(R0, c, ml)
    obs = CanauxAmincis(taux, canal_sous_boucle=0, intensite_boucle=eta, forme_boucle="centree", niveau_reference=ml)
    return simuler_multicanal(a, mu, c, N, T, np.random.default_rng(graine), obs, bruit=bruit, y0=ml, m_haut=mp)[1]


def test_portage_lineaire_identique_a_t7():
    for eta in (0.0, 0.5):
        O1, O2 = _ref_t7_sim(eta, np.random.default_rng(3))
        O = _sim_lineaire(eta, 3)
        assert np.array_equal(O[0], O1) and np.array_equal(O[1], O2)


def test_portage_quadratique_identique_a_t7b():
    ref = _ref_t7b_sim(0.006, 1.0, np.random.default_rng(4))
    mine = _sim_quadratique(0.006, 1.0, 4)
    assert np.array_equal(ref, mine, equal_nan=True)


# ---------------------------------------------------------------------------------------------------------
# Cas linéaire : sous-déclaration, boucle de surveillance, estimateur croisé (propositions 6 et 7)
# ---------------------------------------------------------------------------------------------------------


def _medianes_lineaires(eta, reps=20):
    res = {"naif1": [], "naif2": [], "croise_2_depuis_1": [], "croise_1_depuis_2": []}
    for i in range(reps):
        O = _sim_lineaire(eta, i)
        res["naif1"].append(mc.pente_naive(O[0], O[0]))
        res["naif2"].append(mc.pente_naive(O[1], O[1]))
        res["croise_2_depuis_1"].append(mc.pente_croisee(O[1], O[0]))
        res["croise_1_depuis_2"].append(mc.pente_croisee(O[0], O[1]))
    return {k: float(np.median(v)) for k, v in res.items()}


def test_la_sous_declaration_seule_divise_le_r_apparent():
    r = _medianes_lineaires(0.0)
    assert r["naif1"] == pytest.approx(0.24, abs=0.04) and r["naif2"] == pytest.approx(0.31, abs=0.04)
    assert r["croise_2_depuis_1"] == pytest.approx(0.60, abs=0.03) and r["croise_1_depuis_2"] == pytest.approx(0.60, abs=0.03)


def test_boucle_de_surveillance_gonfle_le_naif_et_le_croise_retrouve_r():
    r = _medianes_lineaires(0.5)
    assert r["naif1"] == pytest.approx(0.71, abs=0.05)  # fausse contagion de type PredPol
    assert r["naif2"] == pytest.approx(0.31, abs=0.04)
    assert r["croise_2_depuis_1"] == pytest.approx(0.60, abs=0.03)  # sortie indépendante, instrument surveillé
    assert r["croise_1_depuis_2"] > 0.75  # sortie surveillée : gonflé


def test_diagnostic_d_asymetrie_designe_le_canal_sous_boucle():
    sans = mc.diagnostic_asymetrie(*(lambda O: (O[1], O[0]))(_sim_lineaire(0.0, 11)))
    assert sans.canal_suspect is None and abs(sans.ecart) < 0.05
    O = _sim_lineaire(0.5, 11)  # canal 0 sous boucle
    avec = mc.diagnostic_asymetrie(O[1], O[0])  # l = canal indépendant, k = canal surveillé
    assert avec.canal_suspect == 1 and avec.ecart > 0.1  # « k » est le canal sous boucle
    inverse = mc.diagnostic_asymetrie(O[0], O[1])
    assert inverse.canal_suspect == 0 and inverse.ecart < -0.1


def test_taux_de_detection_identifie_sans_le_connaitre():
    O = _sim_quadratique(0.012, 0.0, 5)
    assert mc.taux_detection(O[1], O[2]) == pytest.approx(0.5, abs=0.03)
    assert mc.taux_detection(O[2], O[1]) == pytest.approx(0.6, abs=0.03)
    assert mc.taux_detection(O[0], O[2]) == pytest.approx(0.4, abs=0.03)


def test_derive_instrumentee_donnees_insuffisantes_ou_colineaires():
    vide = np.full((5, 4), np.nan)
    with pytest.raises(ValueError, match="Moins de 3"):
        mc.derive_instrumentee(vide, vide)
    constant = np.full((10, 6), 3.0)
    with pytest.raises(ValueError, match="colinéaires"):
        mc.derive_instrumentee(constant, constant)


def test_validations_des_modeles_d_observation():
    with pytest.raises(ValueError, match="taux"):
        CanauxAmincis((0.0, 0.5))
    with pytest.raises(ValueError, match="forme_boucle"):
        CanauxAmincis((0.5,), forme_boucle="autre")
    with pytest.raises(ValueError, match="gain"):
        CapteursAffines((0.0, 1.0), (0.0, 0.0))
    capteurs = CapteursAffines((2.0, 0.5), (1.0, -3.0), bruit_mesure=0.0)
    o = capteurs.observer(np.array([1.0, 2.0]), np.random.default_rng(0))
    assert np.allclose(o[0], [3.0, 5.0]) and np.allclose(o[1], [-2.5, -2.0])


# ---------------------------------------------------------------------------------------------------------
# Cas quadratique : Φ en unités vraies à partir de 3 canaux (proposition 8) — tableau du cahier §3.3
# ---------------------------------------------------------------------------------------------------------


@pytest.mark.slow
def test_multicanal_trois_canaux_boucle_sur_le_canal_1():
    """Cahier : 3 canaux, boucle sur le canal 1 : Φ̂ ≈ 11,5 pour Φ = 12,2 (± 20 %).
    Graines et configurations de `t7b` (40 répétitions, R = 0,6, m₋ = 20, taux 0,4 / 0,5 / 0,6)."""
    c = 0.006
    phi_vrai = m.phi_poisson(0.6, c, 20.0)
    assert phi_vrai == pytest.approx(12.17, abs=0.01)
    res = {"naif": [], "deux_calibre_canal1": [], "trois_instr1": [], "trois_instr3": []}
    for i in range(40):
        O = _sim_quadratique(c, 1.0, i)
        res["naif"].append(min(est.ajuster(O[1]).phi, 99))
        res["deux_calibre_canal1"].append(min(mc.estimer_multicanal(O, 1, 0, 0).phi, 99))
        res["trois_instr1"].append(min(mc.estimer_multicanal(O, 1, 0, 2).phi, 99))
        res["trois_instr3"].append(min(mc.estimer_multicanal(O, 1, 2, 2).phi, 99))
    med = {k: float(np.median(v)) for k, v in res.items()}
    assert med["trois_instr3"] == pytest.approx(11.5, rel=0.20)  # robuste même avec boucle
    assert med["naif"] > 2.5 * phi_vrai  # un seul canal : la société paraît ~3 fois plus sûre
    assert med["deux_calibre_canal1"] < 0.5 * phi_vrai  # calibrage par le canal surveillé : fausse alerte
    assert med["trois_instr1"] == pytest.approx(10.5, rel=0.25)


@pytest.mark.slow
@pytest.mark.parametrize("dispersion, attendu, tol", [(1.0, 1.00, 0.10), (2.0, 2.00, 0.10), (4.0, 3.78, 0.40)])
def test_dispersion_par_canaux_croises(dispersion, attendu, tol):
    """Cahier : φ = 1 / 2 → φ̂ = 1,00 / 2,00 (± 0,1). Pour φ = 4, la note rapporte 3,6–3,8 (biais connu).
    Graines et configuration de `t9` (R = 0,6, m₋ = 20, c = 0,008, 100 × 200, taux 0,5 / 0,6, 30 répétitions)."""
    c = 0.008
    bruit = None if dispersion == 1.0 else BinomialeNegative(dispersion)
    valeurs = []
    for i in range(30):
        a, mu, _, mp = m.params_depuis_inflammabilite(0.6, c, 20.0)
        obs = CanauxAmincis((0.5, 0.6))
        _, O = simuler_multicanal(a, mu, c, 100, 200, np.random.default_rng(100 * i + int(c * 1000) + int(dispersion)),
                                  obs, bruit=bruit, y0=20.0, m_haut=mp)
        valeurs.append(mc.estimer_deux_canaux_avec_dispersion(O, sortie=1, autre=0).dispersion)
    assert np.median(valeurs) == pytest.approx(attendu, abs=tol)
