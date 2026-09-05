"""Tests du modele reduit de bilan de puissance -- §7quater. Style deja
etabli (test_kuramoto.py, test_power_law.py) : proprietes verifiables, pas
de nombre magique -- sauf pour `reactivity_dt`, un parametrage empirique
d'un papier (Bosch & Hale, 1992) verifie a une tolerance large ("ordre de
grandeur conforme a la litterature"), pas par un calcul independant type
scipy/statsmodels."""
import numpy as np

from app.plasma_power_balance import (
    ILLUSTRATIVE_IGNITED_HEATING_RATE,
    ILLUSTRATIVE_N_CM3,
    ILLUSTRATIVE_P_HEAT_BASE,
    ILLUSTRATIVE_STABLE_HEATING_RATE,
    ILLUSTRATIVE_TAU_E_S,
    ILLUSTRATIVE_T_MAX_S,
    bremsstrahlung_density,
    find_critical_heating,
    fusion_power_density,
    reactivity_dt,
    simulate_power_balance,
)


def test_reactivity_increasing_and_positive():
    t = np.array([1.0, 2.0, 5.0, 10.0, 20.0, 50.0])
    sv = reactivity_dt(t)
    assert np.all(sv > 0)
    assert np.all(np.diff(sv) > 0)  # croissante sur cette plage (avant le maximum ~65 keV)


def test_reactivity_order_of_magnitude_matches_literature():
    # Valeurs couramment citees pour D-T (Bosch & Hale, 1992) : ~1.1e-16
    # cm^3/s a 10 keV, ~4.2e-16 a 20 keV -- tolerance large, pas une
    # comparaison a une decimale pres.
    sv_10 = reactivity_dt(np.array([10.0]))[0]
    sv_20 = reactivity_dt(np.array([20.0]))[0]
    assert 5e-17 < sv_10 < 3e-16
    assert 2e-16 < sv_20 < 8e-16


def test_fusion_and_radiation_power_positive_and_scale_with_density():
    t = np.array([10.0])
    n_low, n_high = 1e14, 2e14
    assert fusion_power_density(t, n_high)[0] > fusion_power_density(t, n_low)[0]
    assert bremsstrahlung_density(t, n_high)[0] > bremsstrahlung_density(t, n_low)[0]
    # Puissance de fusion (auto-chauffage alpha) proportionnelle a n^2.
    ratio = fusion_power_density(t, n_high)[0] / fusion_power_density(t, n_low)[0]
    assert abs(ratio - (n_high / n_low) ** 2) < 1e-9


def test_bifurcation_point_exists_for_illustrative_parameters():
    """Le point de bifurcation noeud-col (§7quater) existe bien pour les
    parametres illustratifs du module : un chauffage juste sous le seuil a
    un equilibre stable, juste au-dessus n'en a plus aucun."""
    critical = find_critical_heating(ILLUSTRATIVE_N_CM3, ILLUSTRATIVE_TAU_E_S)
    assert critical > ILLUSTRATIVE_P_HEAT_BASE  # le scenario "stable" reste bien sous le seuil
    assert critical < 1.0  # ordre de grandeur coherent (pas une valeur degeneree)


def test_ignited_scenario_reliably_reaches_ignition():
    """Sur les parametres illustratifs, un chauffage qui rampe a
    ILLUSTRATIVE_IGNITED_HEATING_RATE au-dela du seuil critique doit mener
    a l'ignition dans la quasi-totalite des realisations independantes."""
    n_ignited = 0
    for seed in range(20):
        sim = simulate_power_balance(
            ILLUSTRATIVE_N_CM3,
            ILLUSTRATIVE_TAU_E_S,
            heating_rate=ILLUSTRATIVE_IGNITED_HEATING_RATE,
            p_heat_base=ILLUSTRATIVE_P_HEAT_BASE,
            t_max=ILLUSTRATIVE_T_MAX_S,
            seed=seed,
        )
        if sim["t_ignition"] is not None:
            n_ignited += 1
    assert n_ignited >= 18  # >=90% des realisations


def test_stable_scenario_never_reaches_ignition():
    """Un chauffage constant sous le seuil (scenario de controle) ne doit
    jamais atteindre l'ignition sur les parametres illustratifs."""
    for seed in range(20):
        sim = simulate_power_balance(
            ILLUSTRATIVE_N_CM3,
            ILLUSTRATIVE_TAU_E_S,
            heating_rate=ILLUSTRATIVE_STABLE_HEATING_RATE,
            p_heat_base=ILLUSTRATIVE_P_HEAT_BASE,
            t_max=ILLUSTRATIVE_T_MAX_S,
            seed=seed + 5000,
        )
        assert sim["t_ignition"] is None
        assert sim["temperatures"].max() < 10.0  # reste pres de l'equilibre stable (~1.3-1.5 keV)
