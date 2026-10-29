import numpy as np
import pytest

from app.vulnerabilite.vagues import detecter_demarrages


def _vague(base=100.0, n=60, debut=20, hauteur=4.0, duree=10):
    S = np.full(n, base)
    for k in range(duree):
        S[debut + k] = base * (1 + (hauteur - 1) * np.sin(np.pi * (k + 1) / (duree + 1)))
    return S


def test_une_vague_nette_donne_un_demarrage_sur_sa_montee():
    S = _vague()
    d = detecter_demarrages(S)
    assert len(d) == 1 and 20 <= d[0] <= 23


def test_deux_vagues_separees_et_une_vague_sans_deuxieme_comptage():
    S = _vague(n=100, debut=20) + _vague(n=100, debut=60) - 100.0
    d = detecter_demarrages(S)
    assert len(d) == 2 and d[1] - d[0] >= 30
    # la période réfractaire empêche de recompter la même vague
    assert all(b - a > 8 for a, b in zip(d, d[1:]))


def test_serie_plate_ou_bruitee_sans_vague():
    rng = np.random.default_rng(0)
    assert detecter_demarrages(np.full(80, 100.0)) == []
    assert detecter_demarrages(100 + rng.normal(0, 5, 80)) == []


def test_plancher_niveau_trop_bas():
    S = _vague(base=5.0, hauteur=10.0)
    assert detecter_demarrages(S) == [] and len(detecter_demarrages(S, plancher=1.0)) == 1


def test_croissance_non_confirmee_ne_declenche_pas():
    S = np.full(40, 100.0)
    S[20] = 400.0  # pic isolé, retombe aussitôt
    assert detecter_demarrages(S) == []


def test_nan_refuse_et_series_courtes():
    with pytest.raises(ValueError, match="NaN"):
        detecter_demarrages([1.0, np.nan, 3.0])
    assert detecter_demarrages([100.0] * 5) == []
