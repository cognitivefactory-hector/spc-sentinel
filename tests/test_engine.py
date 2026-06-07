"""Tests for the streaming SPC engine (generator -> limits -> rules + forecast -> alerts).

A deliberate design choice tested here: control limits are computed once from the
in-control warm-up window and then FROZEN. Rolling limits would chase a slow drift and
never breach — the opposite of what this tool is for. So the tests assert limits do not
move once set. A low-noise single signal keeps the assertions deterministic.
"""

import pytest

from sentinel.engine import Engine
from sentinel.sim.generator import SignalSpec

QUIET = SignalSpec("x", "u", 10.0, 0.2)


def make_engine(**kwargs):
    kwargs.setdefault("signals", [QUIET])
    kwargs.setdefault("warmup", 12)
    return Engine(seed=0, **kwargs)


def warm(engine):
    """Advance through the warm-up so limits are established."""
    payload = None
    for _ in range(12):
        payload = engine.step()
    return payload


def test_no_limits_or_alerts_during_warmup():
    engine = make_engine()
    for _ in range(11):
        payload = engine.step()
        assert payload["limits"] == {}
        assert payload["alerts"] == []
    assert payload["warmup_remaining"] == 1


def test_limits_established_after_warmup():
    engine = make_engine()
    payload = warm(engine)
    limits = payload["limits"]["x"]
    assert limits["lcl"] < limits["centerline"] < limits["ucl"]
    assert payload["warmup_remaining"] == 0


def test_limits_are_frozen_and_do_not_chase_drift():
    engine = make_engine()
    before = warm(engine)["limits"]["x"]
    engine.inject("x", kind="step", magnitude=5.0, duration=100)
    for _ in range(20):
        after = engine.step()["limits"]["x"]
    assert after == before


def test_inject_changes_the_stream():
    engine = make_engine()
    warm(engine)
    engine.inject("x", kind="step", magnitude=5.0, duration=50)
    value = engine.step()["samples"]["x"]
    assert value == pytest.approx(15.0, abs=1.0)


def test_injected_spike_fires_a_beyond_3sigma_alarm():
    engine = make_engine()
    warm(engine)
    engine.inject("x", kind="spike", magnitude=5.0)
    alerts = engine.step()["alerts"]
    assert any(a["rule"] == "beyond_3sigma" and a["severity"] == "alarm" for a in alerts)


def test_injected_drift_produces_a_forecast_alert():
    engine = make_engine()
    warm(engine)
    # Gentle drift relative to the control band, so it is detectable for many
    # samples before it actually breaches the LCL.
    engine.inject("x", kind="drift", magnitude=-5.0, duration=300)
    seen_forecast = False
    for _ in range(60):
        if any(a["kind"] == "forecast" for a in engine.step()["alerts"]):
            seen_forecast = True
            break
    assert seen_forecast


def test_reset_restarts_warmup_and_stream():
    engine = make_engine()
    warm(engine)
    engine.step()
    engine.reset()
    payload = engine.step()
    assert payload["t"] == 1
    assert payload["limits"] == {}


def test_config_reports_signals_and_sample_rate():
    engine = make_engine(sample_rate_hz=2.0)
    config = engine.config()
    assert config["sample_rate_hz"] == 2.0
    assert any(s["name"] == "x" and s["unit"] == "u" for s in config["signals"])
