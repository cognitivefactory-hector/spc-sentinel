"""Tests for the Western Electric / Nelson rule engine.

Sources: Western Electric Co., *Statistical Quality Control Handbook* (1956);
L. S. Nelson, "The Shewhart Control Chart — Tests for Special Causes",
*Journal of Quality Technology* 16(4), 1984. Each rule has a positive test (a
hand-built series that trips it) and a negative test (a series that does not).

All tests use a standardized chart (centerline=0, sigma=1) so zone boundaries are
simply ±1, ±2, ±3 and the expected indices are obvious by inspection.
"""

from sentinel.spc.limits import ControlLimits
from sentinel.spc.rules import (
    Violation,
    evaluate,
    rule_beyond_3sigma,
    rule_run_one_side,
    rule_trend,
    rule_two_of_three_2sigma,
)

STD = ControlLimits(centerline=0.0, sigma=1.0)


# Rule 1 — a single point beyond 3 sigma.
def test_beyond_3sigma_flags_the_outlier():
    assert rule_beyond_3sigma([0, 1, -1, 3.5, 0], STD) == [3]


def test_beyond_3sigma_flags_below_too():
    assert rule_beyond_3sigma([0, -4.0, 0], STD) == [1]


def test_beyond_3sigma_ignores_points_inside_limits():
    # 2.9 and -2.9 are within 3 sigma — no violation.
    assert rule_beyond_3sigma([0, 1, 2.9, -2.9, 0], STD) == []


# Rule 2 — N points in a row on one side of the centerline (default 9, Nelson).
def test_run_one_side_flags_ninth_point():
    assert rule_run_one_side([1] * 9, STD) == [8]


def test_run_one_side_flags_each_point_extending_the_run():
    assert rule_run_one_side([1] * 11, STD) == [8, 9, 10]


def test_run_one_side_resets_when_a_point_crosses_centerline():
    # Eight above, then one below — the run never reaches nine.
    assert rule_run_one_side([1, 1, 1, 1, 1, 1, 1, 1, -1], STD) == []


def test_run_one_side_centerline_point_breaks_the_run():
    # A point exactly on the centerline is neither above nor below.
    assert rule_run_one_side([1, 1, 1, 1, 0, 1, 1, 1, 1], STD) == []


# Rule 3 — 6 points in a row steadily increasing or decreasing (Nelson trend).
def test_trend_flags_six_rising_points():
    assert rule_trend([1, 2, 3, 4, 5, 6]) == [5]


def test_trend_flags_six_falling_points():
    assert rule_trend([6, 5, 4, 3, 2, 1]) == [5]


def test_trend_ignores_flat_repeat_breaking_strict_monotonicity():
    # The repeated 5 breaks a strictly-increasing run of six.
    assert rule_trend([1, 2, 3, 4, 5, 5]) == []


# Rule 4 — 2 of 3 consecutive points beyond 2 sigma on the same side.
def test_two_of_three_flags_window_with_two_beyond_2sigma():
    assert rule_two_of_three_2sigma([0, 2.5, 2.5], STD) == [2]


def test_two_of_three_requires_same_side():
    # One above +2 sigma, one below -2 sigma — not the same direction.
    assert rule_two_of_three_2sigma([0, 2.5, -2.5], STD) == []


def test_two_of_three_ignores_single_excursions():
    assert rule_two_of_three_2sigma([2.5, 0, 0, 2.5], STD) == []


# Aggregator — runs every rule and labels each hit.
def test_evaluate_returns_labeled_violations():
    violations = evaluate([0, 1, -1, 3.5, 0], STD)
    assert Violation(rule="beyond_3sigma", index=3) in violations


def test_evaluate_clean_series_has_no_violations():
    assert evaluate([0.1, -0.2, 0.3, -0.1, 0.2, -0.3], STD) == []
