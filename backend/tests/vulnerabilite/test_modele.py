import numpy as np
import pytest

from app.vulnerabilite import modele as m

R0, C0, M0 = 0.6, 0.02, 3.0  # société de référence de la note (Φ = 4,78)


def test_points_fixes_et_identite_symboliques():
    sp = pytest.importorskip("sympy")
    a, c, mu, x = sp.symbols("a c mu x", positive=True)
    F = mu + a * x + c * x**2
    racine = sp.sqrt((1 - a) ** 2 - 4 * c * mu)
    m_bas, m_haut = ((1 - a) - racine) / (2 * c), ((1 - a) + racine) / (2 * c)
    s = m_haut - m_bas
    assert sp.simplify(F.subs(x, m_bas) - m_bas) == 0
    assert sp.simplify(F.subs(x, m_haut) - m_haut) == 0
    assert sp.simplify(sp.diff(F, x).subs(x, m_bas) - (1 - c * s)) == 0  # R = 1 − c s*
    f = F - x
    assert sp.simplify(sp.integrate(-f, (x, m_bas, m_haut)) - c * s**3 / 6) == 0  # barrière additive
    phi_integrale = sp.integrate(2 * (-f) / x, (x, m_bas, m_haut))
    phi_close = (1 - a) * s - 2 * mu * sp.log(m_haut / m_bas)
    valeurs = {a: 0.48, c: 0.02, mu: 1.38}
    assert float(phi_integrale.subs(valeurs)) == pytest.approx(float(phi_close.subs(valeurs)), abs=1e-10)


def test_phi_forme_close_contre_integrale_numerique():
    a, mu, s, m_haut = m.params_depuis_inflammabilite(R0, C0, M0)
    close = m.phi_poisson(R0, C0, M0)
    assert close == pytest.approx(4.778, abs=1e-3)
    assert close == pytest.approx(4.77820588, abs=1e-6)
    assert m.phi_numerique(a, mu, C0) == pytest.approx(close, abs=1e-6)


def test_parametres_de_la_societe_de_reference():
    a, mu, s, m_haut = m.params_depuis_inflammabilite(R0, C0, M0)
    assert (a, s, m_haut) == pytest.approx((0.48, 20.0, 23.0))
    assert mu == pytest.approx(1.38)
    m_bas, m_haut_pf = m.points_fixes(a, mu, C0)
    assert (m_bas, m_haut_pf) == pytest.approx((M0, 23.0))
    assert m.inflammabilite(a, C0, M0) == pytest.approx(R0)
    assert m.identite_inflammabilite(C0, s) == pytest.approx(R0)  # R = 1 − c s*


def test_phi_pour_le_balayage_de_c_de_la_note():
    # note, preuve de la prop. 5 : R = 0,6, m₋ = 3
    attendu = {0.001: 150.6, 0.01: 11.5, 0.02: 4.8, 0.03: 2.8, 0.067: 0.85, 0.1: 0.44}
    for c, phi in attendu.items():
        assert m.phi_poisson(R0, c, M0) == pytest.approx(phi, abs=0.06, rel=0.005), c


def test_phi_surdispersion_divise_par_phi():
    base = m.phi_poisson(R0, 0.01, M0)
    assert m.phi_surdispersion(R0, 0.01, M0, 4.0) == pytest.approx(base / 4.0)
    assert m.phi_surdispersion(R0, 0.01, M0, 1.0) == pytest.approx(base)


def test_phi_petit_c_premier_terme():
    c = 1e-4
    rapport = m.phi_poisson(R0, c, M0) / m.phi_petit_c(R0, c)
    assert rapport == pytest.approx(1.0, abs=0.01)  # O(ln(1/c)) devant (1−R)²/c


def test_phi_gaussien_et_loi_pres_du_pli_coincident_pour_le_quadratique():
    # exacte pour l'application quadratique (corollaire CG) : (1−λ)³/(3c²σ²) = c s*³/(3σ²)
    c, s, sigma2 = 0.8, 0.5, 0.01
    lam = 1.0 - c * s
    assert m.loi_pres_du_pli(lam, c, sigma2) == pytest.approx(m.phi_gaussien(c, s, sigma2))
    a, mu, mm = 0.4, 0.05, None
    m_bas, m_haut = m.points_fixes(a, mu, 1.0)
    phi_num = m.phi_numerique(a, mu, 1.0, variance=lambda x: 0.01)
    assert phi_num == pytest.approx(m.phi_gaussien(1.0, m_haut - m_bas, 0.01), rel=1e-8)


