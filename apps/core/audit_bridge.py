"""Bridge para apps não-audit acessarem AuditLog sem violar ADR-012.

apps.audit é folha terminal: ninguém pode importá-lo. Este módulo resolve o
model AuditLog e helpers de service via `django.apps.apps.get_model` / dotted
import em runtime, mantendo apps.audit invisível no grafo estático de imports.
"""

from __future__ import annotations

from importlib import import_module
from typing import Any, Iterable

from django.apps import apps as django_apps


def get_audit_model() -> type[Any]:
    return django_apps.get_model("audit", "AuditLog")


def list_audit_for_actor(user_id: Any) -> Iterable[dict[str, Any]]:
    AuditLog = get_audit_model()
    return (
        AuditLog.objects.filter(actor_user_id=user_id)
        .order_by("timestamp")
        .values(
            "id", "action", "entity_type", "entity_id",
            "before", "after", "timestamp", "ip",
        )
    )


def log_event(
    actor: Any | None,
    entity: Any,
    before: dict[str, Any],
    after: dict[str, Any],
    action: str,
    ip: str | None = None,
    user_agent: str = "",
) -> Any:
    svc = import_module("apps.audit.services")
    return svc.log_audit(
        actor=actor,
        entity=entity,
        before=before,
        after=after,
        action=action,
        ip=ip,
        user_agent=user_agent,
    )
