import numpy as np
import pandas as pd
import pytest

from app.vulnerabilite import modele as m
from app.vulnerabilite import multicanal as mc
from app.vulnerabilite.interface import estimer_vulnerabilite, preparer_donnees
from app.vulnerabilite.observation import CanauxAmincis, CapteursAffines
from app.vulnerabilite.simulation import simuler_gaussien_capteurs, simuler_multicanal

C, ML, R0 = 0.006, 20.0, 0.6


def _long(O, sources, debut="2020-03-02", freq="D"):
    """Tableau (K, T, N) → format long (une ligne par source, date, unité) ; les NaN sont omis."""
    K, T, N = O.shape
    dates = pd.date_range(debut, periods=T, freq=freq)
    lignes = []
    for k in range(K):
        for t in range(T):
            for n in range(N):
                if not np.isnan(O[k, t, n]):
                    lignes.append((f"D{n:02d}", dates[t], sources[k], O[k, t, n]))
    return pd.DataFrame(lignes, columns=["unite", "date", "source", "valeur"])


def _simuler(K=3, N=40, T=120, graine=0, eta=0.0, c=C):
    a, mu, _, mp = m.params_depuis_inflammabilite(R0, c, ML)
    taux = (0.4, 0.5, 0.6) if K >= 3 else (0.5, 0.6)
    obs = CanauxAmincis(taux, canal_sous_boucle=0 if eta else None, intensite_boucle=eta, forme_boucle="centree", niveau_reference=ML)
    return simuler_multicanal(a, mu, c, N, T, np.random.default_rng(graine), obs, y0=ML, m_haut=mp)[1]


def test_trois_canaux_coherent_avec_l_estimateur_direct():
    O = _simuler(K=3)
    res = estimer_vulnerabilite(_long(O, ["a", "b", "c"]), sources=("a", "b", "c"), pas="jour", effets_fixes="aucun", bootstrap=0)
    assert len(res) == 1
    direct = mc.estimer_multicanal(O, 0, 2, 2)
    assert res.loc[0, "R"] == pytest.approx(direct.R, rel=1e-9) and res.loc[0, "phi"] == pytest.approx(direct.phi, rel=1e-9)
    assert res.loc[0, "R"] == pytest.approx(0.6, abs=0.12)
    colonnes = {"debut", "fin", "R", "c", "s_etoile", "phi", "V_etoile", "theta_a", "theta_b", "theta_c", "drapeaux", "configuration"}
    assert colonnes <= set(res.columns)
    assert res.loc[0, "theta_a"] == pytest.approx(0.4, abs=0.08)


def test_deux_canaux_estime_la_dispersion_et_donne_un_intervalle():
    O = _simuler(K=2, N=60, T=150, graine=1)
    res = estimer_vulnerabilite(_long(O, ["urgences", "sos"]), pas="jour", effets_fixes="aucun", bootstrap=30, graine=3)
    assert res.loc[0, "dispersion"] == pytest.approx(1.0, abs=0.3)  # bruit de Poisson simulé
    assert res.loc[0, "R_bas"] <= res.loc[0, "R_haut"]
    assert res.loc[0, "configuration"] == "deux canaux, dispersion estimée"
    assert np.isfinite(res.loc[0, "r_croise"]) and abs(res.loc[0, "r_croise"] - res.loc[0, "r_croise_inverse"]) < 0.3


def test_un_canal_sous_estime_et_le_dit():
    O = _simuler(K=3, N=40, T=120, graine=2)
    res = estimer_vulnerabilite(_long(O[1:2], ["seul"]), sources=("seul",), pas="jour", effets_fixes="aucun", bootstrap=0)
    assert "non corrigé" in res.loc[0, "configuration"] and np.isnan(res.loc[0, "theta_seul"])
    assert res.loc[0, "R"] < 0.5  # un canal sous-déclaré divise le R apparent (prop. 6)


def test_effets_temporels_et_fenetres_glissantes():
    O = _simuler(K=3, N=40, T=160, graine=4)
    res = estimer_vulnerabilite(_long(O, ["a", "b", "c"]), sources=("a", "b", "c"), pas="jour", effets_fixes="temps",
                                fenetre=80, pas_fenetre=40, bootstrap=0)
    assert len(res) == 3 and np.all(np.isfinite(res["R"]))
    assert (res["debut"].diff().dropna() == pd.Timedelta(days=40)).all() and np.all(res["n_pas"] == 80)


def test_agregation_hebdomadaire_et_semaines_incompletes():
    jours = pd.date_range("2021-01-04", periods=24, freq="D")  # lundi 4 janvier : 3 semaines complètes + 3 jours
    donnees = pd.DataFrame({"unite": "75", "date": jours, "source": "s", "valeur": np.arange(24)})
    O, dates, unites = preparer_donnees(donnees, ["s"], "semaine")
    assert O.shape == (1, 3, 1) and dates[0] == pd.Timestamp("2021-01-04") and unites == ["75"]
    assert O[0, :, 0].tolist() == [sum(range(7)), sum(range(7, 14)), sum(range(14, 21))]


