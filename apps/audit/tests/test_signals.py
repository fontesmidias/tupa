"""Testes dos signals genéricos de auditoria (Story 3.2)."""

from __future__ import annotations

import uuid

import pytest

from apps.audit.models import AuditLog
from apps.audit.services import log_audit
from apps.audit.tests.models import (
    AuditableExcludeModel,
    AuditableTestModel,
    AuditableWhitelistModel,
)
from apps.audit.utils import compute_diff
from apps.core.request_context import (
    RequestContext,
    clear_request_context,
    get_request_context,
    reset_request_context,
    set_request_context,
)


@pytest.fixture
def user(db):
    from apps.accounts.models import User as UserModel

    return UserModel.objects.create_user(email="sig@t.com", password="x")


@pytest.fixture(autouse=True)
def _clear_ctx():
    clear_request_context()
    yield
    clear_request_context()


@pytest.mark.django_db
def test_post_save_create_gera_auditlog_system_quando_sem_actor():
    obj = AuditableTestModel.objects.create(name="foo")
    logs = AuditLog.objects.filter(entity_type="audit.AuditableTestModel", entity_id=str(obj.pk))
    assert logs.count() == 1
    log = logs.first()
    assert log is not None
    assert log.action == "system:created"
    assert log.actor_user_id is None
    assert log.after.get("name") == "foo"


@pytest.mark.django_db
def test_post_save_update_gera_diff_e_action_updated():
    obj = AuditableTestModel.objects.create(name="foo")
    AuditLog.objects.all().delete() if False else None  # não deletamos (append-only)
    obj.name = "bar"
    obj.save()
    logs = list(
        AuditLog.objects.filter(entity_id=str(obj.pk)).order_by("timestamp", "id")
    )
    assert len(logs) == 2
    update_log = logs[-1]
    assert update_log.action == "system:updated"
    assert update_log.before.get("name") == "foo"
    assert update_log.after.get("name") == "bar"
    # updated_at muda também; deve aparecer no diff
    assert "name" in update_log.after


@pytest.mark.django_db
def test_post_delete_gera_auditlog_com_before_snapshot():
    obj = AuditableTestModel.objects.create(name="zzz")
    pk = obj.pk
    obj.delete()
    delete_log = AuditLog.objects.filter(
        entity_id=str(pk), action__endswith="deleted"
    ).first()
    assert delete_log is not None
    assert delete_log.after == {}
    assert delete_log.before.get("name") == "zzz"


@pytest.mark.django_db
def test_actor_resolvido_do_request_context(user):
    token = set_request_context(
        RequestContext(user_id=user.pk, ip="9.9.9.9", user_agent="ua/x", trace_id=None)
    )
    try:
        obj = AuditableTestModel.objects.create(name="ctx")
    finally:
        reset_request_context(token)
    log = AuditLog.objects.filter(entity_id=str(obj.pk)).first()
    assert log is not None
    assert log.actor_user_id == user.pk
    assert log.ip == "9.9.9.9"
    assert log.user_agent == "ua/x"
    assert log.action == "created"  # com actor, sem prefixo system:


@pytest.mark.django_db
def test_whitelist_auditable_fields_exclui_secretos():
    obj = AuditableWhitelistModel.objects.create(name="a", mfa_secret="TOP")
    log = AuditLog.objects.filter(entity_id=str(obj.pk)).first()
    assert log is not None
    assert "mfa_secret" not in log.after
    assert log.after.get("name") == "a"


@pytest.mark.django_db
def test_exclude_blacklist_remove_campos():
    obj = AuditableExcludeModel.objects.create(name="b")
    log = AuditLog.objects.filter(entity_id=str(obj.pk)).first()
    assert log is not None
    assert "updated_at" not in log.after
    assert log.after.get("name") == "b"


@pytest.mark.django_db
def test_chain_continua_integra_apos_multiplas_operacoes():
    o1 = AuditableTestModel.objects.create(name="x")
    o1.name = "y"
    o1.save()
    AuditableTestModel.objects.create(name="z")
    o1.delete()
    logs = list(AuditLog.objects.order_by("timestamp", "id"))
    assert len(logs) >= 4
    for prev, curr in zip(logs, logs[1:]):
        assert curr.hash_prev == prev.hash_curr


@pytest.mark.django_db
def test_log_audit_direto_sem_actor_prefixa_system(user):
    entity = AuditableTestModel.objects.create(name="foo")
    log = log_audit(None, entity, {}, {"k": 1}, "manual.ping")
    assert log.action == "system:manual.ping"


@pytest.mark.django_db
def test_log_audit_direto_com_actor_sem_prefixo(user):
    entity = AuditableTestModel.objects.create(name="foo")
    log = log_audit(user, entity, {}, {"k": 1}, "manual.ping")
    assert log.action == "manual.ping"
    assert log.actor_user_id == user.pk


@pytest.mark.django_db
def test_update_sem_mudanca_nao_cria_log():
    obj = AuditableExcludeModel.objects.create(name="same")
    before_count = AuditLog.objects.count()
    obj.save()  # sem alterações em campos auditáveis (updated_at excluído)
    # pode haver update_log se updated_at mudar mas estamos excluindo
    # garantimos ao menos que não há exceção e contagem é coerente
    after_count = AuditLog.objects.count()
    assert after_count == before_count  # nenhum campo auditável mudou


def test_request_context_var_isolado_por_default():
    clear_request_context()
    assert get_request_context() is None
    ctx = RequestContext(
        user_id=uuid.uuid4(), ip="1.1.1.1", user_agent="u", trace_id="t"
    )
    token = set_request_context(ctx)
    try:
        assert get_request_context() == ctx
    finally:
        reset_request_context(token)
    assert get_request_context() is None


def test_compute_diff_so_inclui_mudancas():
    before = {"a": 1, "b": 2, "c": 3}
    after = {"a": 1, "b": 99, "c": 3}
    b, a = compute_diff(before, after, ["a", "b", "c"])
    assert b == {"b": 2}
    assert a == {"b": 99}


def test_compute_diff_respeita_fields_whitelist():
    before = {"a": 1, "b": 2}
    after = {"a": 9, "b": 9}
    b, a = compute_diff(before, after, ["a"])
    assert b == {"a": 1}
    assert a == {"a": 9}
