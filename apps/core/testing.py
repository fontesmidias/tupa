"""Helpers de teste — BaseTestCase + AuthenticatedClientMixin."""

from __future__ import annotations

import uuid
from typing import Any

from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import Client, TestCase


class BaseTestCase(TestCase):
    """TestCase com helpers de asserção para padrões do projeto."""

    def assertDomainError(self, response: HttpResponse, code: str) -> None:
        self.assertEqual(response["Content-Type"], "application/json")
        import json

        body = json.loads(response.content)
        self.assertEqual(body.get("code"), code, f"Esperado code={code}, veio={body}")

    def assertTraceId(self, response: HttpResponse) -> None:
        trace_id = response.get("X-Trace-Id")
        self.assertIsNotNone(trace_id, "Header X-Trace-Id ausente")
        try:
            uuid.UUID(str(trace_id))
        except ValueError:
            self.fail(f"X-Trace-Id não é UUID válido: {trace_id}")


class AuthenticatedClientMixin:
    """Mixin que expõe authenticated_client com user logado."""

    _auth_user: Any = None
    _auth_client: Client | None = None

    @property
    def authenticated_client(self) -> Client:
        if self._auth_client is None:
            User = get_user_model()
            user, _ = User.objects.get_or_create(
                email="test@example.com",
            )
            user.set_password("test-pass-123")
            user.save()
            client = Client()
            client.force_login(user)
            self._auth_user = user
            self._auth_client = client
        return self._auth_client
