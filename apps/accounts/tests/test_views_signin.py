"""Testes da view /auth/entrar/ — Story 2.2."""

from __future__ import annotations

import pytest
from django.core import mail
from django.test import Client
from django.urls import reverse

from apps.accounts.models import MagicLink


pytestmark = pytest.mark.django_db


def test_get_renderiza_form(client: Client, redis_mock):
    resp = client.get(reverse("accounts:auth_signin"))
    assert resp.status_code == 200
    assert b"<form" in resp.content
    assert b"email" in resp.content.lower()


def test_post_valido_redireciona_para_codigo(client: Client, redis_mock):
    resp = client.post(
        reverse("accounts:auth_signin"),
        data={"email": "x@example.com"},
    )
    assert resp.status_code == 302
    assert "/auth/codigo/" in resp["Location"]
    assert "email=x%40example.com" in resp["Location"]
    assert MagicLink.objects.count() == 1
    assert len(mail.outbox) == 1


def test_post_invalido_renderiza_form_sem_criar(client: Client, redis_mock):
    resp = client.post(
        reverse("accounts:auth_signin"),
        data={"email": "nao-email"},
    )
    assert resp.status_code == 200
    assert b"<form" in resp.content
    assert MagicLink.objects.count() == 0
    assert len(mail.outbox) == 0


def test_post_rate_limit_retorna_429(client: Client, redis_mock):
    for _ in range(5):
        client.post(
            reverse("accounts:auth_signin"),
            data={"email": "z@ex.com"},
            REMOTE_ADDR="7.7.7.7",
        )
    resp = client.post(
        reverse("accounts:auth_signin"),
        data={"email": "z@ex.com"},
        REMOTE_ADDR="7.7.7.7",
    )
    assert resp.status_code == 429
    assert resp["Retry-After"]
    payload = resp.json()
    assert payload["code"] == "RATE_LIMITED"


def test_codigo_view_get_renderiza(client: Client, redis_mock):
    resp = client.get(reverse("accounts:auth_consume_code"), {"email": "abc@x.com"})
    assert resp.status_code == 200
    assert b"abc@x.com" in resp.content


def test_signin_e_codigo_sao_publicos(client: Client, redis_mock):
    # AuthRequiredMiddleware não deve bloquear
    r1 = client.get("/auth/entrar/")
    r2 = client.get("/auth/codigo/")
    assert r1.status_code == 200
    assert r2.status_code == 200
