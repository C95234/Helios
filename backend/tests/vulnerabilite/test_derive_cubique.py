import numpy as np
import pytest

from app.vulnerabilite import derive_cubique as dc
from app.vulnerabilite.simulation import barriere_double_puits, simuler_double_puits


def test_barriere_vraie_du_double_puits():
    # h = 0 : puits en ±1, selle en 0, ΔU = 1/4 ⇒ V* = 2·0,25/σ²
    assert barriere_double_puits(0.0, 0.5, -1.0) == pytest.approx(2.0, rel=1e-6)
    assert barriere_double_puits(0.0, 0.5, 1.0) == pytest.approx(2.0, rel=1e-6)
    # une inclinaison favorise un puits : la barrière depuis le puits favorisé augmente, l'autre diminue
    assert barriere_double_puits(0.1, 0.5, 1.0) > 2.0 > barriere_double_puits(0.1, 0.5, -1.0)
    assert np.isnan(barriere_double_puits(0.5, 0.5, 1.0))  # |h| trop grand : un seul puits


def test_simulation_double_puits_forme_et_bascules():
    x, O, h = simuler_double_puits(0.65, 600, np.random.default_rng(0), n_unites=3)
    assert x.shape == (600, 3) and O.shape == (2, 600, 3) and h.shape == (600, 3)
    assert (x > 0.3).any() and (x < -0.3).any()  # les deux états sont visités
    assert np.abs(h).max() <= 0.15 + 1e-12


def test_recuperation_de_la_derive_cubique_sur_un_grand_echantillon():
    """40 séries indépendantes de 400 points, sans forçage (h = 0) : points fixes et barrière retrouvés."""
    x, O, h = simuler_double_puits(0.45, 400, np.random.default_rng(1), n_unites=40, amplitude_h=0.0)
    d = dc.estimer_derive_cubique(O)
    pts = dc.points_fixes_double_puits(d)
    assert pts is not None
    racines_lecture = [r * d.echelle + d.moyenne for r in pts]  # retour aux unités du capteur 0 (gain 1, décalage 0)
    assert racines_lecture == pytest.approx([-1.0, 0.0, 1.0], abs=0.2)
    v_vrai = barriere_double_puits(0.0, 0.45, -1.0)
    assert dc.vstar_double_puits(d, pts[0]) == pytest.approx(v_vrai, rel=0.4)
    assert dc.vstar_double_puits(d, pts[2]) == pytest.approx(v_vrai, rel=0.4)  # puits droit : axe réfléchi, même barrière par symétrie


def test_pas_de_double_puits_renvoie_nan_et_erreurs():
    # une seule bonne position stable : bruit de mesure pur autour d'une constante
    rng = np.random.default_rng(2)
    O = np.stack([rng.normal(0, 1, (200, 3)), rng.normal(0, 1, (200, 3))])
    try:
        d = dc.estimer_derive_cubique(O)
        assert np.isnan(dc.vstar_double_puits(d, 0.0)) or dc.points_fixes_double_puits(d) is not None
    except ValueError:
        pass
    with pytest.raises(ValueError, match="constant"):
        dc.estimer_derive_cubique(np.ones((2, 50, 2)))
    with pytest.raises(ValueError, match="20 observations"):
        dc.estimer_derive_cubique(np.random.default_rng(3).normal(size=(2, 10, 1)))
    assert np.isnan(dc.v_etoile_fenetre(np.ones((2, 50, 1))))
