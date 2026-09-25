"""Tests pour le classifieur spatial (§2.2) -- proprietes verifiables, pas de
chiffre magique, style deja etabli (test_ml_benchmark.py)."""
import numpy as np

from app.geo import regular_grid_weight_matrix
from app.lyapunov_precedence import random_irregular_weights
from app.spatial_ml import (
    SpatialGraphClassifier,
    classical_moran_predictions,
    generate_topology_dataset,
    normalized_propagation,
)


def test_normalized_propagation_is_symmetric_for_symmetric_weights():
    W = random_irregular_weights(12, seed=1)
    a_hat = normalized_propagation(W)
    assert np.allclose(a_hat, a_hat.T)


def test_normalized_propagation_diagonal_is_positive():
    W, _ = regular_grid_weight_matrix(16)
    a_hat = normalized_propagation(W)
    assert np.all(np.diag(a_hat) > 0)  # boucle propre : chaque noeud se voit lui-meme


def test_generate_topology_dataset_has_balanced_labels_and_right_shape():
    w_real = random_irregular_weights(16, seed=1)
    w_grid, _ = regular_grid_weight_matrix(16)
    X, y = generate_topology_dataset(w_real, w_grid, n_runs_per_class=2, seed0=0, t_max=30.0, snapshot_stride=10)
    assert X.shape[1] == 16
    assert set(np.unique(y)) <= {0.0, 1.0}
    assert (y == 1).sum() > 0
    assert (y == 0).sum() > 0


def test_classifier_forward_pass_returns_one_logit_per_example():
    w_real = random_irregular_weights(10, seed=2)
    w_grid, _ = regular_grid_weight_matrix(10)
    model = SpatialGraphClassifier(w_real, w_grid, seed=0)
    X = np.random.default_rng(0).normal(size=(5, 10)).astype(np.float32)
    probs = model.predict_proba(X)
    assert probs.shape == (5,)
    assert np.all((probs >= 0) & (probs <= 1))


def test_classifier_training_reduces_loss_on_separable_synthetic_task():
    # Tache jouet delibrement facile pour verifier que l'entrainement
    # fonctionne (la loss baisse), pas une mesure de performance realiste.
    w_real = random_irregular_weights(12, seed=3)
    w_grid, _ = regular_grid_weight_matrix(12)
    X, y = generate_topology_dataset(w_real, w_grid, n_runs_per_class=6, seed0=10, t_max=60.0, snapshot_stride=15)
    model = SpatialGraphClassifier(w_real, w_grid, seed=1)
    losses = model.fit(X, y, epochs=15, seed=1)
    assert losses[-1] < losses[0]


def test_classical_moran_predictions_identifies_hand_built_real_pattern():
    # Motif construit a la main, fortement correlé le long des aretes REELLES
    # (valeurs identiques sur chaque paire adjacente du reseau irregulier) et
    # sans rapport avec la grille -- la baseline doit repondre "reseau reel".
    w_real = random_irregular_weights(8, seed=4)
    w_grid, _ = regular_grid_weight_matrix(8)
    # Alterne +1/-1 par composante connexe rudimentaire : utilise directement
    # les valeurs propres de l'adjacence reelle pour garantir une correlation
    # positive maximale avec elle (vecteur propre dominant de W_real).
    eigvals, eigvecs = np.linalg.eigh(w_real)
    x_real_like = eigvecs[:, np.argmax(eigvals)]
    preds = classical_moran_predictions(x_real_like[None, :], w_real, w_grid)
    assert preds[0] == 1.0

    eigvals_g, eigvecs_g = np.linalg.eigh(w_grid)
    x_grid_like = eigvecs_g[:, np.argmax(eigvals_g)]
    preds_grid = classical_moran_predictions(x_grid_like[None, :], w_real, w_grid)
    assert preds_grid[0] == 0.0


def test_save_and_load_checkpoint_roundtrip(tmp_path):
    w_real = random_irregular_weights(10, seed=5)
    w_grid, _ = regular_grid_weight_matrix(10)
    model = SpatialGraphClassifier(w_real, w_grid, seed=2)
    X = np.random.default_rng(1).normal(size=(4, 10)).astype(np.float32)
    before = model.predict_proba(X)

    path = tmp_path / "spatial_checkpoint.pt"
    model.save(str(path))

    reloaded = SpatialGraphClassifier(w_real, w_grid, seed=999)  # graine differente, doit etre ecrasee par load
    reloaded.load(str(path))
    after = reloaded.predict_proba(X)
    assert np.allclose(before, after)
