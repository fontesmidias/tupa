"""Testes dos helpers BaseTestCase + AuthenticatedClientMixin (Story 1.5b)."""

from __future__ import annotations

import uuid

from django.http import HttpResponse, JsonResponse

from apps.core.testing import AuthenticatedClientMixin, BaseTestCase


class BaseTestCaseHelpersTests(BaseTestCase):
    def test_assert_domain_error_ok(self) -> None:
        resp = JsonResponse({"code": "X", "message": "m", "trace_id": "t"}, status=400)
        self.assertDomainError(resp, "X")

    def test_assert_domain_error_fails_on_wrong_code(self) -> None:
        resp = JsonResponse({"code": "Y", "message": "m"}, status=400)
        with self.assertRaises(AssertionError):
            self.assertDomainError(resp, "X")

    def test_assert_trace_id_ok(self) -> None:
        resp = HttpResponse("ok")
        resp["X-Trace-Id"] = str(uuid.uuid4())
        self.assertTraceId(resp)

    def test_assert_trace_id_missing(self) -> None:
        resp = HttpResponse("ok")
        with self.assertRaises(AssertionError):
            self.assertTraceId(resp)

    def test_assert_trace_id_invalid(self) -> None:
        resp = HttpResponse("ok")
        resp["X-Trace-Id"] = "not-a-uuid"
        with self.assertRaises(AssertionError):
            self.assertTraceId(resp)


class AuthenticatedClientMixinTests(AuthenticatedClientMixin, BaseTestCase):
    def test_authenticated_client_creates_user_and_logs_in(self) -> None:
        client = self.authenticated_client
        self.assertIsNotNone(self._auth_user)
        self.assertIsNotNone(client)
        # Reacesso retorna mesmo client (cache).
        self.assertIs(self.authenticated_client, client)
