"""Process-wide singleton Engine shared by the WebSocket producer and REST views.

The in-memory channel layer means a single process serves the demo, so one shared
Engine is the simplest correct design: the producer steps it, REST `inject`/`reset`
mutate the same instance, and every connected client sees the result.

Tunable via env (handy for deploy and for fast local/CI verification):
  SPC_SAMPLE_RATE_HZ  samples per second (default 1.0)
  SPC_WARMUP          in-control samples before limits/alerts (default 20)
"""

import os

from sentinel.engine import Engine

_engine: Engine | None = None


def get_engine() -> Engine:
    global _engine
    if _engine is None:
        _engine = Engine(
            warmup=int(os.environ.get("SPC_WARMUP", "20")),
            sample_rate_hz=float(os.environ.get("SPC_SAMPLE_RATE_HZ", "1.0")),
        )
    return _engine
