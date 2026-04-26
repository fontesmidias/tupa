"""Testes da view /auth/codigo/ POST — Story 2.3."""

from __future__ import annotations

import hashlib
from datetime import timedelta

import pytest
from django.test import Client
from django.urls import reverse
from django.utils import timezone

from apps.accounts.models import MagicLink
from apps.accounts.services.magic_link_consume import FAIL_MAX

pytestmark = pytest.mark.django_db


def _hash(code: str) -> str:
    return hashlib.sha256(code.encode()).hexdigest()


def _make_ml(email="alice@example.com", code="123456", ip="1.2.3.4", ua="ua", mins=15):
    return MagicLink.objects.create(
        email=email,
        code_hash=_hash(code),
        ip=ip,
        user_agent=ua,
        expires_at=timezone.now() + timedelta(minutes=mins),
    )


def test_get_renderiza_form(client: Client, redis_mock):
    resp = client.get(reverse("accounts:auth_consume_code"), {"email": "x@y.com"})
    assert resp.status_code == 200
    assert b"<form" in resp.content
    assert b"x@y.com" in resp.content


def test_post_valido_loga_e_redireciona(client: Client, redis_mock):
    _make_ml(ip="127.0.0.1", ua="")
    resp = client.post(
        reverse("accounts:auth_consume_code"),
        data={"email": "alice@example.com", "code": "123456"},
        REMOTE_ADDR="127.0.0.1",
    )
    assert resp.status_code == 302
    # Sessão autenticada
    assert "_auth_user_id" in client.session


def test_post_expirado_renderiza_erro(client: Client, redis_mock):
    _make_ml(ip="127.0.0.1", ua="", mins=-1)
    resp = client.post(
        reverse("accounts:auth_consume_code"),
        data={"email": "alice@example.com", "code": "123456"},
        REMOTE_ADDR="127.0.0.1",
    )
    assert resp.status_code == 200
    assert b"c\xc3\xb3digo expirado" in resp.content


def test_post_codigo_errado_invalid(client: Client, redis_mock):
    _make_ml(ip="127.0.0.1", ua="")
    resp = client.post(
        reverse("accounts:auth_consume_code"),
        data={"email": "alice@example.com", "code": "999999"},
        REMOTE_ADDR="127.0.0.1",
    )
    assert resp.status_code == 200
    assert b"c\xc3\xb3digo inv\xc3\xa1lido" in resp.content


def test_post_cinco_erros_sexto_429(client: Client, redis_mock):
    _make_ml(ip="8.8.8.8", ua="")
    for _ in range(FAIL_MAX):
        client.post(
            reverse("accounts:auth_consume_code"),
            data={"email": "alice@example.com", "code": "999999"},
            REMOTE_ADDR="8.8.8.8",
        )
    resp = client.post(
        reverse("accounts:auth_consume_code"),
        data={"email": "alice@example.com", "code": "999999"},
        REMOTE_ADDR="8.8.8.8",
    )
    assert resp.status_code == 429
    assert resp.json()["code"] == "BLOCKED"


def test_post_context_mismatch_mensagem_novo_codigo(client: Client, redis_mock):
    _make_ml(ip="1.2.3.4", ua="original-ua")
    resp = client.post(
        reverse("accounts:auth_consume_code"),
        data={"email": "alice@example.com", "code": "123456"},
        REMOTE_ADDR="9.9.9.9",
        HTTP_USER_AGENT="outra-ua",
    )
    assert resp.status_code == 200
    assert b"Novo c\xc3\xb3digo enviado" in resp.content
    # Original ainda válido
    ml = MagicLink.objects.filter(ip="1.2.3.4").first()
    assert ml is not None
    assert ml.used_at is None
