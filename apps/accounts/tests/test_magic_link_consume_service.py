"""Testes do serviço consume_magic_link — Story 2.3."""

from __future__ import annotations

import hashlib
from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.core import mail
from django.utils import timezone

from apps.accounts.models import MagicLink
from apps.accounts.services.magic_link_consume import (
    FAIL_MAX,
    consume_magic_link,
)

User = get_user_model()
pytestmark = pytest.mark.django_db


def _hash(code: str) -> str:
    return hashlib.sha256(code.encode()).hexdigest()


def _make_ml(
    email: str = "alice@example.com",
    code: str = "123456",
    ip: str = "1.2.3.4",
    ua: str = "Mozilla/5.0",
    expires_in_minutes: int = 15,
):
    return MagicLink.objects.create(
        email=email,
        code_hash=_hash(code),
        ip=ip,
        user_agent=ua,
        expires_at=timezone.now() + timedelta(minutes=expires_in_minutes),
    )


def test_happy_path_cria_user_e_redireciona(redis_mock):
    _make_ml()
    res = consume_magic_link(
        email="alice@example.com",
        code="123456",
        ip="1.2.3.4",
        user_agent="Mozilla/5.0",
    )
    assert res.status == "ok"
    assert res.user is not None
    assert res.user.email == "alice@example.com"
    assert res.redirect_url == "/auth/completar-perfil/"
    ml = MagicLink.objects.get(email="alice@example.com")
    assert ml.used_at is not None


def test_expirado_retorna_expired(redis_mock):
    _make_ml(expires_in_minutes=-1)
    res = consume_magic_link(
        email="alice@example.com",
        code="123456",
        ip="1.2.3.4",
        user_agent="Mozilla/5.0",
    )
    assert res.status == "expired"


def test_codigo_errado_invalid(redis_mock):
    _make_ml()
    res = consume_magic_link(
        email="alice@example.com",
        code="999999",
        ip="1.2.3.4",
        user_agent="Mozilla/5.0",
    )
    assert res.status == "invalid"


def test_cinco_erros_bloqueia_no_sexto(redis_mock):
    _make_ml()
    for _ in range(FAIL_MAX):
        r = consume_magic_link(
            email="alice@example.com",
            code="999999",
            ip="5.5.5.5",
            user_agent="ua",
        )
        assert r.status in ("invalid", "blocked")
    r6 = consume_magic_link(
        email="alice@example.com",
        code="999999",
        ip="5.5.5.5",
        user_agent="ua",
    )
    assert r6.status == "blocked"


def test_context_mismatch_ip_gera_novo_link(redis_mock):
    _make_ml(ip="1.2.3.4", ua="same-ua")
    res = consume_magic_link(
        email="alice@example.com",
        code="123456",
        ip="9.9.9.9",  # /24 diferente
        user_agent="same-ua",
    )
    assert res.status == "context_mismatch"
    assert res.new_magic_link_id is not None
    assert MagicLink.objects.filter(email="alice@example.com").count() == 2
    assert len(mail.outbox) == 1
    assert "novo código" in mail.outbox[0].body.lower()
    original = MagicLink.objects.filter(ip="1.2.3.4").first()
    assert original is not None
    assert original.used_at is None


def test_context_mismatch_ua_gera_novo_link(redis_mock):
    _make_ml(ip="1.2.3.4", ua="ua-original")
    res = consume_magic_link(
        email="alice@example.com",
        code="123456",
        ip="1.2.3.4",
        user_agent="ua-diferente",
    )
    assert res.status == "context_mismatch"
    assert res.new_magic_link_id is not None


def test_ip_mesma_classe_24_ok(redis_mock):
    _make_ml(ip="10.0.0.5", ua="ua")
    res = consume_magic_link(
        email="alice@example.com",
        code="123456",
        ip="10.0.0.200",
        user_agent="ua",
    )
    assert res.status == "ok"


