import numpy as np
import pytest

from app.vulnerabilite import estimation as est
from app.vulnerabilite import modele as m
from app.vulnerabilite.simulation import (
    couper_avant_embrasement,
    simuler_societe_chocs_communs,
    simuler_unites,
)

R0, ML = 0.6, 3.0


def _societe(c, N, T, graine):
    a, mu, _, mp = m.params_depuis_inflammabilite(R0, c, ML)
    X = simuler_unites(a, mu, c, N, T, np.random.default_rng(graine), y0=ML)
    return couper_avant_embrasement(X, mp, marge=5)


# ---- copies de référence des fonctions de la note (core.py, v3.1) -------------------------------------
def _ref_phi(R, c, mlow):
    a, mu, s, mp = R - 2 * c * mlow, c * mlow * (mlow + (1 - R) / c), (1 - R) / c, mlow + (1 - R) / c
    return (1 - a) * s - 2 * mu * np.log(mp / mlow)


def _ref_fit(X, weights=True):
    x = X[:-1].ravel()
    y = X[1:].ravel()
    ok = ~np.isnan(x) & ~np.isnan(y)
    x, y = x[ok], y[ok]
    A = np.stack([np.ones_like(x), x, x * x], 1)
    w = np.ones_like(x)
    for _ in range(2 if weights else 1):
        sw = np.sqrt(w)
        b = np.linalg.lstsq(A * sw[:, None], y * sw, rcond=None)[0]
        w = 1 / np.clip(A @ b, 0.5, None)
    mu, a, c = b
    mlow = np.nanmean(X)
    R = a + 2 * c * mlow
    return dict(mu=mu, a=a, c=c, R=R, mlow=mlow, phi=(_ref_phi(R, c, mlow) if (c > 0 and R < 1) else (0.0 if R >= 1 else np.inf)))


def _ref_fit_fe(X):
    x = X[:-1]
    y = X[1:]
    ok = ~np.isnan(x) & ~np.isnan(y)
    rows = []
    for t in range(x.shape[0]):
        mk = ok[t]
        if mk.sum() < 3:
            continue
        xt, yt = x[t, mk], y[t, mk]
        rows.append(np.stack([yt - yt.mean(), xt - xt.mean(), xt * xt - (xt * xt).mean()], 1))
    Mx = np.vstack(rows)
    b = np.linalg.lstsq(Mx[:, 1:], Mx[:, 0], rcond=None)[0]
    a, c = b
    mlow = np.nanmean(X)
    R = a + 2 * c * mlow
    return dict(a=a, c=c, R=R, mlow=mlow, phi=(_ref_phi(R, c, mlow) if (c > 0 and R < 1) else (0.0 if R >= 1 else np.inf)))


def test_ajustement_identique_a_la_note():
    X = _societe(0.02, 100, 200, 11)
    ref, mine = _ref_fit(X), est.ajuster(X)
    assert (mine.mu, mine.a, mine.c, mine.R, mine.m_bas, mine.phi) == pytest.approx(
        (ref["mu"], ref["a"], ref["c"], ref["R"], ref["mlow"], ref["phi"]), rel=1e-12)
    sans_poids = est.ajuster(X, ponderer=False)
    assert sans_poids.c == pytest.approx(_ref_fit(X, weights=False)["c"], rel=1e-12)


def test_effets_temporels_identiques_a_la_note():
    X = _societe(0.02, 60, 100, 12)
    ref, mine = _ref_fit_fe(X), est.ajuster_effets_temporels(X)
    assert (mine.a, mine.c, mine.R, mine.phi) == pytest.approx((ref["a"], ref["c"], ref["R"], ref["phi"]), rel=1e-12)
    assert np.isnan(mine.mu)


def test_recuperation_des_parametres_sur_un_grand_echantillon():
    X = _societe(0.02, 400, 150, 3)
    aj = est.ajuster(X)
    assert aj.R == pytest.approx(R0, abs=0.04)
    assert aj.c == pytest.approx(0.02, rel=0.25)
    assert aj.s_etoile == pytest.approx(20.0, rel=0.3)
    assert 2.5 < aj.phi < 9.0  # Φ vrai = 4,78 ; biais de coupure connu (note, section 2)


def test_niveau_calme_impose():
    X = _societe(0.02, 100, 100, 4)
    aj = est.ajuster(X, niveau_calme=3.0)
    assert aj.m_bas == 3.0 and aj.R == pytest.approx(aj.a + 2 * aj.c * 3.0)


def test_cas_limites_pas_de_seuil_et_pas_d_etat_calme():
    y = np.linspace(1, 40, 60)
    sans_seuil = np.stack([y, 2.0 + 0.8 * y - 0.01 * y**2])  # courbure négative, déterministe
    aj = est.ajuster(sans_seuil)
    assert aj.c < 0 and aj.phi == np.inf and np.isnan(aj.s_etoile)
    explosive = np.stack([y, 0.5 + 1.1 * y + 0.001 * y**2])
    aj2 = est.ajuster(explosive)
    assert aj2.R >= 1 and aj2.phi == 0.0


def test_donnees_insuffisantes_levent_une_erreur():
    X = np.full((10, 3), np.nan)
    X[0, 0], X[1, 0] = 1.0, 2.0
    with pytest.raises(ValueError, match="Moins de 3 paires"):
        est.ajuster(X)
    with pytest.raises(ValueError, match="Aucun instant"):
        est.ajuster_effets_temporels(X)