def test_barriere_additive():
    a, mu, s, _ = m.params_depuis_inflammabilite(R0, C0, M0)
    m_bas, m_haut = m.points_fixes(a, mu, C0)
    from scipy.integrate import quad

    integrale, _ = quad(lambda x: -(m.reponse_moyenne(x, a, mu, C0) - x), m_bas, m_haut)
    assert integrale == pytest.approx(m.barriere_additive(C0, s), rel=1e-9)


def test_pas_d_etat_calme_quand_delta_negatif():
    assert m.points_fixes(0.5, 5.0, 0.1) is None  # Δ = 0,25 − 2 < 0
    with pytest.raises(ValueError, match="Pas d'état calme"):
        m.phi_numerique(0.5, 5.0, 0.1)


@pytest.mark.parametrize(
    "args, motif",
    [((0.6, 0.0, 3.0), "courbure"), ((1.0, 0.02, 3.0), "inférieure à 1"), ((0.6, 0.02, 0.0), "niveau calme"),
     ((0.6, 0.2, 3.0), "inadmissibles")],
)
def test_parametres_hors_domaine_leve_une_erreur(args, motif):
    with pytest.raises(ValueError, match=motif):
        m.params_depuis_inflammabilite(*args)


def test_borne_a_zero_atteinte_a_l_arrondi_pres():
    # R = 0,6, c = 0,1, m₋ = 3 : a = 0 au bit près ; ne doit pas être refusé
    a, _, _, _ = m.params_depuis_inflammabilite(0.6, 0.1, 3.0)
    assert a == 0.0


def test_loi_des_temps_prediction_de_la_note():
    # tableau de la cécité : E[T] prédit 6 300 (Φ = 4,78) et 820 (Φ = 2,75)
    assert m.temps_moyen_predit(R0, 4.78) == pytest.approx(6300, rel=0.03)
    assert m.temps_moyen_predit(R0, 2.75) == pytest.approx(820, rel=0.03)


# ---- identité générale près d'un pli (note, prop. PG1 ; script g1) --------------------------------------
_K = 0.3


def _cubique(h):
    return (
        lambda x: x + _K * (h - (x**3 - x)),
        lambda x: 1 - _K * (3 * x * x - 1),
        lambda x: -6 * _K * x,
    )


def test_identite_generale_double_puits_cubique():
    ecarts = {}
    for h in (0.2, 0.3, 0.36, 0.38):
        F, dF, d2F = _cubique(h)
        r = m.ecart_identite_generale(F, dF, d2F)
        ecarts[round(r["s_etoile"], 3)] = r["ecart"]
    # note : écart 0,135 ; 0,060 ; 0,017 ; 0,003 pour s* = 0,67 ; 0,45 ; 0,24 ; 0,11
    s_valeurs = sorted(ecarts)
    assert ecarts[s_valeurs[0]] < 0.005  # s* ≈ 0,11
    assert ecarts[s_valeurs[-1]] == pytest.approx(0.135, abs=0.005)
    # l'écart croît comme s*² : le rapport écart/s*² est à peu près constant
    rapports = [ecarts[s] / s**2 for s in s_valeurs]
    assert max(rapports) / min(rapports) < 1.2


def test_identite_generale_exacte_pour_le_quadratique():
    a, mu, c = 0.4, 0.05, 1.0
    r = m.ecart_identite_generale(lambda x: mu + a * x + c * x**2, lambda x: a + 2 * c * x, lambda x: 2 * c + 0 * x, -2, 2)
    assert r["ecart"] < 1e-9


def test_identite_generale_sans_bistabilite_leve_une_erreur():
    with pytest.raises(ValueError, match="bistabilité"):
        m.ecart_identite_generale(lambda x: 0.5 * x + 1.0, lambda x: 0.5 + 0 * x, lambda x: 0 * x)  # un seul point fixe
