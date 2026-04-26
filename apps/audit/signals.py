"""Signals genéricos post_save/post_delete para AuditableMixin (Story 3.2)."""

from __future__ import annotations

import logging
from typing import Any

from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from apps.audit.services import log_audit
from apps.audit.utils import _to_json_safe
from apps.core.base_models import AuditableMixin
from apps.core.request_context import get_request_context

logger = logging.getLogger("audit")


def _is_auditable(instance: Any) -> bool:
    return isinstance(instance, AuditableMixin)


def _snapshot(instance: Any) -> dict[str, Any]:
    """Extrai snapshot dict de todos os campos concretos do model."""
    data: dict[str, Any] = {}
    for field in instance._meta.concrete_fields:
        data[field.name] = _to_json_safe(getattr(instance, field.attname, None))
    return data


def _filter_fields(sender: type[Any], snapshot: dict[str, Any]) -> dict[str, Any]:
    # Hints ficam como atributos de classe (Django valida Meta estritamente).
    allowed_list: list[str] | None = getattr(sender, "auditable_fields", None)
    exclude_list: list[str] = list(getattr(sender, "auditable_exclude", []) or [])

    result = dict(snapshot)
    if allowed_list is not None:
        allowed_set = set(allowed_list)
        result = {k: v for k, v in result.items() if k in allowed_set}
    for key in exclude_list:
        result.pop(key, None)
    return result


def _resolve_actor_ctx() -> tuple[Any, str | None, str]:
    """Resolve (actor, ip, ua). actor é o user_id (UUID) ou None."""
    ctx = get_request_context()
    if ctx is None:
        return None, None, ""
    return ctx.user_id, ctx.ip, ctx.user_agent


class _ActorProxy:
    """Proxy mínimo p/ AuditLog.seal que só precisa de .pk."""

    def __init__(self, pk: Any) -> None:
        self.pk = pk


@receiver(pre_save)
def _audit_pre_save(sender: type[Any], instance: Any, **_: Any) -> None:
    if not _is_auditable(instance):
        return
    if not instance.pk:
        instance._audit_before = {}
        return
    try:
        old = sender.objects.filter(pk=instance.pk).first()
        if old is None:
            instance._audit_before = {}
        else:
            instance._audit_before = _filter_fields(sender, _snapshot(old))
    except Exception:  # noqa: BLE001 — tolerante
        logger.exception("audit.pre_save snapshot falhou para %s", sender.__name__)
        instance._audit_before = {}


@receiver(post_save)
def _audit_post_save(
    sender: type[Any], instance: Any, created: bool, **_: Any
) -> None:
    if not _is_auditable(instance):
        return
    try:
        after_full = _filter_fields(sender, _snapshot(instance))
        if created:
            before: dict[str, Any] = {}
            after: dict[str, Any] = after_full
            action = "created"
        else:
            before_full = getattr(instance, "_audit_before", {}) or {}
            from apps.audit.utils import compute_diff

            before, after = compute_diff(before_full, after_full, list(after_full.keys()))
            if not before and not after:
                return  # nada mudou em campos auditáveis
            action = "updated"

        actor_pk, ip, ua = _resolve_actor_ctx()
        actor = _ActorProxy(actor_pk) if actor_pk is not None else None
        log_audit(actor, instance, before, after, action, ip=ip, user_agent=ua)
    except Exception:  # noqa: BLE001 — nunca derruba op principal
        logger.exception("audit.post_save falhou para %s", sender.__name__)


@receiver(post_delete)
def _audit_post_delete(sender: type[Any], instance: Any, **_: Any) -> None:
    if not _is_auditable(instance):
        return
    try:
        before = _filter_fields(sender, _snapshot(instance))
        actor_pk, ip, ua = _resolve_actor_ctx()
        actor = _ActorProxy(actor_pk) if actor_pk is not None else None
        log_audit(actor, instance, before, {}, "deleted", ip=ip, user_agent=ua)
    except Exception:  # noqa: BLE001
        logger.exception("audit.post_delete falhou para %s", sender.__name__)