def test_coupure_au_premier_depassement():
    X = np.array([[1.0, 1.0], [5.0, 1.0], [2.0, 9.0], [3.0, 1.0]])
    coupe = est.couper_au_premier_depassement(X, seuil=5.0, marge=0)
    assert np.array_equal(coupe[:, 0], [1.0, np.nan, np.nan, np.nan], equal_nan=True)
    assert np.array_equal(coupe[:, 1], [1.0, 1.0, np.nan, np.nan], equal_nan=True)
    assert np.array_equal(est.couper_au_premier_depassement(X, 5.0, marge=1)[:, 0], [np.nan] * 4, equal_nan=True)
    assert np.array_equal(est.couper_au_premier_depassement(X, 100.0), X)  # rien à couper


def test_coupure_a_niveau_glissant_identique_a_la_note():
    a, mu, _, _ = m.params_depuis_inflammabilite(R0, 0.02, ML)
    X = simuler_unites(a, mu, 0.02, 80, 150, np.random.default_rng(8), y0=ML)
    # copie de la logique de `t5_derive.society` / `t6_chocs.soc`
    ref = np.full_like(X, np.nan)
    ew = np.full(X.shape[1], 3.0)
    alive = np.ones(X.shape[1], bool)
    for t in range(X.shape[0]):
        ev = alive & (X[t] >= 6 * np.maximum(ew, 1))
        alive &= ~ev
        ref[t, alive] = X[t, alive]
        ew = 0.9 * ew + 0.1 * X[t]
    assert np.array_equal(est.couper_niveau_glissant(X), ref, equal_nan=True)


def test_coupure_iterative_remonte_le_seuil_sans_diverger():
    X = simuler_unites(*m.params_depuis_inflammabilite(R0, 0.02, ML)[:2], 0.02, 100, 200, np.random.default_rng(9), y0=ML)
    aj, seuil = est.ajuster_en_coupant_iterativement(X, k_initial=4.0, niveau_calme=ML)
    assert seuil >= 4.0 * ML
    assert aj.c > 0 or aj.phi in (0.0, np.inf)


def test_fenetres_glissantes():
    X = _societe(0.02, 50, 140, 6)
    resultats = est.ajuster_fenetres(X, taille=60, pas=20)
    assert len(resultats) == 5 and all(r is not None for r in resultats)
    X2 = X.copy()
    X2[:60] = np.nan  # première fenêtre vide
    assert est.ajuster_fenetres(X2, taille=60, pas=20)[0] is None


# ---- tests du tableau du cahier (§3.3), reproduisant les tirages des scripts de la note -------------------
def _phis(c, N, T, reps, graine_de):
    return np.array([min(est.ajuster(_societe_graine(c, N, T, graine_de(r))).phi, 99.0) for r in range(reps)])


def _societe_graine(c, N, T, graine):
    return _societe(c, N, T, graine)


@pytest.mark.slow
@pytest.mark.parametrize("c, phi_vrai, mediane_note", [(0.01, 11.53, 11.0), (0.02, 4.78, 5.0)])
def test_estimation_100x200_mediane_de_phi(c, phi_vrai, mediane_note):
    """Cahier : Φ̂ médian pour Φ = 11,5 / 4,8 → 11,0 / 5,0 à ± 15 % (100 répétitions, graines de `t4`)."""
    valeurs = _phis(c, 100, 200, 100, lambda r: r * 7 + int(c * 1000) + 100 + 200)
    assert np.median(valeurs) == pytest.approx(mediane_note, rel=0.15)


@pytest.mark.slow
@pytest.mark.parametrize("c", [0.01, 0.02, 0.03])
def test_regle_de_coupure_trop_basse_surestime_phi(c):
    """Cahier : coupe à 4 × le niveau calme → Φ̂ > 1,5 Φ ; à 6 × → Φ̂ ≈ Φ (± 10 %) ; graines de `t4c`."""
    a, mu, _, _ = m.params_depuis_inflammabilite(R0, c, ML)
    phi_vrai = m.phi_poisson(R0, c, ML)
    med = {}
    for k in (4, 6):
        valeurs = []
        for r in range(100):
            X = simuler_unites(a, mu, c, 100, 200, np.random.default_rng(r), y0=ML)
            valeurs.append(est.ajuster(est.couper_au_premier_depassement(X, k * ML)).phi)
        med[k] = np.median(valeurs)
    assert med[4] > 1.5 * phi_vrai
    assert med[6] == pytest.approx(phi_vrai, rel=0.10)


@pytest.mark.slow
def test_chocs_communs_effets_fixes_temporels_retrouvent_phi():
    """Cahier : chocs communs croissants, Φ = 11,5 : avec effets fixes temporels Φ̂ ≈ 11,3 (± 20 %) ;
    sans eux l'estimation naïve plafonne (note : médiane > 30, plafonnée à 30 ici comme dans le script)."""
    avec, sans = [], []
    for i in range(30):
        X = simuler_societe_chocs_communs(0.6, np.random.default_rng(i))
        avec.append(min(est.ajuster_effets_temporels(X[240:300]).phi, 30))  # dernière fenêtre de 60 pas
        sans.append(min(est.ajuster(X[240:300]).phi, 30))
    assert np.median(avec) == pytest.approx(11.33, rel=0.20)
    assert np.median(sans) > 2 * 11.53
