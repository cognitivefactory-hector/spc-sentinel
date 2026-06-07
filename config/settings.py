"""Django settings for SPC Sentinel.

Deliberately minimal: no accounts, no DB-backed features (explicit non-goals in
SPEC.md §4.4), so the contrib auth/admin/sessions apps are omitted. State for the
demo lives in an in-memory rolling buffer, and Channels uses the in-memory channel
layer (single-process demo — see DECISIONS.md).
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY: a dev fallback only. Set DJANGO_SECRET_KEY in any deployed environment.
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-insecure-key-change-me")

DEBUG = os.environ.get("DJANGO_DEBUG", "0") == "1"

# Comma-separated env override, e.g. "spc.hector-garza.com". "*" is fine for the
# local demo; tighten in production via the env var.
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "*").split(",")
CSRF_TRUSTED_ORIGINS = [
    o for o in os.environ.get("DJANGO_CSRF_TRUSTED_ORIGINS", "").split(",") if o
]

# Behind Render/Cloudflare TLS termination: trust the forwarded-proto header so
# Django treats proxied requests as HTTPS (and the client uses wss for the socket).
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

INSTALLED_APPS = [
    "daphne",  # must precede staticfiles so its runserver override wins
    "channels",
    "django.contrib.staticfiles",
    "sentinel",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {"context_processors": []},
    },
]

# Channels (ASGI). WSGI_APPLICATION is intentionally unset — this app is ASGI-only.
ASGI_APPLICATION = "config.asgi.application"
CHANNEL_LAYERS = {
    "default": {"BACKEND": "channels.layers.InMemoryChannelLayer"},
}

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
