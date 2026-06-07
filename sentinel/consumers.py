"""Channels WebSocket consumer + the single server-side producer loop.

One producer task steps the shared Engine at the configured rate and broadcasts each
payload to the "telemetry" group; every connected client forwards group messages to its
socket. Starting the producer lazily on first connect avoids needing an app-startup hook.
"""

import asyncio

from channels.generic.websocket import AsyncJsonWebsocketConsumer

from sentinel.runtime import get_engine

GROUP = "telemetry"

_producer_lock = asyncio.Lock()
_producer_task: asyncio.Task | None = None


async def _ensure_producer(channel_layer) -> None:
    global _producer_task
    async with _producer_lock:
        if _producer_task is None or _producer_task.done():
            _producer_task = asyncio.create_task(_produce(channel_layer))


async def _produce(channel_layer) -> None:
    engine = get_engine()
    interval = 1.0 / engine.sample_rate_hz
    while True:
        payload = engine.step()
        await channel_layer.group_send(GROUP, {"type": "telemetry.message", "data": payload})
        await asyncio.sleep(interval)


class TelemetryConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add(GROUP, self.channel_name)
        await self.accept()
        await self.send_json({"type": "config", "config": get_engine().config()})
        await _ensure_producer(self.channel_layer)

    async def disconnect(self, code):
        await self.channel_layer.group_discard(GROUP, self.channel_name)

    async def telemetry_message(self, event):
        await self.send_json(event["data"])
