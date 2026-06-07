"""Tests for the M4 backend wiring: REST control endpoints and the WebSocket stream.

The pure pipeline is covered in test_engine.py; here we verify the framework layer —
that the REST endpoints drive the shared Engine and that the WebSocket actually streams
payloads and reflects an injection (the M4 acceptance: a live stream that POST /inject
changes within seconds).
"""

import asyncio
import json

from channels.testing import WebsocketCommunicator
from django.test import Client

from config.asgi import application
from sentinel import consumers, runtime
from sentinel.engine import Engine


def test_config_endpoint_reports_signals():
    body = Client().get("/api/config").json()
    assert body["sample_rate_hz"]
    assert any(s["name"] == "concentration" for s in body["signals"])


def test_inject_endpoint_accepts_valid_payload():
    response = Client().post(
        "/api/inject",
        data=json.dumps({"signal": "concentration", "kind": "spike", "magnitude": 5}),
        content_type="application/json",
    )
    assert response.status_code == 200
    assert response.json() == {"ok": True}


def test_inject_endpoint_rejects_unknown_signal():
    response = Client().post(
        "/api/inject",
        data=json.dumps({"signal": "bogus", "kind": "spike", "magnitude": 5}),
        content_type="application/json",
    )
    assert response.status_code == 400


def test_reset_endpoint_requires_post():
    assert Client().get("/api/reset").status_code == 405
    assert Client().post("/api/reset").status_code == 200


def test_websocket_streams_and_reflects_injection():
    async def scenario():
        # Fast engine so the producer emits quickly; reset the global producer task.
        runtime._engine = Engine(seed=0, sample_rate_hz=50.0, warmup=2)
        consumers._producer_task = None

        communicator = WebsocketCommunicator(application, "/ws/telemetry")
        connected, _ = await communicator.connect()
        assert connected

        # First message is the config handshake.
        hello = await communicator.receive_json_from(timeout=2)
        assert hello["type"] == "config"

        # Then a telemetry payload with the expected shape.
        payload = await communicator.receive_json_from(timeout=2)
        assert {"t", "samples", "limits", "alerts"} <= set(payload)

        # Inject on the shared engine (what POST /inject does) and watch it appear.
        runtime.get_engine().inject("concentration", "spike", 50.0)
        seen_spike = False
        for _ in range(20):
            p = await communicator.receive_json_from(timeout=2)
            if p.get("samples", {}).get("concentration", 0) > 60:
                seen_spike = True
                break
        assert seen_spike

        await communicator.disconnect()

    asyncio.run(scenario())
