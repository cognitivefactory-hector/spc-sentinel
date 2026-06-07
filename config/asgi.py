"""ASGI entrypoint with HTTP + WebSocket routing.

The WebSocket route streams telemetry (samples, limits, alerts). No auth middleware:
the demo has no accounts (SPEC.md §4.4).
"""

import os

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from django.urls import path

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

django_asgi_app = get_asgi_application()

# Imported after Django is set up so app models/settings are ready.
from sentinel.consumers import TelemetryConsumer  # noqa: E402

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": URLRouter(
            [
                path("ws/telemetry", TelemetryConsumer.as_asgi()),
            ]
        ),
    }
)
