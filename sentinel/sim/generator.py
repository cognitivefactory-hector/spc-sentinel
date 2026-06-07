"""Seeded synthetic telemetry generator for wet-process signals.

Each sample = baseline + diurnal term + Gaussian noise + active injection offsets.
A fixed seed makes the whole stream reproducible (SPEC.md §5), which is what lets a
demo be replayed identically. Noise is drawn for every signal on every step so the
RNG sequence — and therefore reproducibility — is independent of which disturbances
are injected.

Injection model (offsets added on top of the quiet signal):
  - spike: a one-sample bump of `magnitude`.
  - step:  a transient shift of `magnitude` held for `duration` samples, then heals.
  - drift: a linear ramp reaching `magnitude` over `duration` samples
           (slope = magnitude / duration per sample), then HELD — a real drift
           persists until corrected. Call reset() to clear all injections.

NO employer data — baselines are deliberately round, obviously synthetic numbers.
"""

import math
from dataclasses import dataclass, field

import numpy as np

INJECTION_KINDS = ("spike", "step", "drift")


@dataclass(frozen=True)
class SignalSpec:
    name: str
    unit: str
    baseline: float
    noise_sigma: float
    diurnal_amplitude: float = 0.0
    diurnal_period: int = 0  # samples per cycle; 0 disables the diurnal term

    def quiet_value(self, t: int) -> float:
        """Baseline + diurnal term at sample index t (no noise, no injections)."""
        if self.diurnal_period:
            return self.baseline + self.diurnal_amplitude * math.sin(
                2 * math.pi * t / self.diurnal_period
            )
        return self.baseline


# Illustrative, generic baselines (SPEC.md §5) — not tied to any real process.
DEFAULT_SIGNALS = (
    SignalSpec("concentration", "g/L", 25.0, 0.3, diurnal_amplitude=0.5, diurnal_period=3600),
    SignalSpec("temperature", "°C", 35.0, 0.2, diurnal_amplitude=0.8, diurnal_period=3600),
    SignalSpec("thickness", "µm", 12.0, 0.15, diurnal_amplitude=0.3, diurnal_period=3600),
)


@dataclass
class Injection:
    signal: str
    kind: str
    magnitude: float
    duration: int
    start_t: int

    def offset_at(self, t: int) -> float:
        elapsed = t - self.start_t
        if elapsed < 0:
            return 0.0
        if self.kind == "spike":
            return self.magnitude if elapsed == 0 else 0.0
        if self.kind == "step":
            # A transient shift: held for `duration` samples, then it self-heals.
            return self.magnitude if elapsed < self.duration else 0.0
        # drift: ramp to `magnitude` over `duration`, then HOLD — a real process
        # drift persists until someone corrects it (or the stream is reset).
        if elapsed >= self.duration:
            return self.magnitude
        return self.magnitude * elapsed / self.duration


@dataclass
class Generator:
    seed: int = 0
    signals: tuple[SignalSpec, ...] = DEFAULT_SIGNALS
    sample_rate_hz: float = 1.0
    _rng: np.random.Generator = field(init=False)
    _t: int = field(init=False, default=0)
    _injections: list[Injection] = field(init=False, default_factory=list)

    def __post_init__(self):
        self.signals = tuple(self.signals)
        self.reset()

    def reset(self) -> None:
        """Re-seed the RNG and clear injections so the stream replays identically."""
        self._rng = np.random.default_rng(self.seed)
        self._t = 0
        self._injections = []

    def inject(self, signal: str, kind: str, magnitude: float, duration: int = 1) -> None:
        if signal not in {s.name for s in self.signals}:
            raise ValueError(f"unknown signal {signal!r}")
        if kind not in INJECTION_KINDS:
            raise ValueError(f"unknown injection kind {kind!r}; choose from {INJECTION_KINDS}")
        if duration < 1:
            raise ValueError("duration must be at least 1 sample")
        self._injections.append(
            Injection(
                signal=signal, kind=kind, magnitude=magnitude, duration=duration, start_t=self._t
            )
        )

    def step(self) -> dict[str, float]:
        """Advance one sample and return {signal_name: value}."""
        values = {}
        for spec in self.signals:
            noise = float(self._rng.normal(0.0, spec.noise_sigma))
            offset = sum(
                inj.offset_at(self._t) for inj in self._injections if inj.signal == spec.name
            )
            values[spec.name] = spec.quiet_value(self._t) + noise + offset
        self._t += 1
        return values


if __name__ == "__main__":
    # Smoke demo: `python -m sentinel.sim.generator` prints a reproducible stream.
    gen = Generator(seed=0)
    for i in range(10):
        sample = {k: round(v, 3) for k, v in gen.step().items()}
        print(f"{i:3d}  {sample}")
