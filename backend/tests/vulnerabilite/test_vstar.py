import numpy as np
import pytest
from scipy.integrate import quad

from app.vulnerabilite import modele as m
from app.vulnerabilite import multicanal as mc
from app.vulnerabilite.bruits import BinomialeNegative, Gaussien, Poisson
from app.vulnerabilite.observation import CapteursAffines
from app.vulnerabilite.simulation import (
    simuler_gaussien_capteurs,
    temps_avant_embrasement,
    temps_avant_embrasement_gaussien,
)
from app.vulnerabilite.vstar import temps_moyen_exact_poisson, vstar_1d, vstar_gaussien, vstar_poisson

R0, ML = 0.6, 3.0


def _quadratique(mu, a=0.4, c=1.0):
    return (lambda x: mu + a * x + c * x * x), m.zeros_de_derive(lambda x: mu + a * x + c * x * x, -3, 3)


# ---- V* Poisson ------------------------------------------------------------------------------------------
def test_vstar_poisson_converge_avec_la_grille():
    a, mu, _, _ = m.params_depuis_inflammabilite(R0, 0.02, ML)
    v = {g: vstar_poisson(a, mu, 0.02, g) for g in (300, 600, 1500)}
    assert v[1500] == pytest.approx(5.2126, abs=2e-3)  # valeur calculée avec le code de la note
    assert abs(v[300] - v[1500]) < 0.01 and abs(v[600] - v[1500]) < 0.003


def test_vstar_poisson_decroit_quand_la_courbure_augmente():
    valeurs = []
    for c in (0.01, 0.02, 0.03):
        a, mu, _, _ = m.params_depuis_inflammabilite(R0, c, ML)
        valeurs.append(vstar_poisson(a, mu, c, 400))
    assert valeurs[0] > valeurs[1] > valeurs[2] > 0


def test_vstar_poisson_proche_de_phi_et_du_temps_exact():
    # note : V* est plus proche de ln E[T] que Φ (pente 1,03 contre 1,17)
    for c, phi in ((0.02, 4.778), (0.03, 2.751)):
        a, mu, _, mp = m.params_depuis_inflammabilite(R0, c, ML)
        v = vstar_poisson(a, mu, c, 600)
        assert 0.8 * phi < v < 1.25 * phi
        lnT = np.log(temps_moyen_exact_poisson(a, mu, c, ML, mp))
        assert abs((lnT - np.log(2 * np.pi / (1 - R0))) - v) < 1.2  # ln E[T] = V* + ln(2π/(1−R)) + O(1)


def test_temps_exact_coincide_avec_la_simulation():
    # note, tableau de la cécité : E[T] mesuré 643 (c = 0,03), 300 trajectoires
    a, mu, _, mp = m.params_depuis_inflammabilite(R0, 0.03, ML)
    exact = temps_moyen_exact_poisson(a, mu, 0.03, ML, mp)
    mesure = np.nanmean(temps_avant_embrasement(R0, 0.03, ML, n=800, t_max=60_000, seed=2))
    assert mesure == pytest.approx(exact, rel=0.15)


def test_vstar_bruit_binomiale_negative_tend_vers_poisson():
    a, mu, _, _ = m.params_depuis_inflammabilite(R0, 0.03, ML)
    m_bas, m_haut = m.points_fixes(a, mu, 0.03)
    F = lambda x: mu + a * x + 0.03 * x * x  # noqa: E731
    v_p = vstar_1d(F, Poisson(), m_bas, m_haut, 1e-3, 1.6 * m_haut + 5, 300)
    v_nb1 = vstar_1d(F, BinomialeNegative(1.0 + 1e-7), m_bas, m_haut, 1e-3, 1.6 * m_haut + 5, 300)
    v_nb2 = vstar_1d(F, BinomialeNegative(2.0), m_bas, m_haut, 1e-3, 1.6 * m_haut + 5, 300)
    assert v_nb1 == pytest.approx(v_p, rel=1e-3)
    assert v_nb2 < v_p  # plus de bruit, embrasement moins coûteux


