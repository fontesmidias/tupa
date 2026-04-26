"""Configuração structlog: dev=Console colorido, prod=JSON."""

from __future__ import annotations

from typing import Any

import structlog
from django.conf import settings


def _add_trace_id(logger: Any, method_name: str, event_dict: dict[str, Any]) -> dict[str, Any]:
    """Injeta trace_id do context se disponível."""
    ctx = structlog.contextvars.get_contextvars()
    trace_id = ctx.get("trace_id")
    if trace_id and "trace_id" not in event_dict:
        event_dict["trace_id"] = trace_id
    return event_dict


def configure_structlog() -> None:
    """Configura structlog globalmente."""
    debug = getattr(settings, "DEBUG", False)
    renderer: Any = (
        structlog.dev.ConsoleRenderer(colors=True) if debug else structlog.processors.JSONRenderer()
    )
    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        _add_trace_id,
        renderer,
    ]
    structlog.configure(
        processors=processors,
        context_class=dict,
        cache_logger_on_first_use=False,
    )
