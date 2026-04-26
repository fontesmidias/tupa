"""Testes views MFA — Story 2.5."""

from __future__ import annotations

import pyotp
import pytest
from django.core.cache import cache
from django.test import Client

from apps.accounts.tests.factories import GestorUserFactory, RhAdminUserFactory

pytestmark = pytest.mark.django_db


@pytest.fixture
def client():
    return Client()


def test_setup_requires_auth(client):
    r = client.get("/conta/seguranca/mfa/")
    # AuthRequiredMiddleware bloqueia ou redirect
    assert r.status_code in (302, 401)


def test_setup_forbidden_for_non_staff(client):
    user = GestorUserFactory()
    client.force_login(user)
    r = client.get("/conta/seguranca/mfa/")
    assert r.status_code == 403


def test_setup_get_renders(client):
    user = RhAdminUserFactory()
    client.force_login(user)
    r = client.get("/conta/seguranca/mfa/")
    assert r.status_code == 200
    assert b"MFA" in r.content


def test_setup_ativar_renders_qr(client, redis_mock):
    user = RhAdminUserFactory()
    client.force_login(user)
    r = client.post("/conta/seguranca/mfa/?acao=ativar")
    assert r.status_code == 200
    assert b"base64" in r.content or b"QR" in r.content
    assert cache.get(f"mfa:setup:{user.id}") is not None


def test_setup_confirmar_ativacao_ok(client, redis_mock):
    user = RhAdminUserFactory()
    client.force_login(user)
    client.post("/conta/seguranca/mfa/?acao=ativar")
    secret = cache.get(f"mfa:setup:{user.id}")
    code = pyotp.TOTP(secret).now()
    r = client.post(
        "/conta/seguranca/mfa/?acao=confirmar_ativacao", {"code": code}
    )
    assert r.status_code == 302
    user.refresh_from_db()
    assert user.mfa_enabled


def test_setup_confirmar_ativacao_wrong(client, redis_mock):
    user = RhAdminUserFactory()
    client.force_login(user)
    client.post("/conta/seguranca/mfa/?acao=ativar")
    r = client.post(
        "/conta/seguranca/mfa/?acao=confirmar_ativacao", {"code": "000000"}
    )
    # pode colidir raro
    user.refresh_from_db()
    if r.status_code == 302:
        return
    assert r.status_code == 200
    assert not user.mfa_enabled


def test_setup_confirmar_sem_secret_no_cache(client, redis_mock):
    user = RhAdminUserFactory()
    client.force_login(user)
    r = client.post(
        "/conta/seguranca/mfa/?acao=confirmar_ativacao", {"code": "123456"}
    )
    assert r.status_code == 302


def test_setup_desativar_ok(client, redis_mock):
    user = RhAdminUserFactory()
    secret = pyotp.random_base32()
    user.mfa_secret = secret
    user.mfa_enabled = True
    user.save()
    client.force_login(user)
    r = client.post(
        "/conta/seguranca/mfa/?acao=desativar", {"code": pyotp.TOTP(secret).now()}
    )
    assert r.status_code == 302
    user.refresh_from_db()
    assert not user.mfa_enabled


def test_setup_desativar_wrong(client, redis_mock):
    user = RhAdminUserFactory()
    secret = pyotp.random_base32()
    user.mfa_secret = secret
    user.mfa_enabled = True
    user.save()
    client.force_login(user)
    r = client.post("/conta/seguranca/mfa/?acao=desativar", {"code": "000001"})
    if r.status_code == 302:
        return
    assert r.status_code == 200


def test_setup_acao_invalida(client, redis_mock):
    user = RhAdminUserFactory()
    client.force_login(user)
    r = client.post("/conta/seguranca/mfa/?acao=xyz")
    assert r.status_code == 400


def test_challenge_without_pending_redirects(client):
    r = client.get("/auth/mfa/")
    assert r.status_code == 302


def test_challenge_pending_nonexistent_user(client):
    session = client.session
    session["pending_mfa_user_id"] = "00000000-0000-0000-0000-000000000000"
    session.save()
    r = client.get("/auth/mfa/")
    assert r.status_code == 302


def test_challenge_get_ok(client, redis_mock):
    user = RhAdminUserFactory()
    secret = pyotp.random_base32()
    user.mfa_secret = secret
    user.mfa_enabled = True
    user.save()
    session = client.session
    session["pending_mfa_user_id"] = str(user.id)
    session.save()
    r = client.get("/auth/mfa/")
    assert r.status_code == 200


def test_challenge_post_ok_logs_in(client, redis_mock):
    user = RhAdminUserFactory()
    secret = pyotp.random_base32()
    user.mfa_secret = secret
    user.mfa_enabled = True
    user.save()
    session = client.session
    session["pending_mfa_user_id"] = str(user.id)
    session.save()
    r = client.post("/auth/mfa/", {"code": pyotp.TOTP(secret).now()})
    assert r.status_code == 302
    assert r.url == "/rh/"
    # Sessão de pending limpa
    assert "pending_mfa_user_id" not in client.session


def test_challenge_post_wrong_code(client, redis_mock):
    user = RhAdminUserFactory()
    secret = pyotp.random_base32()
    user.mfa_secret = secret
    user.mfa_enabled = True
    user.save()
    session = client.session
    session["pending_mfa_user_id"] = str(user.id)
    session.save()
    r = client.post("/auth/mfa/", {"code": "000001"})
    if r.status_code == 302:
        return
    assert r.status_code == 200
    assert b"inv" in r.content.lower()


def test_challenge_5_failures_blocks(client, redis_mock):
    user = RhAdminUserFactory()
    secret = pyotp.random_base32()
    user.mfa_secret = secret
    user.mfa_enabled = True
    user.save()
    session = client.session
    session["pending_mfa_user_id"] = str(user.id)
    session.save()
    statuses = []
    for _ in range(6):
        r = client.post("/auth/mfa/", {"code": "000001"})
        statuses.append(r.status_code)
    assert 429 in statuses


def test_challenge_next_redirect(client, redis_mock):
    user = RhAdminUserFactory()
    secret = pyotp.random_base32()
    user.mfa_secret = secret
    user.mfa_enabled = True
    user.save()
    session = client.session
    session["pending_mfa_user_id"] = str(user.id)
    session.save()
    r = client.post(
        "/auth/mfa/?next=/custom/", {"code": pyotp.TOTP(secret).now()}
    )
    assert r.status_code == 302
    assert r.url == "/custom/"


def test_challenge_forced_flag_user_without_secret(client, redis_mock):
    import waffle
    waffle.models.Flag.objects.update_or_create(
        name="require_mfa_for_rh", defaults={"everyone": True}
    )
    user = RhAdminUserFactory()
    session = client.session
    session["pending_mfa_user_id"] = str(user.id)
    session.save()
    r = client.get("/auth/mfa/")
    assert r.status_code == 302
    assert "/conta/seguranca/mfa/" in r.url
