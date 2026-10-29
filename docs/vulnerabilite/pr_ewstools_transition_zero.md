# Texte de la PR ewstools « transition=0 » (à publier par Clément ; aucune mention d'outil)

Branche locale prête : `fix-transition-zero` dans `C:\Users\Utilisateur\Desktop\ewstools` (1 commit, `90cec5c`, au-dessus de `main`).
Ce texte est celui à coller dans GitHub. Rien n'a été poussé ni publié.

Commandes pour publier (dans le clone ewstools) :

```
git push fork fix-transition-zero
```

Puis, sur GitHub : « Compare & pull request » depuis ta branche `fix-transition-zero` vers `ThomasMBury/ewstools`, `main`.

---

**Titre :** Honour `transition=0` in `TimeSeries` and `MultiTimeSeries`

**Description :**

`transition=0` is silently ignored. The constructors and about a dozen methods test truthiness (`if self.transition:`, `float(transition) if transition else transition`), and `0` is falsy, so a series indexed from a negative time with the tipping point at time zero is treated as if no transition had been given: every indicator is computed over the whole series, past the transition.

Reproduction on current `main`:

```python
import numpy as np, pandas as pd, ewstools
rng = np.random.default_rng(0)
s = pd.Series(rng.normal(size=100).cumsum() * 0.1, index=np.arange(-50, 50))

for tr in (0, None, 30):
    ts = ewstools.TimeSeries(s, transition=tr)
    ts.compute_var(rolling_window=0.25)
    print(tr, ts.ews["variance"].notna().sum())
# 0    76   <- same as no transition
# None 76
# 30   62
```

`MultiTimeSeries` behaves the same way: with `transition=0`, `compute_corr` runs to the last time point (49) as without a transition, while `transition=30` stops at 30.

**Fix:** `is not None` instead of truthiness in the two constructors (`float(transition) if transition is not None else None`), in the 13 `if self.transition:` checks (`detrend`, `compute_var`, `compute_std`, `compute_cv`, `compute_auto`, `compute_skew`, `compute_kurt`, `compute_entropy`, `compute_dfa`, `compute_spectrum`, and `detrend`, `compute_covar`, `compute_corr` on `MultiTimeSeries`), and in `apply_classifier_inc` (`not self.transition`). Behaviour for `transition=None` and for non-zero transitions is unchanged; `transition` is still stored as a `float`.

**Tests:** `tests/test_transition_zero.py` (15 tests). 13 of them fail on `main` and pass with the fix; the other two pin the unchanged behaviour for `None` and for a positive transition. They cover `compute_var`, `compute_std`, `compute_cv`, `compute_skew`, `compute_kurt`, `compute_auto`, `compute_dfa`, `detrend`, `compute_spectrum`, and the `MultiTimeSeries` correlation, covariance and detrend. One test checks that a series with `transition=0` gives the same indicators as the same data shifted by +50 with `transition=50`. Full suite: 46 passed, 1 skipped (the TensorFlow one).

Not covered by a test: `compute_entropy` and `apply_classifier_inc` (the latter needs a TensorFlow classifier). The change in both is the same one-line condition.

`CHANGELOG.md` has an entry under `[Unreleased]`.

One thing left alone on purpose: `float(transition)` still rejects a `pd.Timestamp`; that is a separate question.
