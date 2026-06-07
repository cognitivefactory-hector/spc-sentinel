"""ASGI entrypoint.

HTTP-only for M0. The WebSocket protocol router (samples + alerts stream) is added
in M4 — see PLAN.md. When it lands, wrap a URLRouter under the "websocket" key here.
"""

import os

from channels.routing import ProtocolTypeRouter
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
    }
)
