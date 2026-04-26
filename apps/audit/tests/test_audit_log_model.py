"""Testes do model AuditLog: campos, indexes, unique, defaults."""

from __future__ import annotations

import uuid

import pytest
from django.db import IntegrityError
from django.db.utils import DataError

from apps.audit.models import AuditLog


@pytest.mark.django_db
def test_auditlog_campos_basicos_e_defaults():
    log = AuditLog.objects.create(
        action="user.created",
        entity_type="accounts.User",
        entity_id=str(uuid.uuid4()),
        hash_prev="0" * 64,
        hash_curr="a" * 64,
    )
    assert isinstance(log.id, uuid.UUID)
    assert log.actor_user_id is None
    assert log.ip is None
    assert log.user_agent == ""
    assert log.before == {}
    assert log.after == {}
    assert log.timestamp is not None


@pytest.mark.django_db
def test_auditlog_db_table_name():
    assert AuditLog._meta.db_table == "audit_log"


@pytest.mark.django_db
def test_auditlog_indexes_definidos():
    index_fields = {tuple(idx.fields) for idx in AuditLog._meta.indexes}
    assert ("entity_type", "entity_id", "timestamp") in index_fields
    assert ("actor_user_id", "timestamp") in index_fields


@pytest.mark.django_db
def test_auditlog_hash_curr_unique():
    AuditLog.objects.create(
        action="a",
        entity_type="t",
        entity_id="1",
        hash_prev="0" * 64,
        hash_curr="b" * 64,
    )
    with pytest.raises((IntegrityError, DataError)):
        AuditLog.objects.create(
            action="b",
            entity_type="t",
            entity_id="2",
            hash_prev="b" * 64,
            hash_curr="b" * 64,
        )
