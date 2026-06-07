"""Process-wide singleton Engine shared by the WebSocket producer and REST views.

The in-memory channel layer means a single process serves the demo, so one shared
Engine is the simplest correct design: the producer steps it, REST `inject`/`reset`
mutate the same instance, and every connected client sees the result.
"""

from sentinel.engine import Engine

# Snappier warm-up than the 60-sample default so a cold demo shows limits within ~30 s.
_WARMUP = 30

_engine: Engine | None = None


def get_engine() -> Engine:
    global _engine
    if _engine is None:
        _engine = Engine(warmup=_WARMUP, sample_rate_hz=1.0)
    return _engine
