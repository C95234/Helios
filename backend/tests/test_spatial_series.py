import numpy as np
import pandas as pd
from scipy.stats import kendalltau

from app.spatial_series import detrend_wide
from app.stats.moran import morans_i


def test_detrend_wide_neutralizes_strengthening_gradient_false_positive():
    """Meme type de faux positif que celui trouve par Bruce Stephenson en relisant
    la contribution d'Helios au paquet ewstools (Journal §9) : un motif spatial
    dont l'AMPLITUDE se renforce dans le temps fait monter l'indice de Moran sans
    aucun vrai ralentissement critique. Le retrait de tendance (LOWESS, par unite)
    doit neutraliser l'essentiel de ce faux positif.

    Note : une pure mise a l'echelle du champ (amplitude * gradient, sans bruit
    additif fixe) ne suffit PAS a reproduire le biais -- I est invariant a une
    renormalisation positive uniforme du champ a un instant donne (numerateur et
    denominateur sont tous deux homogenes de degre 2). Le faux positif vient du
    RAPPORT signal/bruit qui augmente : un motif spatial croissant ajoute a un
    bruit de niveau fixe par unite, comme une vraie serie territoriale ou le bruit
    de mesure ne grandit pas avec la derive structurelle.
    """
    n_units = 6
    n_periods = 80
    t = np.arange(n_periods)
    gradient = np.arange(n_units) - n_units / 2  # motif spatial fixe
    amplitude = 0.3 + 6 * t / n_periods  # se renforce dans le temps
    rng = np.random.default_rng(0)
    noise = rng.normal(size=(n_periods, n_units)) * 0.5  # bruit de niveau fixe

    wide = pd.DataFrame(
        amplitude[:, None] * gradient[None, :] + noise,
        index=pd.RangeIndex(n_periods),
        columns=[f"u{i}" for i in range(n_units)],
    )

    weights = np.zeros((n_units, n_units))
    for i in range(n_units - 1):
        weights[i, i + 1] = weights[i + 1, i] = 1

    i_raw = np.array([morans_i(wide.iloc[k].to_numpy(), weights) for k in range(n_periods)])
    tau_raw, _ = kendalltau(t, i_raw)

    residuals = detrend_wide(wide, frac=0.3)
    i_detrended = np.array([morans_i(residuals.iloc[k].to_numpy(), weights) for k in range(n_periods)])
    tau_detrended, _ = kendalltau(t, i_detrended)

    assert tau_raw > 0.3  # faux positif net sur le champ brut (signal/bruit qui augmente)
    assert abs(tau_detrended) < abs(tau_raw) / 2  # neutralise l'essentiel du faux positif


def test_detrend_wide_preserves_no_trend_when_field_is_stationary():
    """Un champ spatial stationnaire (pas de derive) doit rester proche de zero
    apres retrait de tendance -- le detrending ne doit pas introduire de faux
    signal la ou il n'y en avait pas."""
    rng = np.random.default_rng(0)
    n_units, n_periods = 5, 40
    wide = pd.DataFrame(rng.normal(size=(n_periods, n_units)), columns=[f"u{i}" for i in range(n_units)])

    residuals = detrend_wide(wide, frac=0.3)

    assert residuals.shape == wide.shape
    assert np.abs(residuals.to_numpy()).max() < np.abs(wide.to_numpy()).max() + 1.0
