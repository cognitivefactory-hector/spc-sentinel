"""Tests for the plain-English alert builder.

The whole point of the project is an alert an operator will act on at 2 a.m.
(DECISIONS.md), so alerts must name the variable, say what's happening in plain
English, and — for forecasts — give a likely cause and a recommended action
(SPEC.md §4.2 #4). These tests pin that wording and the rule→severity mapping.
"""

from sentinel.alerts import forecast_alert, rule_alert
from sentinel.sim.generator import SignalSpec
from sentinel.spc.forecast import Forecast

CONCENTRATION = SignalSpec("concentration", "g/L", 25.0, 0.3)


def test_beyond_3sigma_is_an_alarm():
    alert = rule_alert(CONCENTRATION, "beyond_3sigma", 30.0)
    assert alert.severity == "alarm"
    assert alert.kind == "rule"
    assert alert.rule == "beyond_3sigma"


def test_other_rules_are_warnings():
    assert rule_alert(CONCENTRATION, "trend", 26.0).severity == "warning"


def test_rule_alert_names_signal_and_value_in_plain_english():
    msg = rule_alert(CONCENTRATION, "beyond_3sigma", 30.0).message
    assert "Concentration" in msg
    assert "30.0" in msg
    assert "g/L" in msg
    # Plain English, not a bare z-score.
    assert "3σ" in msg or "control limit" in msg


def _downward_forecast():
    # ~22 minutes to breach (1320 s) heading down toward 18 g/L.
    return Forecast(
        slope=-0.05,
        level=20.0,
        direction="down",
        target_limit=18.0,
        samples_to_breach=1320.0,
        seconds_to_breach=1320.0,
    )


def test_forecast_alert_reads_like_the_spec_example():
    alert = forecast_alert(CONCENTRATION, _downward_forecast())
    assert alert is not None
    assert alert.kind == "forecast"
    assert alert.severity == "warning"
    msg = alert.message
    assert "fall below 18.0 g/L" in msg
    assert "~22 min" in msg
    assert "Likely cause" in msg
    assert "Recommend" in msg


def test_forecast_alert_upward_says_rise_above():
    up = Forecast(
        slope=0.05,
        level=34.0,
        direction="up",
        target_limit=36.0,
        samples_to_breach=120.0,
        seconds_to_breach=120.0,
    )
    msg = forecast_alert(SignalSpec("temperature", "°C", 35.0, 0.2), up).message
    assert "rise above 36.0 °C" in msg


def test_forecast_alert_is_none_when_no_breach_predicted():
    flat = Forecast(
        slope=0.0,
        level=25.0,
        direction="flat",
        target_limit=None,
        samples_to_breach=None,
        seconds_to_breach=None,
    )
    assert forecast_alert(CONCENTRATION, flat) is None


def test_unknown_signal_still_gets_generic_cause_and_recommendation():
    spec = SignalSpec("mystery", "u", 1.0, 0.1)
    alert = forecast_alert(spec, _downward_forecast())
    assert "Likely cause" in alert.message
    assert "Recommend" in alert.message


def test_alert_is_json_serializable():
    alert = rule_alert(CONCENTRATION, "beyond_3sigma", 30.0)
    d = alert.as_dict()
    assert d["signal"] == "concentration"
    assert d["severity"] == "alarm"
    assert d["kind"] == "rule"
