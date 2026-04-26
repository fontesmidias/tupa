"""Testes Story 3.7 — User.cpf EncryptedCharField + EncryptedTextField re-export."""

from __future__ import annotations

import pytest
from django.db import connection

from apps.accounts.models import Tomador, User
from apps.accounts.services.self_service import anonymize_user
from django.db import models

from apps.core.fields import (
    _MARKER,
    EncryptedCharField,
    EncryptedTextField,
)


@pytest.fixture
def user(db):
    tomador = Tomador.objects.create(nome="T", dominio_email="x.com")
    return User.objects.create_user(
        email="u@x.com",
        password="x",
        nome="Bruno",
        tipo_gestor=User.TipoGestor.A,
        tomador=tomador,
    )


@pytest.mark.django_db
def test_user_cpf_roundtrip_via_orm(user):
    user.cpf = "12345678900"
    user.save(update_fields=["cpf"])
    fresh = User.objects.get(pk=user.pk)
    assert fresh.cpf == "12345678900"


@pytest.mark.django_db
def test_user_cpf_db_armazena_ciphertext(user):
    user.cpf = "98765432100"
    user.save(update_fields=["cpf"])
    with connection.cursor() as cur:
        cur.execute(
            f'SELECT cpf FROM {User._meta.db_table} WHERE id = %s',
            [user.pk.hex if hasattr(user.pk, "hex") else str(user.pk).replace("-", "")],
        )
        raw = cur.fetchone()[0]
    assert "98765432100" not in raw
    assert raw.startswith(_MARKER)


@pytest.mark.django_db
def test_anonymize_limpa_cpf(user):
    user.cpf = "11122233344"
    user.save(update_fields=["cpf"])
    anonymize_user(user, ip=None, user_agent="")
    user.refresh_from_db()
    assert user.cpf is None


def test_encrypted_text_field_re_exportado():
    """AC 3.7 — EncryptedTextField re-exportado e herda de TextField."""
    assert issubclass(EncryptedTextField, models.TextField)
    assert issubclass(EncryptedCharField, models.CharField)
    from apps.core import fields as _f

    assert hasattr(_f, "EncryptedTextField")
    assert hasattr(_f, "EncryptedCharField")
