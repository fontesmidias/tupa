"""Configuracao Dramatiq (ADR-005, ADR-011). Broker Redis em DB 0, fila unica 'default' no MVP."""

from __future__ import annotations

import os

import django
import dramatiq
from dramatiq.brokers.redis import RedisBroker

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")
django.setup()

from django.conf import settings  # noqa: E402

redis_broker = RedisBroker(url=settings.DRAMATIQ_BROKER_URL)
dramatiq.set_broker(redis_broker)
