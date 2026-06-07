"""Tests for the short-horizon drift forecaster.

The forecaster fits a least-squares line over the last `window` points, then projects
the slope to whichever control limit it is heading toward to estimate time-to-breach.
`window` is the documented sensitivity knob: a shorter window reacts faster to a fresh
drift (more lead time, more false alarms); a longer one is steadier (see WHITEBOARD-
DRILL.md Q3). Tests use a standardized chart (centerline=0, sigma=1 → UCL=+3, LCL=-3).
"""

import pytest

from sentinel.spc.forecast import forecast
from sentinel.spc.limits import ControlLimits

STD = ControlLimits(centerline=0.0, sigma=1.0)


def test_downward_ramp_gives_finite_decreasing_time_to_breach():
    # Acceptance (PLAN.md M3): a known downward ramp yields a finite,
    # decreasing time-to-breach as the signal approaches the LCL.
    ramp = [round(-0.3 * i, 6) for i in range(9)]  # 0, -0.3, ..., -2.4
    early = forecast(ramp[:5], STD)
    late = forecast(ramp[:8], STD)

    assert early.direction == "down"
    assert early.target_limit == STD.lcl
    assert early.samples_to_breach is not None and late.samples_to_breach is not None
    assert late.samples_to_breach < early.samples_to_breach
    assert late.samples_to_breach > 0


def test_rising_ramp_targets_upper_limit():
    rising = [0.0, 0.5, 1.0, 1.5, 2.0]
    f = forecast(rising, STD)
    assert f.direction == "up"
    assert f.target_limit == STD.ucl
    # level ~2.0, slope ~0.5, UCL=3 -> (3-2)/0.5 = 2 samples.
    assert f.samples_to_breach == pytest.approx(2.0)


def test_flat_signal_predicts_no_breach():
    flat = [5.0, 5.0, 5.0, 5.0, 5.0]
    f = forecast(flat, ControlLimits(centerline=5.0, sigma=1.0))
    assert f.direction == "flat"
    assert f.samples_to_breach is None
    assert f.seconds_to_breach is None


def test_seconds_to_breach_uses_sample_rate():
    rising = [0.0, 0.5, 1.0, 1.5, 2.0]  # 2 samples to breach
    f = forecast(rising, STD, sample_rate_hz=0.5)
    assert f.seconds_to_breach == pytest.approx(2.0 / 0.5)  # 4 seconds


def test_already_breached_clamps_to_zero():
    past = [-2.0, -2.5, -3.5]  # already below LCL and still falling
    f = forecast(past, STD)
    assert f.direction == "down"
    assert f.samples_to_breach == 0.0


def test_window_limits_points_used():
    # Flat for a long stretch, then a steep recent drop. A short window sees the
    # steep slope; a long window dilutes it — this is the sensitivity knob.
    series = [0.0] * 10 + [0.0, -1.0, -2.0, -3.0]
    short = forecast(series, STD, window=4)
    long = forecast(series, STD, window=14)
    assert abs(short.slope) > abs(long.slope)


def test_requires_at_least_two_points():
    with pytest.raises(ValueError):
        forecast([5.0], STD)
