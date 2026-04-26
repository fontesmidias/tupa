"""Testes de enforcement append-only."""

from __future__ import annotations

import uuid

import pytest

from apps.audit.exceptions import AuditAppendOnlyError
from apps.audit.models import AuditLog


def _mk(i: int = 0) -> AuditLog:
    return AuditLog.objects.create(
        action="a",
        entity_type="t",
        entity_id=str(i),
        hash_prev="0" * 64,
        hash_curr=f"{i:064d}",
    )


@pytest.mark.django_db
def test_save_em_registro_existente_bloqueado():
    log = _mk(1)
    log.action = "outra"
    with pytest.raises(AuditAppendOnlyError):
        log.save()


@pytest.mark.django_db
def test_delete_bloqueado():
    log = _mk(2)
    with pytest.raises(AuditAppendOnlyError):
        log.delete()


@pytest.mark.django_db
def test_queryset_update_bloqueado():
    _mk(3)
    with pytest.raises(AuditAppendOnlyError):
        AuditLog.objects.all().update(action="x")


@pytest.mark.django_db
def test_queryset_delete_bloqueado():
    _mk(4)
    with pytest.raises(AuditAppendOnlyError):
        AuditLog.objects.all().delete()


@pytest.mark.django_db
def test_bulk_create_permitido():
    logs = [
        AuditLog(
            action="a",
            entity_type="t",
            entity_id=str(i),
            hash_prev="0" * 64,
            hash_curr=f"{i + 100:064d}",
        )
        for i in range(3)
    ]
    AuditLog.objects.bulk_create(logs)
    assert AuditLog.objects.count() == 3


@pytest.mark.django_db
def test_novo_save_permitido():
    log = AuditLog(
        id=uuid.uuid4(),
        action="a",
        entity_type="t",
        entity_id="9",
        hash_prev="0" * 64,
        hash_curr="f" * 64,
    )
    log.save()
    assert AuditLog.objects.filter(pk=log.pk).exists()
