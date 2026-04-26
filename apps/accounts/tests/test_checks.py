"""Testes dos system checks de compliance (Party Mode — Mary)."""

from __future__ import annotations

from django.test import override_settings

from apps.accounts.checks import (
    dpo_email_required,
    field_encryption_key_required,
)


def test_dpo_email_vazio_bloqueia_deploy():
    with override_settings(DPO_EMAIL=""):
        errors = dpo_email_required(None)
    assert len(errors) == 1
    assert errors[0].id == "accounts.E001"


def test_dpo_email_preenchido_passa():
    with override_settings(DPO_EMAIL="dpo@example.com"):
        errors = dpo_email_required(None)
    assert errors == []


def test_field_encryption_key_vazia_bloqueia_deploy():
    with override_settings(FIELD_ENCRYPTION_KEY=""):
        errors = field_encryption_key_required(None)
    assert len(errors) == 1
    assert errors[0].id == "accounts.E002"


def test_field_encryption_key_preenchida_passa():
    with override_settings(FIELD_ENCRYPTION_KEY="some-key"):
        errors = field_encryption_key_required(None)
    assert errors == []
