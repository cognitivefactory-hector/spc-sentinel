"""Short-horizon drift forecaster: estimate time-to-breach for a signal.

A least-squares line is fit over the last `window` samples; its slope (per-sample
rate of change) and fitted current level are projected to whichever control limit the
signal is heading toward. samples-to-breach is converted to seconds via the sample
rate. This is the deliberately *explainable* "learned" piece — a slope an operator can
read off the chart, not a black box (see DECISIONS.md).

`window` is the single documented sensitivity knob (PLAN.md §7): a shorter window
reacts faster to a fresh drift — more lead time but more false alarms — while a longer
window is steadier. Its value is defended in the whiteboard session (WHITEBOARD-DRILL
Q3), tied to the cost asymmetry between a nuisance alarm and a scrapped lot.
"""

from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np

from sentinel.spc.limits import ControlLimits

DEFAULT_WINDOW = 30
# Slopes with magnitude at or below this count as flat (no breach projected).
SLOPE_EPSILON = 1e-9


@dataclass(frozen=True)
class Forecast:
    slope: float  # fitted change per sample
    level: float  # fitted value at the most recent sample
    direction: str  # "up" | "down" | "flat"
    target_limit: float | None  # the limit being approached (UCL/LCL), or None if flat
    samples_to_breach: float | None  # >= 0, or None if not heading toward a limit
    seconds_to_breach: float | None
    # |slope| / SE(slope): how many standard errors the trend is from zero. A
    # significance gate on this is what separates a real drift from noise wander.
    slope_t: float = 0.0


def _slope_t_statistic(x, values, slope: float, intercept: float) -> float:
    """Two-sided t-statistic for the regression slope (|slope| / standard error)."""
    n = len(values)
    if n <= 2:
        return 0.0
    residuals = np.asarray(values, dtype=float) - (slope * x + intercept)
    sse = float(np.sum(residuals**2))
    sxx = float(np.sum((x - x.mean()) ** 2))
    if sxx == 0:
        return 0.0
    if sse == 0:
        # A perfect fit with nonzero slope is maximally significant.
        return float("inf") if abs(slope) > SLOPE_EPSILON else 0.0
    se_slope = (sse / (n - 2)) ** 0.5 / sxx**0.5
    return abs(slope) / se_slope


def forecast(
    values: Sequence[float],
    limits: ControlLimits,
    window: int = DEFAULT_WINDOW,
    sample_rate_hz: float = 1.0,
) -> Forecast:
    """Project a linear trend to the next control-limit breach.

    Raises ValueError if fewer than two points are available (need two to fit a line).
    """
    if len(values) < 2:
        raise ValueError("forecast needs at least two points to fit a trend")

    recent = list(values[-window:])
    x = np.arange(len(recent))
    slope, intercept = np.polyfit(x, recent, 1)
    slope = float(slope)
    level = float(slope * (len(recent) - 1) + intercept)
    slope_t = _slope_t_statistic(x, recent, slope, intercept)

    if slope > SLOPE_EPSILON:
        direction, target = "up", limits.ucl
    elif slope < -SLOPE_EPSILON:
        direction, target = "down", limits.lcl
    else:
        return Forecast(
            slope=slope,
            level=level,
            direction="flat",
            target_limit=None,
            samples_to_breach=None,
            seconds_to_breach=None,
            slope_t=slope_t,
        )

    # Clamp to zero: a negative projection means the limit is already breached.
    samples = max(0.0, (target - level) / slope)
    seconds = samples / sample_rate_hz
    return Forecast(
        slope=slope,
        level=level,
        direction=direction,
        target_limit=target,
        samples_to_breach=samples,
        seconds_to_breach=seconds,
        slope_t=slope_t,
    )
