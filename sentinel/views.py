from django.shortcuts import render


def index(request):
    """M0 placeholder dashboard. The live charts, alert log, and inject controls
    are built in M5 — see PLAN.md."""
    return render(request, "index.html")
