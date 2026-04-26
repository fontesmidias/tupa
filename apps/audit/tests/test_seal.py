"""Testes de AuditLog.seal — happy path, chain, sem actor, determinismo."""

from __future__ import annotations

import hashlib

import pytest

from apps.accounts.models import User
from apps.audit.models import ZERO_HASH, AuditLog
from apps.audit.utils import canonical_json


@pytest.fixture
def user(db):
    return User.objects.create_user(email="a@b.com", password="x")


@pytest.fixture
def entity(user):
    # user serve como entity genérica também (tem pk + _meta)
    return user


@pytest.mark.django_db
def test_seal_primeiro_registro_usa_zero_hash(user, entity):
    log = AuditLog.seal(
        actor=user,
        entity=entity,
        before={},
        after={"nome": "X"},
        action="user.created",
        ip="127.0.0.1",
        user_agent="ua/1",
    )
    assert log.hash_prev == ZERO_HASH
    assert len(log.hash_curr) == 64
    assert log.actor_user_id == user.pk
    assert log.entity_type == "accounts.User"
    assert log.entity_id == str(entity.pk)


@pytest.mark.django_db
def test_seal_chain_integra(user, entity):
    l1 = AuditLog.seal(user, entity, {}, {"v": 1}, "x")
    l2 = AuditLog.seal(user, entity, {"v": 1}, {"v": 2}, "y")
    l3 = AuditLog.seal(user, entity, {"v": 2}, {"v": 3}, "z")
    assert l2.hash_prev == l1.hash_curr
    assert l3.hash_prev == l2.hash_curr
    assert len({l1.hash_curr, l2.hash_curr, l3.hash_curr}) == 3


@pytest.mark.django_db
def test_seal_sem_actor_system(entity):
    log = AuditLog.seal(
        actor=None,
        entity=entity,
        before={},
        after={},
        action="system:cleanup",
    )
    assert log.actor_user_id is None
    assert log.action == "system:cleanup"


@pytest.mark.django_db
def test_seal_hash_recomputavel(user, entity):
    log = AuditLog.seal(user, entity, {}, {"v": 1}, "x", ip="1.1.1.1", user_agent="ua")
    payload = {
        "actor_user_id": str(user.pk),
        "ip": "1.1.1.1",
        "user_agent": "ua",
        "action": "x",
        "entity_type": "accounts.User",
        "entity_id": str(entity.pk),
        "before": {},
        "after": {"v": 1},
        "timestamp_iso": log.timestamp.isoformat(),
    }
    expected = hashlib.sha256(
        f"{log.hash_prev}{canonical_json(payload)}".encode("utf-8")
    ).hexdigest()
    assert log.hash_curr == expected


@pytest.mark.django_db
def test_seal_defaults_ip_user_agent(user, entity):
    log = AuditLog.seal(user, entity, {}, {}, "a")
    assert log.ip is None
    assert log.user_agent == ""


@pytest.mark.django_db
def test_seal_persistido_no_banco(user, entity):
    log = AuditLog.seal(user, entity, {}, {}, "a")
    assert AuditLog.objects.filter(pk=log.pk).exists()
