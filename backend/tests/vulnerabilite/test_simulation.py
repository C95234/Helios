import numpy as np
import pytest

from app.vulnerabilite import modele as m
from app.vulnerabilite.bruits import BinomialeNegative
from app.vulnerabilite.simulation import (
    couper_avant_embrasement,
    simuler_societe_chocs_communs,
    simuler_unites,
    temps_avant_embrasement,
)

R0, ML = 0.6, 3.0


def _reference_note_simulate_units(a, mu, c, N, T, rng, y0, mp, margin=5):
    """Copie de `core.simulate_units` de la note (scripts v3.1), pour vérifier la fidélité du portage."""
    F = lambda y, a, mu, c: mu + a * y + c * y * y  # noqa: E731
    y = np.full(N, round(y0) if y0 else 3.0)
    X = np.full((T, N), np.nan)
    alive = np.ones(N, bool)
    stop = np.full(N, T)
    for t in range(T):
        y = rng.poisson(np.clip(F(y, a, mu, c), 0, 1e5)).astype(float)
        X[t] = y
        if mp is not None:
            hit = alive & (y >= mp)
            stop[hit] = t
            alive &= ~hit
    for i in range(N):
        X[max(stop[i] - margin, 0):, i] = np.nan
    return X


def test_portage_identique_a_la_simulation_de_la_note():
    a, mu, _, mp = m.params_depuis_inflammabilite(R0, 0.03, ML)
    ref = _reference_note_simulate_units(a, mu, 0.03, 100, 200, np.random.default_rng(5), ML, mp)
    X = couper_avant_embrasement(simuler_unites(a, mu, 0.03, 100, 200, np.random.default_rng(5), y0=ML), mp, marge=5)
    assert np.array_equal(ref, X, equal_nan=True)


def test_meme_graine_memes_series_et_formes():
    a, mu, _, _ = m.params_depuis_inflammabilite(R0, 0.02, ML)
    X1 = simuler_unites(a, mu, 0.02, 20, 50, np.random.default_rng(1), y0=ML)
    X2 = simuler_unites(a, mu, 0.02, 20, 50, np.random.default_rng(1), y0=ML)
    X3 = simuler_unites(a, mu, 0.02, 20, 50, np.random.default_rng(2), y0=ML)
    assert X1.shape == (50, 20) and np.array_equal(X1, X2) and not np.array_equal(X1, X3)
    assert np.all(X1 >= 0) and np.all(X1 == np.floor(X1))


def test_coupure_protocole_de_la_note():
    X = np.array([[1.0, 1.0], [2.0, 1.0], [9.0, 1.0], [4.0, 1.0], [5.0, 1.0], [6.0, 1.0], [7.0, 1.0], [8.0, 1.0]])
    coupe = couper_avant_embrasement(X, m_haut=8.0, marge=2)
    # unité 0 : franchit le seuil au pas 2 (valeur 9 ≥ 8) → coupée à partir de max(2−2, 0) = 0
    assert np.all(np.isnan(coupe[:, 0]))
    # unité 1 : ne franchit jamais → les 2 derniers pas sont retirés (comportement des scripts)
    assert np.array_equal(coupe[:6, 1], np.ones(6)) and np.all(np.isnan(coupe[6:, 1]))


def test_surdispersion_rend_la_simulation_plus_dispersee():
    a, mu, _, _ = m.params_depuis_inflammabilite(R0, 0.01, ML)
    Xp = simuler_unites(a, mu, 0.01, 200, 100, np.random.default_rng(3), y0=ML)
    Xb = simuler_unites(a, mu, 0.01, 200, 100, np.random.default_rng(3), y0=ML, bruit=BinomialeNegative(3.0))
    assert np.var(Xb[20:]) > 1.5 * np.var(Xp[20:])


def test_trajectoire_de_parametres_fait_monter_l_activite():
    T = 80
    c = np.full(T, 0.02)
    a = np.full(T, 0.48)
    mu = np.linspace(1.38, 3.0, T)
    X = simuler_unites(0, 0, 0, 300, T, np.random.default_rng(4), y0=ML, mu_t=mu, a_t=a, c_t=c)
    assert X[-10:].mean() > 1.5 * X[:10].mean()


def test_cecite_second_ordre_ac1_et_dispersion_ne_voient_pas_c():
    """Même R et même m₋, c = 0,01 / 0,02 / 0,03 (Φ = 11,5 / 4,8 / 2,8) : AC1 ≈ R, dispersion ≈ 1/(1−R²)."""
    ac1, fano = [], []
    for c in (0.01, 0.02, 0.03):
        a, mu, _, mp = m.params_depuis_inflammabilite(R0, c, ML)
        X = simuler_unites(a, mu, c, 3000, 150, np.random.default_rng(1), y0=ML)
        calme = ~(X >= mp).any(axis=0)  # trajectoires restées calmes (conditionnement de la note)
        Z = X[50:, calme]
        ac1.append(np.mean([np.corrcoef(z[:-1], z[1:])[0, 1] for z in Z.T[:500]]))
        fano.append(np.mean(Z.var(axis=0) / Z.mean(axis=0)))
    assert ac1 == pytest.approx([R0] * 3, abs=0.04)
    assert max(fano) - min(fano) < 0.2
    assert fano == pytest.approx([1 / (1 - R0**2)] * 3, abs=0.2)
    phis = [m.phi_poisson(R0, c, ML) for c in (0.01, 0.02, 0.03)]
    assert phis[0] > 2 * phis[1] > 2 * phis[2]  # alors que Φ varie d'un facteur ~4


def test_chocs_communs_forme_et_effet_de_l_amplitude():
    X0 = simuler_societe_chocs_communs(0.0, np.random.default_rng(0))
    X1 = simuler_societe_chocs_communs(0.6, np.random.default_rng(0))
    assert X0.shape == X1.shape == (300, 100)
    assert np.isnan(X1).any()  # des chocs forts coupent des unités
    assert np.nanstd(np.nanmean(X1, axis=1)) > np.nanstd(np.nanmean(X0, axis=1))  # la moyenne transversale fluctue davantage


@pytest.mark.slow
def test_loi_des_temps_pente_de_ln_t_en_phi_proche_de_un():
    """Prop. 4 : pente de ln E[T] en Φ ≈ 1. Même procédure et mêmes graines que `t2_temps` de la note
    (R ∈ {0,4 ; 0,6 ; 0,8}, m₋ ∈ {1 ; 3 ; 8}, 1 < Φ < 11, séries censurées à moins de 5 % ; note : 22 jeux,
    pente 1,04, corrélation 0,92)."""
    lignes = []
    for R in (0.4, 0.6, 0.8):
        for ml in (1.0, 3.0, 8.0):
            for c in np.geomspace(0.01, 0.5, 12):
                try:
                    phi = m.phi_poisson(R, c, ml)
                except ValueError:
                    continue
                if not 1.0 < phi < 11.0:
                    continue
                T = temps_avant_embrasement(R, c, ml, n=300, t_max=150_000, seed=int(1000 * c + 10 * R + ml))
                if np.isnan(T).mean() > 0.05:
                    continue
                lignes.append((phi, np.log(np.nanmean(T))))
    assert len(lignes) == 22
    phi, lnT = np.array(lignes).T
    pente = np.polyfit(phi, lnT, 1)[0]
    assert 0.8 <= pente <= 1.3
    assert pente == pytest.approx(1.04, abs=0.02)
    assert np.corrcoef(phi, lnT)[0, 1] == pytest.approx(0.92, abs=0.02)