def test_vstar_validations():
    with pytest.raises(ValueError, match="bas < m_bas"):
        vstar_1d(lambda x: x, Poisson(), 5.0, 3.0, 0.0, 10.0)
    with pytest.raises(ValueError, match="Pas d'état calme"):
        vstar_poisson(0.5, 5.0, 0.1)


# ---- V* gaussien -----------------------------------------------------------------------------------------
def test_vstar_gaussien_quadratique_egal_a_l_indice_de_diffusion():
    F, (mb, mh, *_) = _quadratique(0.05)
    sigma = 0.112
    phi_g = 2 * quad(lambda x: -(F(x) - x), mb, mh)[0] / sigma**2
    assert phi_g == pytest.approx(m.phi_gaussien(1.0, mh - mb, sigma**2), rel=1e-8)
    v = vstar_gaussien(F, sigma, mb, mh, bas=mb - 1.5, haut=mh + 2 * (mh - mb) + 0.5, n_noeuds=1000)
    assert v == pytest.approx(phi_g, rel=0.03)  # note : 1,71 contre 1,70


def test_vstar_gaussien_invariant_par_changement_affine_d_unites():
    F, (mb, mh, *_) = _quadratique(0.05)
    sigma, g, b = 0.08, 2.5, -1.7
    Fu = lambda u: g * F((u - b) / g) + b  # noqa: E731
    v1 = vstar_gaussien(F, sigma, mb, mh, n_noeuds=500)
    v2 = vstar_gaussien(Fu, g * sigma, g * mb + b, g * mh + b, n_noeuds=500)
    assert v2 == pytest.approx(v1, abs=1e-8)
    # de même pour un signal de gain négatif (capteur inversé) : V* est une propriété de la dynamique


def test_cout_gaussien_variance_dependante_du_niveau_dans_vstar():
    F, (mb, mh, *_) = _quadratique(0.05)
    v_const = vstar_1d(F, Gaussien(0.01), mb, mh, mb - 0.5, mh + 0.5, 300)
    v_var = vstar_1d(F, Gaussien(lambda x: 0.01 * (1 + 0 * x)), mb, mh, mb - 0.5, mh + 0.5, 300)
    assert v_var == pytest.approx(v_const)


# ---- tests longs du cahier (§3.3) -----------------------------------------------------------------------
@pytest.mark.slow
def test_loi_unifiee_vstar_contre_temps_exacts_147_jeux():
    """Cahier : V* Poisson 1D contre temps exacts → pente ≈ 1,03 (0,9–1,15). Les 147 jeux de la note
    (R de 0,3 à 0,8, m₋ de 2 à 15, Φ de 0,5 à 24 ; note : pente 1,03, écart-type 0,28, corrélation 0,9993)."""
    lignes = []
    for R in (0.3, 0.5, 0.6, 0.7, 0.8):
        for ml in (2.0, 4.0, 8.0, 15.0):
            for c in np.geomspace(0.003, 0.3, 18):
                try:
                    a, mu, _, mp = m.params_depuis_inflammabilite(R, c, ml)
                except ValueError:
                    continue
                if mu <= 0 or mp > 400 or not 0.5 < m.phi_poisson(R, c, ml) < 25:
                    continue
                lignes.append((R, vstar_poisson(a, mu, c), np.log(temps_moyen_exact_poisson(a, mu, c, ml, mp)), m.phi_poisson(R, c, ml)))
    assert len(lignes) == 147
    R, V, lnT, P = np.array(lignes).T
    y = lnT - np.log(2 * np.pi / (1 - R))
    pente_v, ic = np.polyfit(V, y, 1)
    assert 0.9 <= pente_v <= 1.15 and pente_v == pytest.approx(1.03, abs=0.01)
    assert np.std(y - (pente_v * V + ic)) == pytest.approx(0.275, abs=0.01)
    assert np.corrcoef(V, y)[0, 1] > 0.999
    pente_p = np.polyfit(P, y, 1)[0]
    assert pente_p == pytest.approx(1.17, abs=0.02)  # Φ de diffusion : plus loin de 1 que V*


