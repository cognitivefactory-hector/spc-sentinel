"""Acceptance test for M3: the forecaster returns sane estimates on an injected drift.

Wires together the three pure modules built so far — the seeded generator (M2),
control-limit computation (M1), and the forecaster (M3) — on a realistic in-control
warm-up followed by an injected downward drift. Deterministic via a fixed seed.
"""

from sentinel.sim.generator import Generator
from sentinel.spc.forecast import forecast
from sentinel.spc.limits import control_limits


def _concentration_stream(gen, n):
    return [gen.step()["concentration"] for _ in range(n)]


def test_forecaster_tracks_an_injected_downward_drift():
    gen = Generator(seed=0)

    # In-control warm-up → control limits for the concentration signal.
    warmup = _concentration_stream(gen, 60)
    limits = control_limits(warmup)
    assert limits.lcl < limits.centerline < limits.ucl

    # Inject a downward drift and keep streaming.
    gen.inject("concentration", kind="drift", magnitude=-6.0, duration=120)
    series = list(warmup)

    series += _concentration_stream(gen, 15)
    early = forecast(series, limits, window=20)

    series += _concentration_stream(gen, 20)
    late = forecast(series, limits, window=20)

    # Sane: heading down toward the LCL with a finite, positive, shrinking horizon.
    assert early.direction == "down"
    assert early.target_limit == limits.lcl
    assert early.samples_to_breach is not None and early.samples_to_breach > 0
    assert late.samples_to_breach is not None
    assert late.samples_to_breach < early.samples_to_breach
