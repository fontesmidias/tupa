"""Bridge para apps fora de `policies` acessarem `PolicyAcceptance` sem violar
ADR-012. `policies` é camada 3; `accounts` (camada 2) precisa listar aceites
do titular no export LGPD, mas não pode importar upward.

Resolução lazy via `django.apps.apps.get_model` mantém grafo estático limpo.
"""

from __future__ import annotations

from typing import Any

from django.apps import apps as django_apps


def list_policy_acceptances(user_id: Any) -> list[dict[str, Any]]:
    """Lista aceites do titular ordenados por data (formato serializável)."""
    PolicyAcceptance = django_apps.get_model("policies", "PolicyAcceptance")
    qs = (
        PolicyAcceptance.objects.filter(user_id=user_id)
        .select_related("policy_version")
        .order_by("accepted_at")
    )
    out: list[dict[str, Any]] = []
    for acc in qs:
        out.append(
            {
                "id": str(acc.pk),
                "policy_kind": acc.policy_version.kind,
                "policy_version": acc.policy_version.version,
                "accepted_at": acc.accepted_at.isoformat(),
                "ip": acc.ip,
                "summary_shown_version": acc.summary_shown_version,
            }
        )
    return out
