"""Testes de configure_structlog (Story 1.5b)."""

from __future__ import annotations

import structlog
from django.test import TestCase, override_settings

from apps.core.logging import _add_trace_id, configure_structlog


class ConfigureStructlogTests(TestCase):
    @override_settings(DEBUG=True)
    def test_configure_dev_does_not_crash(self) -> None:
        configure_structlog()
        logger = structlog.get_logger("test")
        logger.info("hello", foo=1)

    @override_settings(DEBUG=False)
    def test_configure_prod_does_not_crash(self) -> None:
        configure_structlog()
        logger = structlog.get_logger("test")
        logger.info("hello", foo=1)

    def test_add_trace_id_processor_injects_when_present(self) -> None:
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(trace_id="abc-123")
        event: dict = {"event": "x"}
        result = _add_trace_id(None, "info", event)
        self.assertEqual(result["trace_id"], "abc-123")
        structlog.contextvars.clear_contextvars()

    def test_add_trace_id_processor_no_op_when_missing(self) -> None:
        structlog.contextvars.clear_contextvars()
        event: dict = {"event": "x"}
        result = _add_trace_id(None, "info", event)
        self.assertNotIn("trace_id", result)

    def test_add_trace_id_preserves_existing(self) -> None:
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(trace_id="ctx")
        event: dict = {"event": "x", "trace_id": "explicit"}
        result = _add_trace_id(None, "info", event)
        self.assertEqual(result["trace_id"], "explicit")
        structlog.contextvars.clear_contextvars()
