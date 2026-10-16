import pytest

from app.stats.discrimination import fisher_discrimination_p


@pytest.mark.parametrize("hits, fa, expected", [(8, 3, 0.035), (8, 4, 0.085), (8, 5, 0.175), (7, 5, 0.325)])
def test_fisher_discrimination_matches_known_values_for_10_vs_10(hits, fa, expected):
    assert fisher_discrimination_p(hits, 10, fa, 10) == pytest.approx(expected, abs=0.0006)


def test_one_tip_of_difference_in_false_alarms_flips_the_verdict_at_five_percent():
    # Le cas reel de Fusion : le resultat 'favorable' tient a UN tir.
    assert fisher_discrimination_p(8, 10, 3, 10) < 0.05 <= fisher_discrimination_p(8, 10, 4, 10)


def test_fisher_discrimination_is_none_without_both_groups():
    assert fisher_discrimination_p(0, 0, 2, 10) is None
    assert fisher_discrimination_p(3, 10, 0, 0) is None
