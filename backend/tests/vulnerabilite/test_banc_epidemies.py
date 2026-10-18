import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from app.vulnerabilite import banc_epidemies as be
from app.vulnerabilite import calendrier as cal

RACINE = Path(__file__).resolve().parents[3] / "data" / "vulnerabilite"
DEPS = ["02", "06", "10", "13", "14", "17", "18", "21", "25", "29", "33", "34", "35", "38", "42", "44", "45", "50", "54", "56"]


def donnees_simulees(graine=0, R=0.7, theta=(0.4, 0.6), N=len(DEPS), T=be.N_SEMAINES):
    """Épidémie simulée : trois vagues nationales, départements de tailles très différentes, deux canaux amincis indépendants.
    L'indicateur d'eaux usées est la croissance du total national vrai, bruitée."""
    rng = np.random.default_rng(graine)
    taille = np.geomspace(1.0, 40.0, N)
    t = np.arange(T)
    vague = sum(np.exp(-0.5 * ((t - c) / 4.0) ** 2) for c in (12, 45, 80))
    y = taille * 4.0
    vrai = np.zeros((T, N))
    for i in range(T):
        y = rng.poisson(taille * (1.0 + 5.0 * vague[i]) * (1 - R) * 4.0 + R * y).astype(float)
        vrai[i] = y
    urgences = np.stack([rng.binomial(vrai[i].astype(int), theta[0]) for i in range(T)]).astype(float)
    sos = np.stack([rng.binomial(vrai[i].astype(int), theta[1]) for i in range(T)]).astype(float)
    semaines = pd.date_range(be.DEBUT, periods=T, freq="7D")
    eaux = vrai.sum(axis=1) * np.exp(rng.normal(0, 0.05, T))

    def jours(X):  # répartition uniforme des comptes hebdomadaires sur 7 jours (somme conservée)
        return np.stack([rng.multinomial(int(X[i, d]), np.full(7, 1 / 7)) for i in range(X.shape[0]) for d in range(X.shape[1])]).reshape(T, N, 7).transpose(0, 2, 1).reshape(7 * T, N).astype(float)

    urg_j, sos_j = jours(urgences), jours(sos)
    vac = {z: [(pd.Timestamp("2023-02-18"), pd.Timestamp("2023-03-06")), (pd.Timestamp("2024-07-06"), pd.Timestamp("2024-09-02"))] for z in ("Zone A", "Zone B", "Zone C", "Corse")}
    feries = pd.DatetimeIndex(["2023-05-01", "2023-05-08", "2024-05-01", "2024-07-14"])
    stations = pd.DataFrame({f"S{k}": np.where(np.arange(T) >= 62, eaux * (1 + 0.05 * k), np.nan) for k in range(8)}, index=semaines)
    return be.DonneesBanc(
        semaines=semaines, departements=list(DEPS), urgences=urgences, sos=sos, eaux=eaux,
        controles=cal.controles_hebdomadaires(semaines, DEPS, feries, vac),
        urgences_j=urg_j, sos_j=sos_j, controles_j=cal.controles_quotidiens(pd.date_range(be.DEBUT, periods=7 * T, freq="D"), DEPS, feries, vac),
        eaux_stations=stations, stations_departement={f"S{k}": DEPS[k] for k in range(8)},
    )


# ---- briques ---------------------------------------------------------------------------------------------
def test_croissance_eaux_valeur_connue():
    g = be.croissance_eaux(np.exp(0.1 * np.arange(30)), 12)
    assert len(g) == 19 and np.allclose(g, 0.1)
    e = np.exp(0.1 * np.arange(30))
    e[10] = np.nan
    assert np.isnan(be.croissance_eaux(e, 12)[:10]).all() or np.isnan(be.croissance_eaux(e, 12)[0])


