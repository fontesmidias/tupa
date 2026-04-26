"""Testes do RequestContextMiddleware (Story 3.2)."""

from __future__ import annotations

from unittest.mock import MagicMock

from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from apps.core.middleware import RequestContextMiddleware
from apps.core.request_context import (
    clear_request_context,
    get_request_context,
)


class RequestContextMiddlewareTests(TestCase):
    def setUp(self) -> None:
        self.rf = RequestFactory()
        clear_request_context()

    def tearDown(self) -> None:
        clear_request_context()

    def _mw(self, captured: dict) -> RequestContextMiddleware:
        def inner(_req):
            captured["during"] = get_request_context()
            return HttpResponse("ok")

        return RequestContextMiddleware(inner)

    def test_popula_context_com_user_autenticado(self):
        user = MagicMock(pk="u-1", is_authenticated=True)
        captured: dict = {}
        mw = self._mw(captured)
        req = self.rf.get("/x", HTTP_USER_AGENT="ua/test", REMOTE_ADDR="4.4.4.4")
        req.user = user
        req.trace_id = "t-1"
        mw(req)
        ctx = captured["during"]
        assert ctx is not None
        assert ctx.user_id == "u-1"
        assert ctx.ip == "4.4.4.4"
        assert ctx.user_agent == "ua/test"
        assert ctx.trace_id == "t-1"
        # reset depois
        assert get_request_context() is None

    def test_usuario_anonimo_user_id_none(self):
        captured: dict = {}
        mw = self._mw(captured)
        req = self.rf.get("/x")
        req.user = AnonymousUser()
        mw(req)
        ctx = captured["during"]
        assert ctx is not None
        assert ctx.user_id is None

    def test_x_forwarded_for_tem_precedencia(self):
        captured: dict = {}
        mw = self._mw(captured)
        req = self.rf.get(
            "/x",
            HTTP_X_FORWARDED_FOR="1.2.3.4, 5.6.7.8",
            REMOTE_ADDR="9.9.9.9",
        )
        req.user = AnonymousUser()
        mw(req)
        assert captured["during"].ip == "1.2.3.4"

    def test_context_reset_mesmo_com_excecao(self):
        def inner(_req):
            raise RuntimeError("boom")

        mw = RequestContextMiddleware(inner)
        req = self.rf.get("/x")
        req.user = AnonymousUser()
        try:
            mw(req)
        except RuntimeError:
            pass
        assert get_request_context() is None
