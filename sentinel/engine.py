"""Streaming SPC engine: the framework-free pipeline behind the live demo.

Each step pulls one sample from the seeded generator, maintains a rolling history per
signal, and — once an in-control warm-up has established control limits — runs the
Western Electric / Nelson rules and the drift forecaster, emitting plain-English alerts.

Design choice (see DECISIONS.md): control limits are computed once from the warm-up
window and then FROZEN. A rolling-window recompute would slowly absorb a real drift
into the limits and never breach — defeating the purpose. The cost is that limits don't
adapt to a genuine new normal; for a demo that trade is clearly right.
"""

from collections import defaultdict

from sentinel.alerts import forecast_alert, rule_alert
from sentinel.sim.generator import DEFAULT_SIGNALS, Generator
from sentinel.spc.forecast import forecast
from sentinel.spc.limits import ControlLimits, control_limits
from sentinel.spc.rules import evaluate


class Engine:
    def __init__(
        self,
        seed: int = 0,
        signals=DEFAULT_SIGNALS,
        warmup: int = 60,
        history: int = 200,
        sample_rate_hz: float = 1.0,
        breach_horizon_s: float = 1800.0,
    ):
        self._seed = seed
        self._signals = tuple(signals)
        self.warmup = warmup
        self.history_len = history
        self.sample_rate_hz = sample_rate_hz
        self.breach_horizon_s = breach_horizon_s
        self.reset()

    def reset(self) -> None:
        self._generator = Generator(
            seed=self._seed, signals=self._signals, sample_rate_hz=self.sample_rate_hz
        )
        self._history: dict[str, list[float]] = defaultdict(list)
        self._limits: dict[str, ControlLimits] = {}
        self._t = 0

    def inject(self, signal: str, kind: str, magnitude: float, duration: int = 1) -> None:
        self._generator.inject(signal, kind, magnitude, duration)

    def config(self) -> dict:
        return {
            "sample_rate_hz": self.sample_rate_hz,
            "warmup": self.warmup,
            "breach_horizon_s": self.breach_horizon_s,
            "signals": [
                {"name": s.name, "unit": s.unit, "baseline": s.baseline} for s in self._signals
            ],
        }

    def step(self) -> dict:
        sample = self._generator.step()
        for name, value in sample.items():
            history = self._history[name]
            history.append(value)
            if len(history) > self.history_len:
                del history[0]

        self._freeze_limits_after_warmup()
        alerts = self._evaluate(sample) if self._limits else []
        self._t += 1

        return {
            "t": self._t,
            "samples": sample,
            "limits": self._limits_payload(),
            "alerts": [a.as_dict() for a in alerts],
            "warmup_remaining": max(0, self.warmup - len(next(iter(self._history.values())))),
        }

    # --- internals -------------------------------------------------------

    def _freeze_limits_after_warmup(self) -> None:
        if self._limits:
            return
        if all(len(h) >= self.warmup for h in self._history.values()):
            self._limits = {
                name: control_limits(history[: self.warmup])
                for name, history in self._history.items()
            }

    def _evaluate(self, sample: dict) -> list:
        alerts = []
        for spec in self._signals:
            history = self._history[spec.name]
            limits = self._limits[spec.name]

            # A rule "fires now" only if its triggering index is the latest sample.
            current = len(history) - 1
            for violation in evaluate(history, limits):
                if violation.index == current:
                    alerts.append(rule_alert(spec, violation.rule, sample[spec.name]))

            fc = forecast(history, limits, sample_rate_hz=self.sample_rate_hz)
            if (
                fc.seconds_to_breach is not None
                and 0 < fc.seconds_to_breach <= self.breach_horizon_s
            ):
                alert = forecast_alert(spec, fc)
                if alert is not None:
                    alerts.append(alert)
        return alerts

    def _limits_payload(self) -> dict:
        payload = {}
        for spec in self._signals:
            limits = self._limits.get(spec.name)
            if limits is None:
                continue
            payload[spec.name] = {
                "centerline": limits.centerline,
                "sigma": limits.sigma,
                "ucl": limits.ucl,
                "lcl": limits.lcl,
                "unit": spec.unit,
            }
        return payload
