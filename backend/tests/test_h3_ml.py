"""Tests pour le classifieur double-entree temporel+spatial (§2.3) --
proprietes verifiables, peu de realisations (rapide), style deja etabli."""
import numpy as np

from app.h3_ml import DualBranchFusionClassifier, classical_joint_predictions, generate_joint_dataset
from app.lyapunov_precedence import random_irregular_weights

WINDOW_LEN = 60


def test_generate_joint_dataset_shapes_are_consistent():
    w_real = random_irregular_weights(12, seed=1)
    x_temporal, x_spatial, y = generate_joint_dataset(
        w_real, n_runs_per_class=3, seed0=0, window_len=WINDOW_LEN, t_max=40.0, snapshot_stride=5, horizon_steps=100
    )
    assert x_temporal.shape[1] == WINDOW_LEN
    assert x_spatial.shape[1] == 12
    assert x_temporal.shape[0] == x_spatial.shape[0] == len(y)
    assert set(np.unique(y)) <= {0.0, 1.0}


def test_generate_joint_dataset_has_some_positive_examples_when_tipping():
    # mu_rate assez rapide pour que mu(t)=-2+mu_rate*t franchisse 0 tres tot
    # (t~20 ici) et laisse largement le temps a l'echappement bruite avant
    # t_max -- avec un horizon large, au moins quelques fenetres positives
    # doivent apparaitre parmi les runs qui basculent reellement.
    w_real = random_irregular_weights(10, seed=2)
    _, _, y = generate_joint_dataset(
        w_real, n_runs_per_class=4, seed0=5, window_len=WINDOW_LEN, t_max=100.0,
        mu_rate_tip=0.1, snapshot_stride=5, horizon_steps=300,
    )
    assert (y == 1).sum() > 0


def test_classifier_forward_pass_returns_one_logit_per_example():
    w_real = random_irregular_weights(8, seed=3)
    model = DualBranchFusionClassifier(WINDOW_LEN, w_real, seed=0)
    rng = np.random.default_rng(0)
    xt = rng.normal(size=(5, WINDOW_LEN)).astype(np.float32)
    xs = rng.normal(size=(5, 8)).astype(np.float32)
    model._mean, model._std = 0.0, 1.0
    probs = model.predict_proba(xt, xs)
    assert probs.shape == (5,)
    assert np.all((probs >= 0) & (probs <= 1))


def test_classifier_training_reduces_loss_on_toy_task():
    w_real = random_irregular_weights(10, seed=4)
    x_temporal, x_spatial, y = generate_joint_dataset(
        w_real, n_runs_per_class=5, seed0=20, window_len=WINDOW_LEN, t_max=60.0,
        mu_rate_tip=0.03, snapshot_stride=5, horizon_steps=200,
    )
    model = DualBranchFusionClassifier(WINDOW_LEN, w_real, seed=1)
    losses = model.fit(x_temporal, x_spatial, y, epochs=15, seed=1)
    assert losses[-1] < losses[0]


def test_classical_joint_predictions_returns_binary_array_matching_length():
    w_real = random_irregular_weights(9, seed=5)
    x_temporal, x_spatial, y = generate_joint_dataset(
        w_real, n_runs_per_class=3, seed0=30, window_len=WINDOW_LEN, t_max=40.0, snapshot_stride=5, horizon_steps=100
    )
    preds = classical_joint_predictions(x_temporal, x_spatial, w_real)
    assert preds.shape == y.shape
    assert set(np.unique(preds)) <= {0.0, 1.0}


def test_save_and_load_checkpoint_roundtrip(tmp_path):
    w_real = random_irregular_weights(8, seed=6)
    model = DualBranchFusionClassifier(WINDOW_LEN, w_real, seed=2)
    rng = np.random.default_rng(2)
    xt = rng.normal(size=(4, WINDOW_LEN)).astype(np.float32)
    xs = rng.normal(size=(4, 8)).astype(np.float32)
    model._mean, model._std = 0.0, 1.0
    before = model.predict_proba(xt, xs)

    path = tmp_path / "h3_checkpoint.pt"
    model.save(str(path))

    reloaded = DualBranchFusionClassifier(WINDOW_LEN, w_real, seed=999)
    reloaded.load(str(path))
    after = reloaded.predict_proba(xt, xs)
    assert np.allclose(before, after)
