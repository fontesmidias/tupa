"""Testes do serviço request_magic_link — Story 2.2."""

from __future__ import annotations

import hashlib

import pytest
from django.core import mail
from django.utils import timezone

from apps.accounts.models import MagicLink
from apps.accounts.services import magic_link as svc


pytestmark = pytest.mark.django_db


def test_happy_path_cria_magiclink_e_envia_email(redis_mock):
    result = svc.request_magic_link(
        email="Alice@Example.com", ip="1.2.3.4", user_agent="Mozilla"
    )
    assert result.ok is True
    assert result.value is not None
    ml = result.value
    assert ml.email == "alice@example.com"
    assert len(ml.code_hash) == 64
    assert ml.expires_at > timezone.now()
    assert ml.used_at is None
    assert MagicLink.objects.count() == 1
    assert len(mail.outbox) == 1
    msg = mail.outbox[0]
    assert msg.subject == "Seu código gestao-vagas"
    assert "expira em 15 minutos" in msg.body
    # Código não armazenado em claro
    import re
    m = re.search(r"(\d{6})", msg.body)
    assert m is not None
    assert hashlib.sha256(m.group(1).encode()).hexdigest() == ml.code_hash


def test_email_invalido_retorna_erro(redis_mock):
    result = svc.request_magic_link(email="nao-email", ip="1.2.3.4", user_agent="ua")
    assert result.ok is False
    assert result.error is not None
    assert result.error.code == "INVALID_EMAIL"
    assert MagicLink.objects.count() == 0
    assert len(mail.outbox) == 0


def test_email_vazio_retorna_erro(redis_mock):
    result = svc.request_magic_link(email="", ip="1.2.3.4", user_agent="")
    assert result.ok is False
    assert result.error is not None
    assert result.error.code == "INVALID_EMAIL"


def test_rate_limit_dispara_apos_5(redis_mock):
    for i in range(5):
        r = svc.request_magic_link(
            email="bob@example.com", ip="9.9.9.9", user_agent="ua"
        )
        assert r.ok is True, f"tentativa {i} deveria passar"
    # Sexta é bloqueada
    r6 = svc.request_magic_link(
        email="bob@example.com", ip="9.9.9.9", user_agent="ua"
    )
    assert r6.ok is False
    assert r6.error is not None
    assert r6.error.code == "RATE_LIMITED"
    assert MagicLink.objects.filter(email="bob@example.com").count() == 5


def test_rate_limit_isolado_por_ip_diferente(redis_mock):
    for _ in range(5):
        svc.request_magic_link(email="c@x.com", ip="1.1.1.1", user_agent="u")
    r_ip2 = svc.request_magic_link(email="c@x.com", ip="2.2.2.2", user_agent="u")
    assert r_ip2.ok is True


def test_mask_email_helper():
    assert svc._mask_email("alice@example.com") == "al***@example.com"
    assert svc._mask_email("a@b.com") == "a***@b.com"
    assert svc._mask_email("no-at-sign") == "no***"


def test_generate_code_6_digitos():
    for _ in range(20):
        code = svc._generate_code()
        assert len(code) == 6
        assert code.isdigit()


def test_user_agent_truncado_512(redis_mock):
    long_ua = "x" * 1000
    r = svc.request_magic_link(email="d@x.com", ip="3.3.3.3", user_agent=long_ua)
    assert r.ok is True
    assert r.value is not None
    assert len(r.value.user_agent) == 512


def test_ip_vazio_salva_none(redis_mock):
    r = svc.request_magic_link(email="e@x.com", ip="", user_agent="ua")
    assert r.ok is True
    assert r.value is not None
    assert r.value.ip is None
