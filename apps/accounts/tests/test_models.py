"""Testes User model + Tomador + Circulo (Story 2.1)."""

from __future__ import annotations

import pytest
from django.db import IntegrityError

from apps.accounts.models import Circulo, Tomador, User
from apps.accounts.tests.factories import (
    CirculoFactory,
    GestorUserFactory,
    RhAdminUserFactory,
    TomadorFactory,
    UserFactory,
)


@pytest.mark.django_db
def test_user_pk_uuid():
    u = UserFactory()
    assert isinstance(u.pk, type(u.id))
    assert len(str(u.id)) == 36


@pytest.mark.django_db
def test_email_lowercased_on_save():
    u = User.objects.create_user(email="Foo@BAR.com", password="x")
    assert u.email == "foo@bar.com"


@pytest.mark.django_db
def test_email_unique_case_insensitive():
    User.objects.create_user(email="a@b.com", password="x")
    with pytest.raises(IntegrityError):
        User.objects.create_user(email="A@B.COM", password="x")


@pytest.mark.django_db
def test_username_field_is_email():
    assert User.USERNAME_FIELD == "email"
    assert User.REQUIRED_FIELDS == []


@pytest.mark.django_db
def test_is_cadastro_completo_false_default():
    u = UserFactory(nome="", tipo_gestor=None, tomador=None)
    assert u.is_cadastro_completo is False


@pytest.mark.django_db
def test_is_cadastro_completo_true():
    u = GestorUserFactory()
    assert u.is_cadastro_completo is True


@pytest.mark.django_db
def test_is_cadastro_completo_partial():
    t = TomadorFactory()
    u = UserFactory(nome="Alice", tipo_gestor=None, tomador=t)
    assert u.is_cadastro_completo is False
    u2 = UserFactory(nome="", tipo_gestor="A", tomador=t)
    assert u2.is_cadastro_completo is False


@pytest.mark.django_db
def test_fk_tomador_circulo():
    t = TomadorFactory()
    c = CirculoFactory()
    u = UserFactory(tomador=t, circulo=c)
    assert u.tomador == t
    assert u.circulo == c


@pytest.mark.django_db
def test_rh_admin_factory():
    u = RhAdminUserFactory()
    assert u.is_staff is True


@pytest.mark.django_db
def test_tomador_str():
    t = TomadorFactory(nome="Empresa X")
    assert str(t) == "Empresa X"


@pytest.mark.django_db
def test_circulo_str():
    c = CirculoFactory(nome="RH")
    assert str(c) == "RH"


@pytest.mark.django_db
def test_user_str():
    u = UserFactory(email="z@test.local")
    assert str(u) == "z@test.local"


@pytest.mark.django_db
def test_tipo_gestor_choices():
    assert "A" in User.TipoGestor.values
    assert "B" in User.TipoGestor.values
    assert "C" in User.TipoGestor.values


@pytest.mark.django_db
def test_anonimizado_em_nullable():
    u = UserFactory()
    assert u.anonimizado_em is None


@pytest.mark.django_db
def test_tomador_circulo_uuid_pks():
    t = TomadorFactory()
    c = CirculoFactory()
    assert len(str(t.id)) == 36
    assert len(str(c.id)) == 36
    assert isinstance(t, Tomador)
    assert isinstance(c, Circulo)
