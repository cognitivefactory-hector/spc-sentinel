"""Tests for control-limit computation (individuals chart).

sigma is estimated from the average moving range, sigma_hat = MR_bar / d2, with
d2 = 1.128 for moving ranges of n=2 consecutive points (Montgomery, *Introduction
to Statistical Quality Control*). This is the standard I-chart estimator rather than
the raw sample std, which inflates sigma when the warm-up window contains drift.
"""

import pytest

from sentinel.spc.limits import control_limits

# [10,12,10,12,10,12]: mean=11, every moving range=2, so MR_bar=2.
WARMUP = [10, 12, 10, 12, 10, 12]
D2 = 1.128
EXPECTED_SIGMA = 2 / D2


def test_centerline_is_mean():
    assert control_limits(WARMUP).centerline == pytest.approx(11.0)


def test_sigma_from_average_moving_range():
    assert control_limits(WARMUP).sigma == pytest.approx(EXPECTED_SIGMA, rel=1e-9)


def test_ucl_and_lcl_are_three_sigma():
    limits = control_limits(WARMUP)
    assert limits.ucl == pytest.approx(11 + 3 * EXPECTED_SIGMA)
    assert limits.lcl == pytest.approx(11 - 3 * EXPECTED_SIGMA)


def test_zone_boundaries_at_k_sigma():
    limits = control_limits(WARMUP)
    assert limits.upper(2) == pytest.approx(11 + 2 * EXPECTED_SIGMA)
    assert limits.lower(1) == pytest.approx(11 - 1 * EXPECTED_SIGMA)


def test_requires_at_least_two_points():
    # A moving range needs two consecutive points.
    with pytest.raises(ValueError):
        control_limits([5])
