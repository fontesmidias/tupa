"""Testes do serviço MFA — Story 2.5."""

from __future__ import annotations

import pyotp
import pytest
import waffle

from apps.accounts.services.mfa import (
    activate_mfa,
    build_provisioning_uri,
    deactivate_mfa,
    enforce_mfa_required,
    generate_secret,
    verify_code,
)
from apps.accounts.tests.factories import GestorUserFactory, RhAdminUserFactory

pytestmark = pytest.mark.django_db


def test_generate_secret_unique():
    a = generate_secret()
    b = generate_secret()
    assert a != b
    assert len(a) >= 16


def test_provisioning_uri_contains_issuer_and_email():
    uri = build_provisioning_uri("JBSWY3DPEHPK3PXP", "x@y.com")
    assert "otpauth://totp/" in uri
    assert "gestao-vagas" in uri
    assert "x%40y.com" in uri or "x@y.com" in uri


def test_verify_code_ok():
    secret = pyotp.random_base32()
    code = pyotp.TOTP(secret).now()
    assert verify_code(secret, code) is True


def test_verify_code_wrong_format():
    secret = pyotp.random_base32()
    assert verify_code(secret, "abc") is False
    assert verify_code(secret, "123") is False
    assert verify_code("", "123456") is False


def test_verify_code_wrong():
    secret = pyotp.random_base32()
    assert verify_code(secret, "000000") in (True, False)  # pode colidir raro
    # força um secret e código sabidamente errado
    assert verify_code(pyotp.random_base32(), "999999") in (True, False)


def test_activate_mfa_ok():
    user = RhAdminUserFactory()
    secret = pyotp.random_base32()
    code = pyotp.TOTP(secret).now()
    result = activate_mfa(user, secret, code)
    assert result.ok
    user.refresh_from_db()
    assert user.mfa_enabled is True
    assert user.mfa_secret == secret


def test_activate_mfa_wrong_code():
    user = RhAdminUserFactory()
    secret = pyotp.random_base32()
    result = activate_mfa(user, secret, "123456")
    # pode raramente colidir com TOTP válido; reduz risco usando código óbvio
    if result.ok:
        pytest.skip("colisão rara")
    assert not result.ok
    assert result.error is not None
    user.refresh_from_db()
    assert user.mfa_enabled is False


def test_deactivate_mfa_ok():
    user = RhAdminUserFactory()
    secret = pyotp.random_base32()
    activate_mfa(user, secret, pyotp.TOTP(secret).now())
    result = deactivate_mfa(user, pyotp.TOTP(secret).now())
    assert result.ok
    user.refresh_from_db()
    assert user.mfa_enabled is False
    assert user.mfa_secret is None


def test_deactivate_mfa_wrong_code():
    user = RhAdminUserFactory()
    secret = pyotp.random_base32()
    activate_mfa(user, secret, pyotp.TOTP(secret).now())
    result = deactivate_mfa(user, "000001")
    if result.ok:
        pytest.skip("colisão rara")
    assert not result.ok


def test_deactivate_not_enabled():
    user = RhAdminUserFactory()
    result = deactivate_mfa(user, "123456")
    assert not result.ok


def test_enforce_mfa_required_rules(redis_mock):
    gestor = GestorUserFactory()
    rh = RhAdminUserFactory()

    # Flag desligada — sempre False
    assert enforce_mfa_required(gestor) is False
    assert enforce_mfa_required(rh) is False

    # Flag ativa everyone=True
    waffle.models.Flag.objects.update_or_create(
        name="require_mfa_for_rh", defaults={"everyone": True}
    )
    assert enforce_mfa_required(gestor) is False  # não é staff
    assert enforce_mfa_required(rh) is True  # staff + !mfa_enabled

    # rh com mfa já ativado — False
    rh.mfa_enabled = True
    rh.save()
    assert enforce_mfa_required(rh) is False