def test_user_existente_redireciona_gestor(redis_mock):
    from apps.accounts.tests.factories import GestorUserFactory

    u = GestorUserFactory(email="bob@example.com")
    assert u.is_cadastro_completo is True
    _make_ml(email="bob@example.com", ip="1.1.1.1", ua="ua")
    res = consume_magic_link(
        email="bob@example.com",
        code="123456",
        ip="1.1.1.1",
        user_agent="ua",
    )
    assert res.status == "ok"
    assert res.redirect_url == "/gestor/"


def test_user_staff_redireciona_rh(redis_mock):
    from apps.accounts.tests.factories import RhAdminUserFactory

    RhAdminUserFactory(email="rh@example.com", tipo_gestor="A")
    # Força cadastro completo
    from apps.accounts.tests.factories import TomadorFactory

    u = User.objects.get(email="rh@example.com")
    u.tomador = TomadorFactory()
    u.save()
    _make_ml(email="rh@example.com", ip="1.1.1.1", ua="ua")
    res = consume_magic_link(
        email="rh@example.com",
        code="123456",
        ip="1.1.1.1",
        user_agent="ua",
    )
    assert res.status == "ok"
    assert res.redirect_url == "/rh/"


def test_user_novo_vai_para_completar_perfil(redis_mock):
    _make_ml(email="novo@example.com", ip="2.2.2.2", ua="ua")
    res = consume_magic_link(
        email="novo@example.com",
        code="123456",
        ip="2.2.2.2",
        user_agent="ua",
    )
    assert res.status == "ok"
    assert res.redirect_url == "/auth/completar-perfil/"
    assert User.objects.filter(email="novo@example.com").exists()


def test_code_nao_numerico_invalid(redis_mock):
    res = consume_magic_link(
        email="x@y.com", code="abcdef", ip="1.1.1.1", user_agent="ua"
    )
    assert res.status == "invalid"


def test_email_vazio_invalid(redis_mock):
    res = consume_magic_link(email="", code="123456", ip="1.1.1.1", user_agent="ua")
    assert res.status == "invalid"


def test_bloqueado_retorna_blocked_imediato(redis_mock):
    _make_ml()
    # Dispara bloqueio com 5 erros
    for _ in range(FAIL_MAX):
        consume_magic_link(
            email="alice@example.com", code="000000", ip="7.7.7.7", user_agent="ua"
        )
    # Mesmo com código correto, está bloqueado
    res = consume_magic_link(
        email="alice@example.com",
        code="123456",
        ip="7.7.7.7",
        user_agent="Mozilla/5.0",
    )
    assert res.status == "blocked"


def test_consume_returns_mfa_required_when_user_has_mfa_enabled(redis_mock):
    """Story 2.5: user com mfa_enabled retorna status mfa_required."""
    import pyotp
    user = User.objects.create_user(email="mfa@example.com")
    user.mfa_enabled = True
    user.mfa_secret = pyotp.random_base32()
    user.save()
    _make_ml(email="mfa@example.com", code="654321", ip="1.2.3.4", ua="UA")
    res = consume_magic_link(
        email="mfa@example.com",
        code="654321",
        ip="1.2.3.4",
        user_agent="UA",
    )
    assert res.status == "mfa_required"
    assert res.redirect_url == "/auth/mfa/"
    assert res.user is not None


def test_consume_returns_mfa_required_when_flag_forces_rh(redis_mock):
    """Story 2.5: rh_admin sem mfa com flag ativa retorna mfa_required."""
    import waffle
    waffle.models.Flag.objects.update_or_create(
        name="require_mfa_for_rh", defaults={"everyone": True}
    )
    user = User.objects.create_user(email="rh@example.com")
    user.is_staff = True
    user.role = "rh_admin"
    user.save()
    _make_ml(email="rh@example.com", code="111222", ip="1.2.3.4", ua="UA")
    res = consume_magic_link(
        email="rh@example.com",
        code="111222",
        ip="1.2.3.4",
        user_agent="UA",
    )
    assert res.status == "mfa_required"
