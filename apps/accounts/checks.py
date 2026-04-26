"""Django system checks — LGPD/compliance gate (Party Mode — Mary).

Registra avisos/erros em `manage.py check --deploy` para impedir prod sem
configuração crítica.
"""

from __future__ import annotations

from typing import Any

from django.conf import settings
from django.core.checks import Error, Warning, register


@register(deploy=True)
def dpo_email_required(app_configs: Any, **kwargs: Any) -> list[Any]:
    """DPO_EMAIL obrigatório em produção — sem ele, notificações LGPD silenciam."""
    errors: list[Any] = []
    dpo = getattr(settings, "DPO_EMAIL", "") or ""
    if not dpo:
        errors.append(
            Error(
                "DPO_EMAIL não configurado.",
                hint=(
                    "Defina DPO_EMAIL no ambiente. Sem ele, ações LGPD críticas "
                    "(anonimização, revogação de consentimento) são registradas "
                    "como `dpo.notify.skipped` — inaceitável em produção."
                ),
                id="accounts.E001",
            )
        )
    return errors


@register(deploy=True)
def field_encryption_key_required(app_configs: Any, **kwargs: Any) -> list[Any]:
    """FIELD_ENCRYPTION_KEY obrigatória em produção."""
    errors: list[Any] = []
    key = getattr(settings, "FIELD_ENCRYPTION_KEY", "") or ""
    if not key:
        errors.append(
            Error(
                "FIELD_ENCRYPTION_KEY não configurada.",
                hint="Gere com: python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\"",
                id="accounts.E002",
            )
        )
    return errors
