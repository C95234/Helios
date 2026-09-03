import numpy as np
import pytest

from app.kuramoto import (
    critical_coupling,
    order_parameter,
    simulate_adaptive_control,
    simulate_uncontrolled,
)


def test_order_parameter_is_one_when_all_phases_equal():
    theta = np.full(20, 1.234)
    assert order_parameter(theta) == pytest.approx(1.0, abs=1e-9)


def test_order_parameter_is_zero_for_perfectly_spread_phases():
    # N phases regulierement espacees sur le cercle -> sum(e^{i*theta}) = 0 exactement.
    n = 12
    theta = np.linspace(0, 2 * np.pi, n, endpoint=False)
    assert order_parameter(theta) == pytest.approx(0.0, abs=1e-9)


def test_order_parameter_always_in_unit_interval():
    rng = np.random.default_rng(0)
    for _ in range(20):
        theta = rng.uniform(-10, 10, size=30)
        r = order_parameter(theta)
        assert -1e-9 <= r <= 1 + 1e-9


def test_critical_coupling_matches_closed_form_for_standard_normal():
    # K_c = 2 / (pi * g(0)), g(0) = 1/sqrt(2*pi) pour omega ~ N(0,1)
    # -> K_c = 2*sqrt(2*pi)/pi
    expected = 2 * np.sqrt(2 * np.pi) / np.pi
    assert critical_coupling(sigma=1.0) == pytest.approx(expected, rel=1e-9)


def test_below_critical_coupling_stays_incoherent():
    k_c = critical_coupling(sigma=1.0)
    result = simulate_uncontrolled(n=200, k=0.3 * k_c, duration=40, dt=0.02, sigma=1.0, seed=42)
    # loin sous K_c, le systeme reste incoherent : r final proche de 0, pas de bascule.
    assert np.mean(result["r"][-100:]) < 0.25


def test_well_above_critical_coupling_synchronizes():
    k_c = critical_coupling(sigma=1.0)
    result = simulate_uncontrolled(n=200, k=3.0 * k_c, duration=40, dt=0.02, sigma=1.0, seed=42)
    # loin au-dessus de K_c, le systeme se synchronise fortement : r -> proche de 1.
    assert np.mean(result["r"][-100:]) > 0.8


def test_uncontrolled_simulation_is_reproducible_with_seed():
    a = simulate_uncontrolled(n=30, k=3.0, duration=10, dt=0.02, seed=7)
    b = simulate_uncontrolled(n=30, k=3.0, duration=10, dt=0.02, seed=7)
    assert np.allclose(a["r"], b["r"])


def test_adaptive_control_keeps_lower_synchronization_than_uncontrolled():
    # Meme K de base, tres au-dessus de K_c (l'increment non-controle s'emballe vers r=1) ;
    # le controle adaptatif doit maintenir une synchronisation nettement plus faible en regime
    # etabli, pour la meme graine (meme frequences propres, memes conditions initiales).
    k_c = critical_coupling(sigma=1.0)
    k = 3.0 * k_c
    n, duration, dt, seed = 60, 40, 0.02, 11

    uncontrolled = simulate_uncontrolled(n=n, k=k, duration=duration, dt=dt, seed=seed)
    controlled = simulate_adaptive_control(
        n=n, k_base=k, r_target=0.5, beta=4.0, duration=duration, dt=dt, seed=seed
    )

    tail = len(uncontrolled["r"]) // 5
    r_unc = np.mean(uncontrolled["r"][-tail:])
    r_ctl = np.mean(controlled["r"][-tail:])

    assert r_unc > 0.8  # confirme que sans controle, le systeme a bien bascule
    assert r_ctl < r_unc - 0.2  # le controle adaptatif reduit nettement la synchronisation


def test_adaptive_control_mean_coupling_drops_below_baseline():
    k = 5.0
    result = simulate_adaptive_control(n=40, k_base=k, r_target=0.5, beta=4.0, duration=30, dt=0.02, seed=3)
    # le couplage effectif moyen doit baisser sous le K_base fixe -- sinon "l'adaptatif" ne fait rien.
    assert np.mean(result["mean_k"][-100:]) < k


def test_adaptive_control_reproducible_with_seed():
    a = simulate_adaptive_control(n=25, k_base=3.0, r_target=0.5, beta=2.0, duration=10, dt=0.02, seed=5)
    b = simulate_adaptive_control(n=25, k_base=3.0, r_target=0.5, beta=2.0, duration=10, dt=0.02, seed=5)
    assert np.allclose(a["r"], b["r"])
    assert np.allclose(a["mean_k"], b["mean_k"])
