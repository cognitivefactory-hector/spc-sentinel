"""Control-limit computation for an individuals (I) chart.

sigma is estimated from the average moving range, sigma_hat = MR_bar / d2, with
d2 = 1.128 for moving ranges of n=2 consecutive points (Montgomery, *Introduction
to Statistical Quality Control*; the classic I-MR chart). The moving-range estimator
is preferred over the raw sample std because the latter inflates sigma when the
warm-up window contains a slow drift — exactly the signal this tool exists to catch.
"""

from collections.abc import Sequence
from dataclasses import dataclass

# Hartley's constant d2 for a moving range of two consecutive observations.
D2_N2 = 1.128


@dataclass(frozen=True)
class ControlLimits:
    """Centerline and sigma for a signal, with zone helpers for the rule engine."""

    centerline: float
    sigma: float

    def upper(self, k: float) -> float:
        """Upper boundary at k sigma above the centerline (k=1/2/3 → zones C/B/A)."""
        return self.centerline + k * self.sigma

    def lower(self, k: float) -> float:
        """Lower boundary at k sigma below the centerline."""
        return self.centerline - k * self.sigma

    @property
    def ucl(self) -> float:
        return self.upper(3)

    @property
    def lcl(self) -> float:
        return self.lower(3)


def control_limits(values: Sequence[float]) -> ControlLimits:
    """Compute centerline + sigma from an in-control warm-up window.

    Raises ValueError if fewer than two points are given (a moving range needs two).
    """
    if len(values) < 2:
        raise ValueError("control_limits needs at least two points to form a moving range")

    centerline = sum(values) / len(values)
    moving_ranges = [abs(values[i] - values[i - 1]) for i in range(1, len(values))]
    mr_bar = sum(moving_ranges) / len(moving_ranges)
    sigma = mr_bar / D2_N2
    return ControlLimits(centerline=centerline, sigma=sigma)
