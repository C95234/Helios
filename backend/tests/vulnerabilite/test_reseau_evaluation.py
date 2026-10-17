import numpy as np
import pytest

from app.vulnerabilite import modele as m
from app.vulnerabilite.evaluation import auc, tendance_kendall
from app.vulnerabilite.reseau import (
    AjustementReseau,
    ajuster_reseau,
    etalonner_temps,
    matrice_grille,
    normaliser_par_ligne,
    simuler_reseau,
)

R0, ML = 0.6, 3.0


def test_matrice_grille_torique():
    W = matrice_grille(5)
    assert W.shape == (25, 25) and np.allclose(W.sum(axis=1), 1.0) and np.allclose(W, W.T)
    assert np.all((W > 0).sum(axis=1) == 4) and np.all(np.diag(W) == 0)


def test_normalisation_par_ligne_et_unite_isolee():
    A = np.array([[0, 1, 1], [1, 0, 0], [1, 0, 0]], float)
    assert np.allclose(normaliser_par_ligne(A).sum(axis=1), 1.0)
    with pytest.raises(ValueError, match="aucun voisin"):
        normaliser_par_ligne(np.zeros((2, 2)))


def test_sans_couplage_le_reseau_est_un_ensemble_d_unites_independantes():
    """w = 0 : chaque unité suit sa propre dynamique ; le premier embrasement de N unités arrive de l'ordre de N fois
    plus vite (note : 94 mesuré pour 63 prédit à Φ = 4,78 ; 15 mesuré à Φ = 2,75 : la prédiction « unités indépendantes »
    sous-estime d'un facteur ~1,5 à 2)."""
    a, mu, _, mp = m.params_depuis_inflammabilite(R0, 0.03, ML)
    W = matrice_grille(10)
    T, taille, _ = simuler_reseau(R0, 0.03, ML, 0.0, W, 20_000, np.random.default_rng(3), n_repetitions=60)
    t_unite = m.temps_moyen_predit(R0, m.phi_poisson(R0, 0.03, ML)) / 100  # prédiction « unités indépendantes »
    assert np.isnan(T).mean() == 0 and t_unite < np.nanmean(T) < 3 * t_unite
    assert np.nanmedian(taille) >= 1


def test_le_couplage_retarde_l_embrasement():
    W = matrice_grille(10)
    T0 = simuler_reseau(R0, 0.03, ML, 0.0, W, 10_000, np.random.default_rng(1), 40)[0]
    T3 = simuler_reseau(R0, 0.03, ML, 0.3, W, 10_000, np.random.default_rng(1), 40)[0]
    # note : à Φ = 2,75, E[T] passe de 15 pas (w = 0) à plus de 10⁴ pas (w = 0,3 ; 97 % de séries censurées)
    assert np.isnan(T0).mean() == 0 and np.nanmean(T0) < 100
    assert np.isnan(T3).mean() > 0.9


def test_etalonnage_renvoie_temps_censure_et_foyer():
    W = matrice_grille(10)
    r = etalonner_temps(R0, 0.05, ML, 0.0, W, n_repetitions=30, n_pas_max=5000, seed=1)
    assert set(r) == {"T_moyen", "part_censuree", "taille_foyer_mediane"} and r["T_moyen"] > 0


def test_ajustement_reseau_identique_a_la_note_pour_w_0_3():
    """Script `t10c` de la note : Φ̂ médian 6,84 (c = 0,01) et 2,99 (c = 0,03) ; AUC 0,85 (20 sociétés × 200 pas)."""
    W = matrice_grille(10)
    est = {}
    for c in (0.01, 0.03):
        v = []
        for i in range(20):
            _, _, H = simuler_reseau(R0, c, ML, 0.3, W, 200, np.random.default_rng(500 + i + int(c * 1000)), 1, True, 200)
            a = ajuster_reseau(H, W)
            assert isinstance(a, AjustementReseau) and a.c == pytest.approx(a.c_yy + a.c_yw + a.c_ww)
            v.append(min(a.phi, 99))
        est[c] = np.array(v)
    assert np.median(est[0.01]) == pytest.approx(6.84, abs=0.02)
    assert np.median(est[0.03]) == pytest.approx(2.99, abs=0.02)
    assert auc(-est[0.03], -est[0.01]) == pytest.approx(0.85, abs=0.01)


def test_ajustement_reseau_sans_paire_complete():
    W = matrice_grille(3)
    H = np.full((5, 1, 9), np.nan)
    with pytest.raises(ValueError, match="Aucune paire"):
        ajuster_reseau(H, W)


def test_w_estime_nan_si_courbures_non_positives():
    a = AjustementReseau(1, 0.1, 0.1, -0.01, 0.0, 0.02, 0.5, 3.0, float("inf"))
    assert np.isnan(a.w_estime)
    b = AjustementReseau(1, 0.1, 0.1, 0.01, 0.0, 0.04, 0.5, 3.0, 1.0)
    assert b.w_estime == pytest.approx(2 / 3)  # √0,04 / (√0,01 + √0,04)


def test_auc():
    assert auc([3, 4, 5], [0, 1, 2]) == 1.0 and auc([0, 1], [3, 4]) == 0.0
    assert auc([1, 1], [1, 1]) == 0.5
    rng = np.random.default_rng(0)
    assert auc(rng.normal(size=500), rng.normal(size=500)) == pytest.approx(0.5, abs=0.06)


def test_tendance_de_kendall():
    assert tendance_kendall([1, 2, 3, 4]) == pytest.approx(1.0) and tendance_kendall([4, 3, 2, 1]) == pytest.approx(-1.0)
    assert tendance_kendall([2, 2, 2, 2]) == 0.0
    assert np.isnan(tendance_kendall([2, 2, 2, 2], nan_en_zero=False))
