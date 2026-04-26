"""Settings dev — ADR-002: porta 3005."""

from .base import *  # noqa: F401,F403

DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0"]

# Story 2.2: backend de email console em dev.
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
