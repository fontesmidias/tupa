"""Testes MfaRequiredMiddleware — Story 2.5."""

from __future__ import annotations

import pytest
import waffle
from django.test import Client

from apps.accounts.tests.factories import (
    GestorUserFactory,
    RhAdminUserFactory,
    TomadorFactory,
)


def _complete(user):
    user.nome = "RH Nome"
    user.tipo_gestor = "A"
    user.tomador = TomadorFactory()
    user.save()
    return user

pytestmark = pytest.mark.django_db


@pytest.fixture
def client():
    return Client()


@pytest.fixture
def mfa_flag_on(redis_mock):
    flag, _ = waffle.models.Flag.objects.update_or_create(
        name="require_mfa_for_rh", defaults={"everyone": True}
    )
    yield flag
    from django.core.cache import cache as _c
    _c.clear()


def test_flag_on_staff_without_mfa_redirects(client, mfa_flag_on):
    user = _complete(RhAdminUserFactory())
    client.force_login(user)
    r = client.get("/rh/")
    assert r.status_code == 302
    assert "/conta/seguranca/mfa/" in r.url


def test_flag_on_staff_with_mfa_passes(client, mfa_flag_on):
    user = _complete(RhAdminUserFactory(mfa_enabled=True, mfa_secret="XYZ"))
    client.force_login(user)
    r = client.get("/rh/")
    assert r.status_code == 200


def test_flag_on_non_staff_passes(client, mfa_flag_on):
    user = GestorUserFactory()
    client.force_login(user)
    r = client.get("/gestor/")
    assert r.status_code == 200


def test_flag_off_staff_without_mfa_passes(client, redis_mock):
    waffle.models.Flag.objects.filter(name="require_mfa_for_rh").delete()
    user = _complete(RhAdminUserFactory())
    client.force_login(user)
    r = client.get("/rh/")
    assert r.status_code == 200


def test_anonymous_passes_middleware(client, mfa_flag_on):
    # Anônimo é barrado antes por AuthRequiredMiddleware em path privado,
    # mas deve passar no MfaRequiredMiddleware sem lançar.
    r = client.get("/auth/entrar/")
    assert r.status_code == 200


def test_bypass_paths_allow_setup(client, mfa_flag_on):
    user = RhAdminUserFactory()
    client.force_login(user)
    r = client.get("/conta/seguranca/mfa/")
    # Deve ir direto pro setup (não loop)
    assert r.status_code == 200