def test_une_semaine_trouee_est_manquante_et_non_nulle():
    jours = pd.date_range("2021-01-04", periods=21, freq="D").delete(10)  # un jour manquant au milieu de la semaine 2
    donnees = pd.DataFrame({"unite": "75", "date": jours, "source": "s", "valeur": 1})
    O, dates, _ = preparer_donnees(donnees, ["s"], "semaine")
    assert O.shape == (1, 3, 1) and np.isnan(O[0, 1, 0]) and O[0, 0, 0] == 7 and O[0, 2, 0] == 7
    # une semaine incomplète en bordure de série est simplement écartée
    bord = pd.DataFrame({"unite": "75", "date": pd.date_range("2021-01-06", periods=12, freq="D"), "source": "s", "valeur": 1})
    assert preparer_donnees(bord, ["s"], "semaine")[0].shape == (1, 1, 1)


def test_validations_des_entrees():
    base = pd.DataFrame({"unite": ["75"] * 3, "date": pd.date_range("2021-01-04", periods=3), "source": "s", "valeur": [1, 2, 3]})
    with pytest.raises(ValueError, match="Colonnes manquantes"):
        preparer_donnees(base.drop(columns="valeur"), ["s"], "jour")
    with pytest.raises(ValueError, match="Source"):
        preparer_donnees(base, ["inconnue"], "jour")
    with pytest.raises(ValueError, match="négatives"):
        preparer_donnees(base.assign(valeur=[1, -2, 3]), ["s"], "jour")
    with pytest.raises(ValueError, match="non entières"):
        preparer_donnees(base.assign(valeur=[1.5, 2.0, 3.0]), ["s"], "jour")  # un taux n'est pas un comptage
    assert preparer_donnees(base.assign(valeur=[1.5, 2.0, 3.0]), ["s"], "jour", comptages=False)[0].shape == (1, 3, 1)
    with pytest.raises(ValueError, match="manquantes"):
        preparer_donnees(base.assign(valeur=[1, np.nan, 3]), ["s"], "jour")
    with pytest.raises(ValueError, match="Doublons"):
        preparer_donnees(pd.concat([base, base]), ["s"], "jour")
    with pytest.raises(ValueError, match="pas"):
        preparer_donnees(base, ["s"], "mois")


def test_les_colonnes_nominatives_sont_refusees_avant_tout_calcul():
    base = pd.DataFrame({"unite": ["75"] * 3, "date": pd.date_range("2021-01-04", periods=3), "source": "s", "valeur": [1, 2, 3]})
    from app.guardrails import NominalDataRejected

    with pytest.raises(NominalDataRejected):
        preparer_donnees(base.assign(nom=["Jean", "Marie", "Luc"]), ["s"], "jour")  # colonne en trop : refusée, pas ignorée


def test_options_non_supportees_sont_refusees_explicitement():
    d = _long(_simuler(K=2, N=10, T=30), ["a", "b"])
    with pytest.raises(NotImplementedError, match="jour de semaine"):
        estimer_vulnerabilite(d, sources=("a", "b"), pas="jour", effets_fixes="jour_semaine")
    with pytest.raises(NotImplementedError, match="voisinage"):
        estimer_vulnerabilite(d, sources=("a", "b"), pas="jour", effets_fixes="aucun", voisinage=pd.DataFrame())
    with pytest.raises(ValueError, match="observation"):
        estimer_vulnerabilite(d, sources=("a", "b"), pas="jour", observation="autre")
    with pytest.raises(ValueError, match="gaussien"):
        estimer_vulnerabilite(d, sources=("a", "b"), pas="jour", effets_fixes="aucun", bruit="gaussien")
    with pytest.raises(ValueError, match="capteurs"):
        estimer_vulnerabilite(d, sources=("a", "b"), pas="jour", effets_fixes="aucun", observation="capteurs_affines")
    with pytest.raises(ValueError, match="bruit"):
        estimer_vulnerabilite(d, sources=("a", "b"), pas="jour", effets_fixes="aucun", bruit="laplace")


def test_avertissement_sous_trente_unites_et_drapeau():
    O = _simuler(K=2, N=12, T=100, graine=5)
    with pytest.warns(UserWarning, match="12 unités"):
        res = estimer_vulnerabilite(_long(O, ["a", "b"]), sources=("a", "b"), pas="jour", effets_fixes="aucun", bootstrap=0)
    assert res.attrs["avertissements"] and "peu_d_unites" in res.loc[0, "drapeaux"]


def test_estimation_impossible_est_rapportee_sans_lever():
    d = pd.DataFrame({"unite": "75", "date": pd.date_range("2021-01-04", periods=2), "source": "s", "valeur": [1, 2]})
    with pytest.warns(UserWarning, match="unités"):
        res = estimer_vulnerabilite(d, sources=("s",), pas="jour", effets_fixes="aucun", bootstrap=0)
    assert res.loc[0, "drapeaux"] == "estimation_impossible" and "Moins de 3" in res.loc[0, "erreur"]


def test_capteurs_affines_renvoient_v_etoile():
    F = lambda x: 0.05 + 0.4 * x + x * x  # noqa: E731
    m0, mp0 = m.zeros_de_derive(F, -2, 2)[:2]
    O = simuler_gaussien_capteurs(F, 0.08, m0, mp0, 50, 200, np.random.default_rng(0), CapteursAffines((2.0, 0.5), (1.0, -3.0), 0.08))
    res = estimer_vulnerabilite(_long(O, ["x", "y"]), sources=("x", "y"), bruit="gaussien", observation="capteurs_affines",
                                pas="jour", effets_fixes="aucun", bootstrap=0)
    assert res.loc[0, "configuration"] == "deux capteurs affines" and 1.0 < res.loc[0, "V_etoile"] < 15.0
