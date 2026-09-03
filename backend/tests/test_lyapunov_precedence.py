"""Tests de non-regression pour la reproduction de §5.6quater/quinquies --
cahier des charges §7bis point 5. Peu de realisations (rapide pour la CI) :
on verifie les PROPRIETES QUALITATIVES (bascule effective, precedence
majoritaire, avance mesurable), pas un chiffre exact -- le Monte-Carlo est
stochastique et le nombre de realisations ici est volontairement petit.
"""
import numpy as np

from app.lyapunov_precedence import (
    detect_precedence,
    laplacian,
    morans_i_instant,
    random_irregular_weights,
    ring_weights,
    run_precedence_batch,
    simulate_saddle_node,
)


def test_ring_weights_is_symmetric_and_each_node_has_two_neighbors():
    W = ring_weights(10)
    assert np.allclose(W, W.T)
    assert np.all(W.sum(axis=1) == 2)


def test_laplacian_rows_sum_to_zero():
    W = ring_weights(12)
    L = laplacian(W)
    assert np.allclose(L.sum(axis=1), 0)


def test_random_irregular_network_is_connected():
    # Verifie la connexite via une recherche en largeur sur la matrice de poids.
    W = random_irregular_weights(20, seed=3)
    visited = {0}
    frontier = [0]
    while frontier:
        node = frontier.pop()
        for neighbor in np.where(W[node] > 0)[0]:
            if neighbor not in visited:
                visited.add(neighbor)
                frontier.append(neighbor)
    assert len(visited) == 20


def test_morans_i_instant_matches_reference_chain_example():
    values = np.array([1.0, 2.0, 3.0, 4.0])
    W = np.array([[0, 1, 0, 0], [1, 0, 1, 0], [0, 1, 0, 1], [0, 0, 1, 0]], dtype=float)
    assert morans_i_instant(values, W) == __import__("pytest").approx(1 / 3, abs=1e-9)


def test_saddle_node_simulation_escapes_near_theoretical_bifurcation_time():
    # mu(t) = -2 + 0.005*t atteint 0 a t=400 -- avec la calibration retenue
    # (sigma=0.2), l'echappement doit survenir a proximite (pas des le debut,
    # pas jamais dans la fenetre testee).
    W = ring_weights(20)
    sim = simulate_saddle_node(W, coupling="diffusive", seed=1, t_max=500)
    assert sim["t_escape"] is not None
    assert 300 < sim["t_escape"] < 500


def test_detect_precedence_returns_earlier_crossing_for_synthetic_series():
    dt = 0.1
    n = 200
    times = np.arange(n) * dt
    # signal "xbar" plat puis qui bouge fort a partir de l'indice 100 (variance monte tot)
    xbar = np.concatenate([np.zeros(100), np.linspace(0, 5, 100)])
    # "moran" plat puis qui monte plus tard (a partir de l'indice 150)
    moran = np.concatenate([np.full(150, 0.1), np.linspace(0.1, 2.0, 50)])
    result = detect_precedence(times, xbar, moran, dt=dt, window_time=1.0, baseline_time=5.0)
    assert result["t_var"] is not None
    assert result["t_moran"] is not None
    assert result["t_var"] < result["t_moran"]


def test_precedence_batch_on_ring_is_majority_variance_first():
    # Reproduction §5.6quater sur l'anneau, peu de realisations (rapide) --
    # doit rester dans le meme sens que le resultat documente (variance precede
    # Moran dans la grande majorite des cas), sans exiger le meme pourcentage
    # exact (Monte-Carlo, echantillon reduit ici).
    W = ring_weights(40)
    result = run_precedence_batch(W, "diffusive", n_reps=8, seed0=2000)
    assert result["n_tipped"] >= 6  # la plupart des realisations doivent basculer reellement
    assert result["precedence_rate"] is not None
    assert result["precedence_rate"] >= 0.6
    assert result["advance_var"] > result["advance_moran"]  # la variance detecte plus tot


def test_precedence_batch_reproducible_with_seed():
    W = ring_weights(30)
    a = run_precedence_batch(W, "diffusive", n_reps=4, seed0=99)
    b = run_precedence_batch(W, "diffusive", n_reps=4, seed0=99)
    assert a["n_precedence"] == b["n_precedence"]
    assert a["advance_var"] == b["advance_var"]
