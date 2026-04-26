"""Serviços do app policies (Story 3.5)."""

from __future__ import annotations

from django.db.models import Max
from django.utils import timezone

from apps.policies.models import PolicyAcceptance, PolicyKind, PolicyVersion


def get_current_versions() -> dict[str, PolicyVersion]:
    """Retorna a PolicyVersion vigente (maior effective_at <= now) por kind."""
    now = timezone.now()
    result: dict[str, PolicyVersion] = {}
    for kind, _label in PolicyKind.choices:
        pv = (
            PolicyVersion.objects.filter(kind=kind, effective_at__lte=now)
            .order_by("-effective_at")
            .first()
        )
        if pv is not None:
            result[kind] = pv
    return result


def get_pending_versions(user) -> list[PolicyVersion]:
    """Retorna versões vigentes que o usuário ainda não aceitou."""
    current = get_current_versions()
    if not current:
        return []
    accepted_ids = set(
        PolicyAcceptance.objects.filter(
            user=user, policy_version_id__in=[pv.id for pv in current.values()]
        ).values_list("policy_version_id", flat=True)
    )
    return [pv for pv in current.values() if pv.id not in accepted_ids]
