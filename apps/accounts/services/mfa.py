"""Serviço MFA TOTP — Story 2.5.

Fluxo:
- activate_mfa: valida código + persiste secret criptografado + mfa_enabled=True.
- deactivate_mfa: valida código atual + limpa secret + mfa_enabled=False.
- enforce_mfa_required: True se flag require_mfa_for_rh ativa + is_staff + !mfa_enabled.
"""

from __future__ import annotations

from typing import Any

import pyotp
import structlog
import waffle

from apps.accounts.models import User
from apps.core.base_services import DomainError, ServiceResult

logger: Any = structlog.get_logger(__name__)

TOTP_ISSUER = "gestao-vagas"


def generate_secret() -> str:
    """Gera novo TOTP secret base32."""
    return pyotp.random_base32()


def build_provisioning_uri(secret: str, email: str) -> str:
    """Monta otpauth:// URI para QR."""
    return pyotp.totp.TOTP(secret).provisioning_uri(
        name=email, issuer_name=TOTP_ISSUER
    )


def verify_code(secret: str, code: str) -> bool:
    """Valida código TOTP (janela ±1 período por padrão do pyotp)."""
    if not secret or not code or not code.isdigit() or len(code) != 6:
        return False
    return pyotp.TOTP(secret).verify(code, valid_window=1)


def activate_mfa(user: User, secret: str, code: str) -> ServiceResult[None]:
    """Ativa MFA se código bate com secret fornecido."""
    if not verify_code(secret, code):
        return ServiceResult.failure(
            DomainError(message="código TOTP inválido", code="MFA_INVALID_CODE")
        )
    user.mfa_secret = secret
    user.mfa_enabled = True
    user.save(update_fields=["mfa_secret", "mfa_enabled"])
    logger.info("mfa.enabled", user_id=str(user.id))
    return ServiceResult.success(None)


def deactivate_mfa(user: User, code: str) -> ServiceResult[None]:
    """Desativa MFA se código TOTP atual bate."""
    secret = user.mfa_secret or ""
    if not user.mfa_enabled or not verify_code(secret, code):
        return ServiceResult.failure(
            DomainError(message="código TOTP inválido", code="MFA_INVALID_CODE")
        )
    user.mfa_secret = None
    user.mfa_enabled = False
    user.save(update_fields=["mfa_secret", "mfa_enabled"])
    logger.info("mfa.disabled", user_id=str(user.id))
    return ServiceResult.success(None)


def enforce_mfa_required(user: User, request: Any = None) -> bool:
    """True se flag require_mfa_for_rh ativa + is_staff + !mfa_enabled."""
    if not getattr(user, "is_rh", False):
        return False
    if getattr(user, "mfa_enabled", False):
        return False
    if request is not None:
        try:
            return bool(waffle.flag_is_active(request, "require_mfa_for_rh"))
        except Exception:
            pass
    # Sem request: consulta direta do estado da flag (everyone).
    try:
        flag = waffle.models.Flag.objects.filter(name="require_mfa_for_rh").first()
    except Exception:
        return False
    if flag is None:
        return False
    return bool(flag.everyone)
