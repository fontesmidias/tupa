"""Exceções do app policies."""

from __future__ import annotations

from apps.core.base_services import DomainError


class PolicyAcceptanceAppendOnlyError(DomainError):
    """PolicyAcceptance é append-only: updates/deletes são proibidos."""

    code = "POLICY_ACCEPTANCE_APPEND_ONLY"
