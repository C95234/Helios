import warnings

import numpy as np
import pytest

from app.vulnerabilite import estimation as est
from app.vulnerabilite import modele as m
from app.vulnerabilite.garde_fous import Drapeaux, evaluer_garde_fous
from app.vulnerabilite.incertitude import bootstrap_blocs_temps, bootstrap_unites
from app.vulnerabilite.simulation import couper_avant_embrasement, simuler_unites


def _societe(N=60, T=100, c=0.02, graine=0):
    a, mu, _, mp = m.params_depuis_inflammabilite(0.6, c, 3.0)
    return couper_avant_embrasement(simuler_unites(a, mu, c, N, T, np.random.default_rng(graine), y0=3.0), mp, 5)


# ---- bootstrap -----------------------------------------------------------------------------------------
def test_bootstrap_unites_intervalle_coherent_et_reproductible():
    X = _societe()
    f = lambda Z: est.ajuster(Z).phi  # noqa: E731
    i1 = bootstrap_unites(X, f, n_tirages=60, rng=np.random.default_rng(1))
    i2 = bootstrap_unites(X, f, n_tirages=60, rng=np.random.default_rng(1))
    assert (i1.bas, i1.haut) == (i2.bas, i2.haut)
    assert i1.bas < i1.haut and i1.largeur > 0 and i1.niveau == 0.90 and i1.avertissement is None
    assert i1.bas < est.ajuster(X).phi < i1.haut


def test_bootstrap_unites_avertit_sous_trente_unites():
    X = _societe(N=16, T=100)
    with pytest.warns(UserWarning, match="sous-couvre"):
        i = bootstrap_unites(X, lambda Z: est.ajuster(Z).phi, n_tirages=20, rng=np.random.default_rng(0))
    assert i.avertissement and "16" in i.avertissement


def test_bootstrap_ecarte_les_tirages_invalides_et_plafonne():
    X = _societe(N=40)
    compteur = {"n": 0}

    def statistique(Z):
        compteur["n"] += 1
        if compteur["n"] % 4 == 0:
            raise ValueError("tirage inexploitable")
        return 1e6  # sera plafonné

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        i = bootstrap_unites(X, statistique, n_tirages=40, rng=np.random.default_rng(0), plafond=50.0)
    assert i.n_tirages_invalides == 10 and i.n_tirages == 30 and (i.bas, i.haut) == (50.0, 50.0)
    with pytest.raises(ValueError, match="Aucun tirage"):
        bootstrap_unites(X, lambda Z: (_ for _ in ()).throw(ValueError("x")), n_tirages=5, rng=np.random.default_rng(0))


def test_bootstrap_blocs_ne_fabrique_aucune_transition_entre_blocs():
    X = np.tile(np.arange(40, dtype=float)[:, None], (1, 3))  # y_t = t : y_{t+1} − y_t = 1 dans un bloc

    def ecarts_non_unitaires(Z):
        d = Z[1:] - Z[:-1]
        d = d[~np.isnan(d)]
        return float(np.sum(d != 1.0))

    i = bootstrap_blocs_temps(X, ecarts_non_unitaires, taille_bloc=8, n_tirages=30, rng=np.random.default_rng(2))
    assert i.bas == 0.0 and i.haut == 0.0  # aucune paire (t, t+1) ne traverse la jonction de deux blocs
    assert "non testé" in i.avertissement
    with pytest.raises(ValueError, match="taille_bloc"):
        bootstrap_blocs_temps(X, ecarts_non_unitaires, taille_bloc=1)


def test_bootstrap_blocs_sur_ajustement_reel():
    X = _societe(N=60, T=120)
    i = bootstrap_blocs_temps(X, lambda Z: est.ajuster(Z).phi, taille_bloc=20, n_tirages=30, rng=np.random.default_rng(3))
    assert i.n_tirages + i.n_tirages_invalides == 30 and i.bas <= i.haut


@pytest.mark.slow
def test_couverture_de_l_intervalle_a_90_pour_cent_100x200():
    """Cahier : couverture ≈ 90 % (82–97 %). Procédure de `t11` (b) : 60 jeux, 200 tirages, société c = 0,02."""
    a, mu, _, _ = m.params_depuis_inflammabilite(0.6, 0.02, 3.0)
    phi_vrai = m.phi_poisson(0.6, 0.02, 3.0)
    couvre = []
    for i in range(60):
        rng = np.random.default_rng(1000 + i)
        X = est.couper_au_premier_depassement(simuler_unites(a, mu, 0.02, 100, 200, rng, y0=3.0), 6 * 3.0)
        iv = bootstrap_unites(X, lambda Z: est.ajuster(Z).phi, n_tirages=200, rng=rng)
        couvre.append(iv.bas <= phi_vrai <= iv.haut)
    assert 0.82 <= np.mean(couvre) <= 0.97


# ---- garde-fous ---------------------------------------------------------------------------------------
def test_aucun_drapeau_quand_tout_va_bien():
    d = evaluer_garde_fous(phi=8.0, c=0.01, R=0.6, n_unites=96, seuil_coupure=60.0, m_haut_estime=43.0, theta=0.4, ecart_croise=0.02)
    assert d.aucun and d.liste() == []


def test_chaque_drapeau_se_leve_pour_la_bonne_raison():
    assert evaluer_garde_fous(phi=1.4).plancher and not evaluer_garde_fous(phi=2.5).plancher
    assert not evaluer_garde_fous(phi=0.0).plancher  # Φ = 0 correspond à R ≥ 1, signalé à part
    assert not evaluer_garde_fous(phi=float("inf")).plancher
    assert evaluer_garde_fous(n_unites=29).peu_d_unites and not evaluer_garde_fous(n_unites=30).peu_d_unites
    assert evaluer_garde_fous(seuil_coupure=12.0, m_haut_estime=43.0).coupure_trop_basse
    assert not evaluer_garde_fous(seuil_coupure=60.0, m_haut_estime=43.0).coupure_trop_basse
    assert evaluer_garde_fous(theta=1.2).theta_hors_intervalle and evaluer_garde_fous(theta=-0.1).theta_hors_intervalle
    assert evaluer_garde_fous(ecart_croise=-0.3).asymetrie_croisee
    assert evaluer_garde_fous(c=-0.001).pas_de_seuil and evaluer_garde_fous(c=0.0).pas_de_seuil
    assert evaluer_garde_fous(R=1.05).pas_d_etat_calme


def test_les_informations_absentes_ou_nan_ne_levent_rien():
    d = evaluer_garde_fous(phi=float("nan"), c=float("nan"), theta=float("nan"), ecart_croise=float("nan"))
    assert d.aucun
    assert isinstance(d, Drapeaux)


def test_liste_des_drapeaux_levés():
    d = evaluer_garde_fous(phi=1.0, n_unites=10, c=-1.0)
    assert set(d.liste()) == {"plancher", "peu_d_unites", "pas_de_seuil"} and not d.aucun
