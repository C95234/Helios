"""H2 : reproductibilite des graines et verdict robuste a l'aleatoire Monte-Carlo
(Journal §15). Cas reel qui a motive ces tests : p-value 'grille' de H2/logements
autorises = 0.052 (20000 surrogats), mais verdict 'defavorable' dans 19 tirages sur
50 a 500 surrogats -- et graine `hash(str) % 1000`, differente a chaque lancement."""
import math
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

from app.routers.h2 import _outcome, _robust_significant, _stable_seed
from app.schemas import TrendTestOut
from app.stats.surrogates import surrogate_trend_test

BACKEND = Path(__file__).resolve().parent.parent


def _seed_in_fresh_process(key: str, hash_seed: str) -> str:
    code = f"from app.routers.h2 import _stable_seed; print(_stable_seed({key!r}))"
    env = {**os.environ, "PYTHONHASHSEED": hash_seed}
    return subprocess.run([sys.executable, "-c", code], cwd=BACKEND, env=env, capture_output=True, text=True, check=True).stdout.strip()


def test_stable_seed_is_identical_across_python_processes():
    # Avec l'ancien `hash(key) % 1000`, deux lancements donnaient des graines differentes.
    a = _seed_in_fresh_process("construction", "1")
    b = _seed_in_fresh_process("construction", "2")
    assert a == b == str(_stable_seed("construction"))


def test_stable_seed_differs_between_variables_and_is_bounded():
    seeds = {k: _stable_seed(k) for k in ["chomage", "defaillances", "construction", "creations", "population"]}
    assert len(set(seeds.values())) == len(seeds)
    assert all(0 <= s < 1000 for s in seeds.values())


def test_trend_test_reports_monte_carlo_standard_error_and_borderline_flag():
    rng = np.random.default_rng(0)
    series = np.cumsum(rng.normal(size=80)) + 0.05 * np.arange(80)
    r = surrogate_trend_test(series, n_surrogates=400, seed=1)
    p, n = r["p_value"], r["n_surrogates"]
    assert r["p_value_se"] == pytest.approx(math.sqrt(p * (1 - p) / n))
    assert r["borderline"] == (abs(p - 0.05) <= 2 * r["p_value_se"])


def test_borderline_is_false_for_clear_cases():
    rng = np.random.default_rng(3)
    clear_trend = np.arange(120) + rng.normal(scale=0.3, size=120)
    r = surrogate_trend_test(clear_trend, n_surrogates=500, seed=1)
    assert r["significant_at_0_05"] and not r["borderline"]


def test_borderline_flag_marks_p_value_within_two_standard_errors_of_threshold():
    # Le cas reel : p ~ 0.052, 5000 surrogats -> erreur-type ~0.003, donc a la limite.
    n, p = 5000, 0.052
    se = math.sqrt(p * (1 - p) / n)
    assert abs(p - 0.05) <= 2 * se
    # ... alors que p = 0.0175 (defaillances, grille) est clairement sous le seuil.
    assert not abs(0.0175 - 0.05) <= 2 * math.sqrt(0.0175 * (1 - 0.0175) / n)


def _trend(sig: bool, borderline: bool) -> TrendTestOut:
    return TrendTestOut(observed_tau=0.1, p_value=0.04 if sig else 0.5, n_surrogates=1000, n_points=100,
                        significant_at_0_05=sig, p_value_se=0.006, borderline=borderline)


def test_borderline_significance_is_not_retained_in_the_outcome():
    grid_borderline = _trend(sig=True, borderline=True)   # ex. 'construction' : p ~ 0.05, le tirage decide
    grid_clear = _trend(sig=True, borderline=False)       # ex. 'defaillances' : p ~ 0.018
    real_ns = _trend(sig=False, borderline=False)
    assert _outcome(_robust_significant(real_ns), _robust_significant(grid_borderline)) == "neutral"
    assert _outcome(_robust_significant(real_ns), _robust_significant(grid_clear)) == "against"
