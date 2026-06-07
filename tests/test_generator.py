"""Tests for the synthetic telemetry generator.

Reproducibility (a fixed seed → identical stream) is what makes the demo
trustworthy, so it is tested first. Behavioural tests of the injection model use a
"quiet" signal (no noise, no diurnal term) so the deterministic disturbance is
exactly checkable; injection magnitudes are documented in generator.py.
"""

import pytest

from sentinel.sim.generator import Generator, SignalSpec

# A noise-free, drift-free signal so injected disturbances are exact.
QUIET = SignalSpec(name="q", unit="x", baseline=10.0, noise_sigma=0.0)


def quiet_gen(**kwargs):
    return Generator(signals=[QUIET], **kwargs)


def stream(gen, n):
    return [gen.step()["q"] for _ in range(n)]


def test_default_generator_has_three_signals():
    values = Generator(seed=0).step()
    assert set(values) == {"concentration", "temperature", "thickness"}


def test_same_seed_is_reproducible():
    a = [Generator(seed=42).step() for _ in range(5)]
    b = [Generator(seed=42).step() for _ in range(5)]
    assert a == b


def test_different_seeds_diverge():
    a = Generator(seed=1).step()["concentration"]
    b = Generator(seed=2).step()["concentration"]
    assert a != b


def test_quiet_signal_sits_at_baseline():
    assert stream(quiet_gen(), 3) == [10.0, 10.0, 10.0]


def test_injected_drift_has_expected_slope():
    # drift magnitude is the TOTAL change reached over `duration` samples,
    # so slope per sample = magnitude / duration = 6 / 6 = 1.0.
    gen = quiet_gen()
    gen.inject("q", kind="drift", magnitude=6.0, duration=6)
    values = stream(gen, 6)
    diffs = [round(b - a, 9) for a, b in zip(values, values[1:], strict=False)]
    assert diffs == [1.0, 1.0, 1.0, 1.0, 1.0]


def test_injected_drift_holds_after_duration():
    # The ramp completes at `duration`, then the offset is held (drift persists).
    gen = quiet_gen()
    gen.inject("q", kind="drift", magnitude=6.0, duration=6)
    values = stream(gen, 9)
    assert values[5] == pytest.approx(15.0)  # end of ramp: 10 + 6*5/6
    assert values[6] == pytest.approx(16.0)  # held at baseline + magnitude
    assert values[8] == pytest.approx(16.0)


def test_injected_step_holds_then_expires():
    gen = quiet_gen()
    gen.inject("q", kind="step", magnitude=2.0, duration=3)
    assert stream(gen, 5) == [12.0, 12.0, 12.0, 10.0, 10.0]


def test_injected_spike_affects_single_sample():
    gen = quiet_gen()
    gen.inject("q", kind="spike", magnitude=5.0)
    assert stream(gen, 3) == [15.0, 10.0, 10.0]


def test_inject_rejects_unknown_signal():
    with pytest.raises(ValueError):
        quiet_gen().inject("nope", kind="drift", magnitude=1.0, duration=5)


def test_inject_rejects_unknown_kind():
    with pytest.raises(ValueError):
        quiet_gen().inject("q", kind="explode", magnitude=1.0, duration=5)


def test_reset_restores_initial_stream():
    gen = Generator(seed=7)
    first = [gen.step() for _ in range(4)]
    gen.reset()
    again = [gen.step() for _ in range(4)]
    assert first == again


def test_reset_clears_injections():
    gen = quiet_gen(seed=7)
    gen.inject("q", kind="step", magnitude=99.0, duration=100)
    gen.step()
    gen.reset()
    assert gen.step()["q"] == 10.0
