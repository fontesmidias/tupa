"""Wrapper de alto nível sobre AuditLog.seal (Story 3.2)."""

from __future__ import annotations

from typing import Any

from django.db import transaction

from apps.audit.models import AuditLog


def log_audit(
    actor: Any | None,
    entity: Any,
    before: dict[str, Any],
    after: dict[str, Any],
    action: str,
    ip: str | None = None,
    user_agent: str = "",
) -> AuditLog:
    """Registra evento de auditoria de forma atômica.

    Se `actor` for None e a action ainda não estiver prefixada com `system:`,
    prefixa automaticamente para deixar claro que foi uma operação sistêmica.
    """
    if actor is None and not action.startswith("system:"):
        action = f"system:{action}"

    with transaction.atomic():
        return AuditLog.seal(
            actor=actor,
            entity=entity,
            before=before,
            after=after,
            action=action,
            ip=ip,
            user_agent=user_agent,
        )