def test_fenetres_et_blocs():
    assert len(be.fenetres(105, 12)) == 94 and be.fenetres(105, 12)[-1] == slice(93, 105)
    idx = be._indices_blocs(94, 12, np.random.default_rng(0))
    assert len(idx) == 94 and idx.min() >= 0 and idx.max() < 94
    assert (np.diff(idx[:12]) == 1).all()  # un bloc est fait de fenêtres consécutives


def test_fins_temoins_comme_dans_le_preenregistrement():
    assert be.fins_temoins(105, [10, 31, 72]) == [59, 60, 61, 62, 63, 100, 101, 102, 103, 104]


def test_c1_prime_reussit_quand_le_croise_suit_g_et_pas_les_canaux_seuls():
    rng = np.random.default_rng(0)
    g = np.convolve(rng.normal(size=120), np.ones(8) / 8, mode="valid")[:94]
    r = {"croise": g + rng.normal(0, 0.05 * g.std(), 94), "urgences": rng.normal(size=94), "sos": rng.normal(size=94)}
    res = be.c1_prime(r, g, rng, 300)
    assert res["reussi"] and res["delta"] > 0.5 and res["ic90_delta"][0] > 0 and res["rho_croise"] > 0.9


def test_c1_prime_echoue_quand_un_canal_seul_est_aussi_bon():
    rng = np.random.default_rng(1)
    g = np.convolve(rng.normal(size=120), np.ones(8) / 8, mode="valid")[:94]
    r = {"croise": g + rng.normal(0, 0.3 * g.std(), 94), "urgences": g + rng.normal(0, 0.1 * g.std(), 94), "sos": rng.normal(size=94)}
    res = be.c1_prime(r, g, rng, 300)
    assert not res["reussi"] and res["delta"] < 0


def test_c1_prime_gere_les_fenetres_non_estimables():
    rng = np.random.default_rng(2)
    g = np.arange(94, dtype=float)
    r = {"croise": g.copy(), "urgences": np.sin(g), "sos": np.cos(g)}
    r["croise"][:10] = np.nan
    res = be.c1_prime(r, g, rng, 100)
    assert res["n_fenetres"] == 94 and np.isfinite(res["rho_croise"])


# ---- pipeline complet sur données simulées -----------------------------------------------------------------
@pytest.fixture(scope="module")
def sim():
    return donnees_simulees(graine=3)


@pytest.fixture(scope="module")
def resultat(sim):
    return be.executer_tout(sim, donnees_partielles=sim, graine=7, n_boot=60, n_perm=8, n_placebo=50)


def test_le_pipeline_produit_toutes_les_sections_du_preenregistrement(resultat):
    assert {"C1_prime", "C3_canaux_melanges", "C2_prime", "decision", "sensibilites"} <= set(resultat)
    assert resultat["decision"] in ("succes", "echec_partiel", "echec")
    assert set(resultat["sensibilites"]) == {
        "effets_temporels_complets", "controles_calendrier", "sos_decale_4_jours", "pas_quotidien", "departements_45",
        "fenetre_8_semaines", "fenetre_16_semaines", "stations_eaux_usees",
    }
    for cle, v in resultat["sensibilites"].items():
        assert "delta" in v or "non_concluant" in v or "non_disponible" in v, cle
    c1 = resultat["C1_prime"]
    assert c1["n_fenetres"] == 94 and len(c1["ic90_delta"]) == 2 and isinstance(c1["reussi"], bool)
    assert resultat["sensibilites"]["fenetre_8_semaines"]["n_fenetres"] == 98
    assert resultat["sensibilites"]["fenetre_16_semaines"]["n_fenetres"] == 90
    assert resultat["sensibilites"]["pas_quotidien"]["n_fenetres"] == 94
    json.dumps(resultat)  # sérialisable