@pytest.mark.slow
def test_vstar_gaussien_contre_temps_simules_application_quadratique():
    """Cahier : pente ≈ 0,98 (0,85–1,1). Famille quadratique x ↦ μ + 0,4·x + x², 1 500 trajectoires par cas.

    Remarque (voir reproduction.md) : le script `g2` de la note applique par mégarde à cette famille la courbure
    `c` laissée par la boucle précédente (fermeture tardive), pas c = 1 ; la pente obtenue ici avec les paramètres
    annoncés est la même (0,98) à 0,01 près."""
    lignes = []
    for mu in (0.02, 0.05, 0.08):
        F, (mb, mh, *_) = _quadratique(mu)
        lam = 0.4 + 2 * mb
        seuil = mh + 2 * (mh - mb)
        for sigma in np.geomspace(0.03, 0.3, 8):
            phi_g = 2 * quad(lambda x: -(F(x) - x), mb, mh)[0] / sigma**2
            if not 1.0 < phi_g < 14:
                continue
            T = temps_avant_embrasement_gaussien(F, sigma, mb, seuil, seed=int(sigma * 1000))
            if np.isnan(T).mean() > 0.05:
                continue
            V = vstar_gaussien(F, sigma, mb, mh, bas=mb - 1.5, haut=seuil + 0.5, n_noeuds=1500)
            lignes.append((lam, V, np.log(np.nanmean(T))))
    assert len(lignes) >= 8
    lam, V, lnT = np.array(lignes).T
    pente = np.polyfit(V, lnT - np.log(2 * np.pi / (1 - lam)), 1)[0]
    assert 0.85 <= pente <= 1.1 and pente == pytest.approx(0.98, abs=0.03)


def _g3(sigma, eta_relatif, reps=30):
    mu, a, c = 0.05, 0.4, 1.0
    F = lambda x: mu + a * x + c * x * x  # noqa: E731
    m0, mp0 = m.zeros_de_derive(F, -2, 2)[:2]
    v_vrai = vstar_gaussien(F, sigma, m0, mp0)
    un, deux = [], []
    capteurs = CapteursAffines((2.0, 0.5), (1.0, -3.0), bruit_mesure=eta_relatif * sigma)
    for i in range(reps):
        O = simuler_gaussien_capteurs(F, sigma, m0, mp0, 50, 300, np.random.default_rng(i), capteurs)
        un.append(min(mc.estimer_vstar_un_capteur(O[0]), 99))
        deux.append(min(mc.estimer_vstar_deux_capteurs(O), 99))
    return v_vrai, float(np.median(un)), float(np.nanmedian(deux))


@pytest.mark.slow
def test_capteurs_affines_deux_capteurs_corrigent_le_bruit_de_mesure():
    """Cahier : V* à deux capteurs, bruit de mesure égal au bruit dynamique ≈ 3,9 (un capteur ≈ 17,7), ± 20 %.
    Gains (2 ; 0,5), décalages (1 ; −3), σ = 0,08, 50 séries × 300 pas, 30 répétitions (script `g3`)."""
    v_vrai, un, deux = _g3(0.08, 1.0)
    assert v_vrai == pytest.approx(3.32, abs=0.02)
    assert deux == pytest.approx(3.9, rel=0.20)
    assert un == pytest.approx(17.7, rel=0.20)
    assert un > 4 * v_vrai  # un capteur bruité : la population paraît 5 fois plus loin du seuil

    _, un0, deux0 = _g3(0.08, 0.0)
    assert un0 == pytest.approx(deux0, rel=0.10)  # sans bruit de mesure, un capteur suffit
    assert deux0 == pytest.approx(4.04, rel=0.15)  # biais résiduel = coupure et plancher, pas la mesure
