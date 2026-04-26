"""Testes EncryptedCharField — Story 2.5."""

from __future__ import annotations

import pytest
from django.core.exceptions import ImproperlyConfigured
from django.test import override_settings

from apps.core.fields import _MARKER, EncryptedCharField, _decrypt, _encrypt, _get_fernet
from apps.core.tests.models import ConcreteEncrypted


pytestmark = pytest.mark.django_db


def test_encrypt_decrypt_roundtrip():
    enc = _encrypt("hello-world")
    assert enc.startswith(_MARKER)
    assert _decrypt(enc) == "hello-world"


def test_decrypt_plaintext_passthrough():
    assert _decrypt("plain") == "plain"


def test_model_roundtrip():
    obj = ConcreteEncrypted.objects.create(secret="my-secret")
    # Reload
    obj2 = ConcreteEncrypted.objects.get(pk=obj.pk)
    assert obj2.secret == "my-secret"


def test_model_none():
    obj = ConcreteEncrypted.objects.create(secret=None)
    obj2 = ConcreteEncrypted.objects.get(pk=obj.pk)
    assert obj2.secret is None


def test_to_python_plain():
    f = EncryptedCharField()
    assert f.to_python("plain") == "plain"
    assert f.to_python(None) is None


def test_to_python_encrypted():
    f = EncryptedCharField()
    token = _encrypt("xyz")
    assert f.to_python(token) == "xyz"


def test_get_prep_value_none():
    f = EncryptedCharField()
    assert f.get_prep_value(None) is None


def test_get_prep_value_already_encrypted():
    f = EncryptedCharField()
    token = _encrypt("abc")
    # Não re-encripta
    assert f.get_prep_value(token) == token


def test_raw_db_value_is_encrypted():
    """Verifica que a coluna persistida NÃO contém texto plano."""
    from django.db import connection
    obj = ConcreteEncrypted.objects.create(secret="plaintext-sensitive")
    table = ConcreteEncrypted._meta.db_table
    with connection.cursor() as cur:
        cur.execute(f"SELECT secret FROM {table} WHERE id=%s", [obj.pk])
        raw = cur.fetchone()[0]
    assert "plaintext-sensitive" not in raw
    assert raw.startswith(_MARKER)


def test_missing_key_raises():
    _get_fernet.cache_clear()
    with override_settings(FIELD_ENCRYPTION_KEY=""):
        with pytest.raises(ImproperlyConfigured):
            _get_fernet()
    _get_fernet.cache_clear()


def test_invalid_key_raises():
    _get_fernet.cache_clear()
    with override_settings(FIELD_ENCRYPTION_KEY="not-a-valid-fernet-key"):
        with pytest.raises(ImproperlyConfigured):
            _get_fernet()
    _get_fernet.cache_clear()
