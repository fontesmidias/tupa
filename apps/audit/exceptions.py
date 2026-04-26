"""Exceções do app audit."""

from __future__ import annotations

from apps.core.base_services import DomainError


class AuditAppendOnlyError(DomainError):
    """AuditLog é append-only: updates/deletes são proibidos."""

    code = "AUDIT_APPEND_ONLY"
