"""Testes dos middlewares (Story 1.5b)."""

from __future__ import annotations

import json
import uuid
from unittest.mock import MagicMock

from django.contrib.auth.models import AnonymousUser, User
from django.http import HttpResponse
from django.test import RequestFactory, TestCase, override_settings

from apps.core.exceptions import (
    ConsentRequired,
    DomainValidationError,
    DuplicateDetected,
    ExtractionFailed,
    ProviderUnavailable,
)
from apps.core.base_services import DomainError
from apps.core.middleware import (
    AuthRequiredMiddleware,
    DomainExceptionMiddleware,
    TraceIdMiddleware,
)


class TraceIdMiddlewareTests(TestCase):
    def setUp(self) -> None:
        self.rf = RequestFactory()

    def test_generates_new_trace_id_when_absent(self) -> None:
        inner = MagicMock(return_value=HttpResponse("ok"))
        mw = TraceIdMiddleware(inner)
        req = self.rf.get("/x")
        resp = mw(req)
        assert hasattr(req, "trace_id")
        uuid.UUID(req.trace_id)  # valid
        self.assertEqual(resp["X-Trace-Id"], req.trace_id)

    def test_reuses_valid_incoming_trace_id(self) -> None:
        tid = str(uuid.uuid4())
        inner = MagicMock(return_value=HttpResponse("ok"))
        mw = TraceIdMiddleware(inner)
        req = self.rf.get("/x", HTTP_X_TRACE_ID=tid)
        resp = mw(req)
        self.assertEqual(req.trace_id, tid)
        self.assertEqual(resp["X-Trace-Id"], tid)

    def test_rejects_invalid_incoming_trace_id(self) -> None:
        inner = MagicMock(return_value=HttpResponse("ok"))
        mw = TraceIdMiddleware(inner)
        req = self.rf.get("/x", HTTP_X_TRACE_ID="not-a-uuid")
        resp = mw(req)
        self.assertNotEqual(req.trace_id, "not-a-uuid")
        uuid.UUID(resp["X-Trace-Id"])


class DomainExceptionMiddlewareTests(TestCase):
    def setUp(self) -> None:
        self.rf = RequestFactory()
        self.mw = DomainExceptionMiddleware(MagicMock(return_value=HttpResponse("ok")))

    def _exc_response(self, exc: Exception) -> HttpResponse | None:
        req = self.rf.get("/x")
        req.trace_id = str(uuid.uuid4())  # type: ignore[attr-defined]
        return self.mw.process_exception(req, exc)

    def test_validation_error_400(self) -> None:
        resp = self._exc_response(DomainValidationError("bad"))
        assert resp is not None
        self.assertEqual(resp.status_code, 400)
        body = json.loads(resp.content)
        self.assertEqual(body["code"], "DOMAIN_VALIDATION")
        self.assertEqual(body["message"], "bad")
        self.assertIn("trace_id", body)

    def test_provider_unavailable_503(self) -> None:
        resp = self._exc_response(ProviderUnavailable("down"))
        assert resp is not None
        self.assertEqual(resp.status_code, 503)

    def test_extraction_failed_422(self) -> None:
        resp = self._exc_response(ExtractionFailed("x"))
        assert resp is not None
        self.assertEqual(resp.status_code, 422)

    def test_duplicate_409(self) -> None:
        resp = self._exc_response(DuplicateDetected("x"))
        assert resp is not None
        self.assertEqual(resp.status_code, 409)

    def test_consent_403(self) -> None:
        resp = self._exc_response(ConsentRequired("x"))
        assert resp is not None
        self.assertEqual(resp.status_code, 403)

    def test_generic_domain_error_500(self) -> None:
        resp = self._exc_response(DomainError("x"))
        assert resp is not None
        self.assertEqual(resp.status_code, 500)

    def test_non_domain_exception_passthrough(self) -> None:
        resp = self._exc_response(ValueError("not-domain"))
        self.assertIsNone(resp)

    def test_normal_flow_calls_inner(self) -> None:
        req = self.rf.get("/x")
        resp = self.mw(req)
        self.assertEqual(resp.status_code, 200)


class AuthRequiredMiddlewareTests(TestCase):
    def setUp(self) -> None:
        self.rf = RequestFactory()
        self.inner = MagicMock(return_value=HttpResponse("ok"))
        self.mw = AuthRequiredMiddleware(self.inner)

    def _req(self, path: str, user: object | None = None) -> object:
        req = self.rf.get(path)
        req.user = user if user is not None else AnonymousUser()  # type: ignore[attr-defined]
        return req

    def test_anon_on_protected_returns_401(self) -> None:
        resp = self.mw(self._req("/private/resource"))
        self.assertEqual(resp.status_code, 401)
        body = json.loads(resp.content)
        self.assertEqual(body["code"], "AUTH_REQUIRED")

    def test_anon_on_public_passes(self) -> None:
        resp = self.mw(self._req("/"))
        self.assertEqual(resp.status_code, 200)

    def test_anon_on_public_prefix_passes(self) -> None:
        resp = self.mw(self._req("/static/foo.css"))
        self.assertEqual(resp.status_code, 200)

    def test_authenticated_user_passes(self) -> None:
        # User real do Django tem is_anonymous=False por padrão.
        user = User(username="u")
        resp = self.mw(self._req("/private/x", user=user))
        self.assertEqual(resp.status_code, 200)

    @override_settings(PUBLIC_PATHS=["/open"])
    def test_respects_settings_override(self) -> None:
        resp = self.mw(self._req("/open"))
        self.assertEqual(resp.status_code, 200)
        resp2 = self.mw(self._req("/"))
        self.assertEqual(resp2.status_code, 401)
