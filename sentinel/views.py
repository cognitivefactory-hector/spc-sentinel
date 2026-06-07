"""HTTP views: the dashboard page and the REST control endpoints.

The control endpoints (inject/reset/config) operate on the shared Engine singleton, so
they affect the live WebSocket stream. They are async so they run on the ASGI event loop
alongside the producer rather than in a worker thread. CSRF is exempted because this is
an account-free, synthetic-data demo (a non-goal to add auth — SPEC.md §4.4).
"""

import json

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from sentinel.runtime import get_engine


def index(request):
    """The dashboard. Live charts, alert log, and inject controls land in M5."""
    return render(request, "index.html")


@csrf_exempt
@require_http_methods(["POST"])
async def inject(request):
    try:
        data = json.loads(request.body or b"{}")
        get_engine().inject(
            signal=data["signal"],
            kind=data["kind"],
            magnitude=float(data["magnitude"]),
            duration=int(data.get("duration", 1)),
        )
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        return JsonResponse({"error": str(exc)}, status=400)
    return JsonResponse({"ok": True})


@csrf_exempt
@require_http_methods(["POST"])
async def reset(request):
    get_engine().reset()
    return JsonResponse({"ok": True})


async def config(request):
    return JsonResponse(get_engine().config())
