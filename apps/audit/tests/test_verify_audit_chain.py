"""Testes do management command verify_audit_chain (Story 3.3)."""

from __future__ import annotations

from datetime import timedelta
from io import StringIO

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError
from django.db import connection
from django.utils import timezone

from apps.accounts.models import User
from apps.audit.models import AuditLog


def _raw_update(pk, **fields):
    """Bypass do AuditLogManager (append-only) para simular corrupção externa."""
    assigns = ", ".join(f'"{k}" = %s' for k in fields)
    params = list(fields.values()) + [pk.hex if hasattr(pk, "hex") else str(pk).replace("-", "")]
    with connection.cursor() as cur:
        cur.execute(f'UPDATE audit_log SET {assigns} WHERE id = %s', params)
        assert cur.rowcount == 1, f"UPDATE não afetou linha (pk={pk})"


@pytest.fixture
def user(db):
    return User.objects.create_user(email="a@b.com", password="x")


def _run(*args: str) -> str:
    out = StringIO()
    call_command("verify_audit_chain", *args, stdout=out)
    return out.getvalue()


@pytest.mark.django_db
def test_cadeia_vazia_passa():
    output = _run()
    assert "Cadeia integra: 0 registros" in output


@pytest.mark.django_db
def test_cadeia_integra_passa(user):
    for i in range(3):
        AuditLog.seal(user, user, {}, {"v": i}, f"a{i}")
    output = _run()
    assert "Cadeia integra: 3 registros" in output


@pytest.mark.django_db
def test_hash_prev_corrompido_falha(user):
    AuditLog.seal(user, user, {}, {"v": 1}, "a")
    l2 = AuditLog.seal(user, user, {}, {"v": 2}, "b")
    _raw_update(l2.pk, hash_prev="f" * 64)
    with pytest.raises(CommandError, match="hash_prev"):
        _run()


@pytest.mark.django_db
def test_hash_curr_corrompido_falha(user):
    log = AuditLog.seal(user, user, {}, {"v": 1}, "a")
    import json
    _raw_update(log.pk, after=json.dumps({"v": 999}))
    with pytest.raises(CommandError, match="hash_curr"):
        _run()


@pytest.mark.django_db
def test_since_filtra_e_ancora_hash_prev(user):
    l1 = AuditLog.seal(user, user, {}, {"v": 1}, "a")
    _raw_update(l1.pk, timestamp=timezone.now() - timedelta(hours=1))
    cutoff = timezone.now() - timedelta(minutes=1)
    AuditLog.seal(user, user, {}, {"v": 2}, "b")
    AuditLog.seal(user, user, {}, {"v": 3}, "c")
    output = _run("--since", cutoff.isoformat())
    assert "Cadeia integra: 2 registros" in output


@pytest.mark.django_db
def test_since_invalido_erro():
    with pytest.raises(CommandError, match="--since invalido"):
        _run("--since", "nao-e-data")