def test_c3_et_c2_ont_la_forme_attendue(resultat):
    c3 = resultat["C3_canaux_melanges"]
    assert c3["n_permutations"] == 8 and isinstance(c3["propre"], bool) and np.isfinite(c3["delta_placebo_p95"])
    c2 = resultat["C2_prime"]
    assert len(c2["demarrages"]) >= 2 and all(d >= "2023-02" for d in c2["exploitables"])
    assert c2["n_temoins"] >= 2 and "Descriptif" in c2["avertissement"]
    for v in c2["vagues"]:
        assert set(v["tau"]) == {"R_croise", "R_urgences", "R_sos", "AC1", "variance"}
        assert all(-1.0 <= t <= 1.0 for t in v["tau"].values() if np.isfinite(t))


def test_reproductibilite_a_graine_egale(sim):
    a = be.executer_tout(sim, graine=11, n_boot=30, n_perm=4, n_placebo=20)
    b = be.executer_tout(sim, graine=11, n_boot=30, n_perm=4, n_placebo=20)
    assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)


def test_sur_donnees_simulees_le_r_croise_est_positivement_correle_a_la_croissance(sim):
    c1, r, g = be.analyse_c1(sim, np.random.default_rng(0), n_boot=30)
    assert c1["rho_croise"] > 0.15 and c1["rho_urgences"] > 0.15  # la dynamique simulée est bien captée


def test_decalage_sos_decale_vers_l_avant_et_perd_la_premiere_semaine(sim):
    d = be._variante_decalage(sim, 4)
    assert np.isnan(d.sos[0]).all() and np.array_equal(d.sos[1:, :], be.semaines_depuis_jours(d.sos_j)[1:, :])
    assert np.allclose(d.sos_j[4:], sim.sos_j[:-4])
    assert sim.sos.shape == d.sos.shape


def test_variante_stations_sur_donnees_simulees(sim):
    res = be._variante_stations(sim, np.random.default_rng(0), 30)
    assert res["n_fenetres"] > 20 and len(res["departements"]) == 8


def test_variante_stations_non_disponible_et_non_concluante(sim):
    assert be._variante_stations(be.DonneesBanc(**{**sim.__dict__, "eaux_stations": None}), np.random.default_rng(0), 10) == {"non_disponible": True}
    peu = be.DonneesBanc(**{**sim.__dict__, "stations_departement": {"S0": DEPS[0], "S1": DEPS[1]}})
    assert be._variante_stations(peu, np.random.default_rng(0), 10)["non_concluant"] is True


def test_semaines_depuis_jours_propage_les_manques():
    X = np.ones((14, 2))
    X[3, 1] = np.nan
    s = be.semaines_depuis_jours(X)
    assert s.shape == (2, 2) and s[0, 0] == 7 and np.isnan(s[0, 1]) and s[1, 1] == 7


# ---- chargement des données réelles : structure uniquement, aucune statistique d'évaluation -----------------
@pytest.mark.skipif(not (RACINE / "raw" / "sursaud-covid-quot-dep-2025-01-01-18h00.csv").exists(), reason="données brutes absentes (hors git)")
def test_chargement_des_donnees_reelles_structure():
    d = be.charger_donnees(RACINE)
    assert len(d.departements) == 37 and d.urgences.shape == (105, 37) and d.sos.shape == (105, 37)
    assert d.semaines[0] == pd.Timestamp("2022-12-26") and d.semaines[-1] == pd.Timestamp("2024-12-23")
    assert d.urgences_j.shape == (735, 37) and d.controles.shape == (105, 37, 2) and d.controles_j.shape == (735, 37, 8)
    assert np.isfinite(d.eaux).all() and (d.eaux > 0).all()
    assert d.departements[0] == "02" and "75" in d.departements
    p = be.charger_donnees(RACINE, "partielle")
    assert len(p.departements) == 45 and p.departements[:2] == ["02", "06"]
    assert d.eaux_stations is not None and d.stations_departement["AMIENS"] == "80"
    with pytest.raises(ValueError, match="couverture"):
        be.charger_donnees(RACINE, "autre")
