"""Turn a rule hit or a drift forecast into a plain-English, actionable alert.

An operator won't act on a z-score at 2 a.m. (DECISIONS.md), so every alert names
the variable, says what is happening in plain language, and — for a forecast —
states a likely cause and a recommended action (SPEC.md §4.2 #4). Cause/recommendation
are deliberately generic, illustrative guidance: no real process recipes.
"""

from dataclasses import asdict, dataclass

from sentinel.sim.generator import SignalSpec
from sentinel.spc.forecast import Forecast

# Human phrasing for each rule key emitted by spc.rules.evaluate().
RULE_PHRASES = {
    "beyond_3sigma": "a point beyond the 3σ control limit",
    "run_one_side": "a long run on one side of the centerline",
    "trend": "a steady trend",
    "two_of_three_2sigma": "2 of 3 points beyond 2σ",
}

# Generic, illustrative cause/recommendation per signal (cause, recommendation).
SIGNAL_GUIDANCE = {
    "concentration": ("drag-out depletion", "a chemistry addition"),
    "temperature": ("heater or chiller drift", "checking the temperature controller"),
    "thickness": ("bath aging or current drift", "verifying current density"),
}
GENERIC_GUIDANCE = ("a process disturbance", "an operator check")


@dataclass(frozen=True)
class Alert:
    signal: str
    severity: str  # "alarm" | "warning"
    message: str
    kind: str = "rule"  # "rule" | "forecast"
    rule: str | None = None

    def as_dict(self) -> dict:
        return asdict(self)


def _label(spec: SignalSpec) -> str:
    return spec.name.capitalize()


def rule_alert(spec: SignalSpec, rule_name: str, value: float) -> Alert:
    """Build an alert for a fired Western Electric / Nelson rule."""
    phrase = RULE_PHRASES.get(rule_name, "a control-rule violation")
    severity = "alarm" if rule_name == "beyond_3sigma" else "warning"
    message = f"{_label(spec)}: {phrase} (value {value:.1f} {spec.unit})."
    return Alert(signal=spec.name, severity=severity, message=message, kind="rule", rule=rule_name)


def forecast_alert(spec: SignalSpec, fc: Forecast) -> Alert | None:
    """Build a time-to-breach warning, or None if no breach is predicted."""
    if fc.seconds_to_breach is None or fc.target_limit is None:
        return None

    verb = "rise above" if fc.direction == "up" else "fall below"
    minutes = max(1, round(fc.seconds_to_breach / 60))
    cause, recommendation = SIGNAL_GUIDANCE.get(spec.name, GENERIC_GUIDANCE)
    message = (
        f"{_label(spec)} trending {fc.direction} — projected to {verb} "
        f"{fc.target_limit:.1f} {spec.unit} in ~{minutes} min. "
        f"Likely cause: {cause}. Recommend {recommendation}."
    )
    return Alert(signal=spec.name, severity="warning", message=message, kind="forecast")
