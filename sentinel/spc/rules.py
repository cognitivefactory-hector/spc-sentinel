"""Western Electric / Nelson rule engine for an individuals control chart.

Sources: Western Electric Co., *Statistical Quality Control Handbook* (1956);
L. S. Nelson, "The Shewhart Control Chart — Tests for Special Causes",
*Journal of Quality Technology* 16(4), 1984.

These rules are deterministic on purpose — explainability is the whole point of the
project (see DECISIONS.md). The learned part (time-to-breach) lives in forecast.py.

Each rule is a pure function that returns the indices of the points that *trigger*
the violation (the point completing the offending pattern). For run/window rules a
violation can be re-triggered on each subsequent point that still satisfies it.
"""

from collections.abc import Sequence
from dataclasses import dataclass

from sentinel.spc.limits import ControlLimits

# Default lengths. Nelson uses 9 for a one-sided run and 6 for a trend; the Western
# Electric handbook uses 8 for the run. We follow Nelson.
RUN_LENGTH = 9
TREND_LENGTH = 6


@dataclass(frozen=True)
class Violation:
    """A single rule hit at a sample index. Consumed by the alert builder (M4)."""

    rule: str
    index: int


def rule_beyond_3sigma(values: Sequence[float], limits: ControlLimits) -> list[int]:
    """Rule 1: a single point beyond the 3-sigma control limits."""
    return [i for i, x in enumerate(values) if x > limits.ucl or x < limits.lcl]


def rule_run_one_side(
    values: Sequence[float], limits: ControlLimits, n: int = RUN_LENGTH
) -> list[int]:
    """Rule 2: n consecutive points all on the same side of the centerline.

    A point exactly on the centerline belongs to neither side and breaks the run.
    """
    cl = limits.centerline
    hits = []
    above = below = 0
    for i, x in enumerate(values):
        above = above + 1 if x > cl else 0
        below = below + 1 if x < cl else 0
        if above >= n or below >= n:
            hits.append(i)
    return hits


def rule_trend(values: Sequence[float], n: int = TREND_LENGTH) -> list[int]:
    """Rule 3: n points in a row steadily increasing or steadily decreasing.

    Monotonicity is strict — an equal consecutive value breaks the trend.
    """
    hits = []
    rising = falling = 1  # length of the monotonic run ending at the current point
    for i in range(1, len(values)):
        rising = rising + 1 if values[i] > values[i - 1] else 1
        falling = falling + 1 if values[i] < values[i - 1] else 1
        if rising >= n or falling >= n:
            hits.append(i)
    return hits


def rule_two_of_three_2sigma(values: Sequence[float], limits: ControlLimits) -> list[int]:
    """Rule 4: 2 of 3 consecutive points beyond 2 sigma on the same side."""
    upper, lower = limits.upper(2), limits.lower(2)
    hits = []
    for i in range(2, len(values)):
        window = values[i - 2 : i + 1]
        if sum(1 for x in window if x > upper) >= 2:
            hits.append(i)
        elif sum(1 for x in window if x < lower) >= 2:
            hits.append(i)
    return hits


def evaluate(values: Sequence[float], limits: ControlLimits) -> list[Violation]:
    """Run every rule and return labeled violations, ordered by index then rule."""
    found = [
        ("beyond_3sigma", rule_beyond_3sigma(values, limits)),
        ("run_one_side", rule_run_one_side(values, limits)),
        ("trend", rule_trend(values)),
        ("two_of_three_2sigma", rule_two_of_three_2sigma(values, limits)),
    ]
    violations = [Violation(rule=name, index=i) for name, indices in found for i in indices]
    return sorted(violations, key=lambda v: (v.index, v.rule))
