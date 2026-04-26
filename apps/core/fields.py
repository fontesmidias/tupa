"""Campos de modelo customizados — Story 2.5.

EncryptedCharField: CharField que criptografa o valor em repouso usando
cryptography.fernet.Fernet. A chave deve vir de settings.FIELD_ENCRYPTION_KEY
(base64 urlsafe 32 bytes). Substituível por django-cryptography-django5 na Story 3.7.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db import models


_MARKER = "enc::"


@lru_cache(maxsize=1)
def _get_fernet() -> Fernet:
    key = getattr(settings, "FIELD_ENCRYPTION_KEY", "") or ""
    if not key:
        raise ImproperlyConfigured(
            "FIELD_ENCRYPTION_KEY não configurada — defina no .env (Fernet key base64 32 bytes)."
        )
    try:
        return Fernet(key.encode("utf-8") if isinstance(key, str) else key)
    except (ValueError, TypeError) as exc:
        raise ImproperlyConfigured(
            "FIELD_ENCRYPTION_KEY inválida — gere com "
            "`python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\"`."
        ) from exc


def _encrypt(value: str) -> str:
    token = _get_fernet().encrypt(value.encode("utf-8")).decode("utf-8")
    return f"{_MARKER}{token}"


def _decrypt(value: str) -> str:
    if not value.startswith(_MARKER):
        # Valor em texto plano (legado ou teste); retorna como está.
        return value
    token = value[len(_MARKER):]
    try:
        return _get_fernet().decrypt(token.encode("utf-8")).decode("utf-8")
    except InvalidToken as exc:
        raise ImproperlyConfigured("Falha ao descriptografar EncryptedCharField") from exc


class _EncryptedMixin:
    """Lógica comum de encrypt/decrypt para CharField/TextField — Story 3.7."""

    def from_db_value(  # type: ignore[no-untyped-def]
        self, value: Any, expression: Any, connection: Any
    ) -> str | None:
        if value is None:
            return None
        return _decrypt(str(value))

    def to_python(self, value: Any) -> str | None:  # type: ignore[no-untyped-def]
        if value is None:
            return None
        if isinstance(value, str):
            if value.startswith(_MARKER):
                return _decrypt(value)
            return value
        return str(value)

    def get_prep_value(self, value: Any) -> str | None:  # type: ignore[no-untyped-def]
        if value is None:
            return None
        s = str(value)
        if s.startswith(_MARKER):
            return s
        return _encrypt(s)


class EncryptedCharField(_EncryptedMixin, models.CharField):  # type: ignore[type-arg]
    """CharField com criptografia Fernet em repouso."""

    description = "CharField criptografado via Fernet."

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        kwargs.setdefault("max_length", 512)
        super().__init__(*args, **kwargs)


class EncryptedTextField(_EncryptedMixin, models.TextField):  # type: ignore[type-arg]
    """TextField com criptografia Fernet em repouso — Story 3.7."""

    description = "TextField criptografado via Fernet."
