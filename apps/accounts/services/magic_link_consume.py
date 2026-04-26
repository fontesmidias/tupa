"""Serviço de consumo de link mágico — Story 2.3.

Fluxo:
- Localiza MagicLink mais recente (por email, não usado, não expirado) com code_hash batendo.
- Valida expiração; valida contexto (IP /24 + UA hash SHA-256).
- Contexto divergente: gera NOVO MagicLink + envia email; não consome o original.
- Código errado: incrementa contador de falhas; bloqueia após 5 em 10min.
"""

from __future__ import annotations

import hashlib
import ipaddress
import secrets
from dataclasses import dataclass
from datetime import timedelta
from typing import Any, Literal

import structlog
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.mail import send_mail
from django.utils import timezone

from apps.accounts.models import MagicLink

logger: Any = structlog.get_logger(__name__)

User = get_user_model()

MAGIC_LINK_TTL = timedelta(minutes=15)
FAIL_MAX = 5
FAIL_WINDOW = 10 * 60  # 10min
BLOCK_TTL = 15 * 60  # 15min


ConsumeStatus = Literal[
    "ok", "expired", "invalid", "context_mismatch", "blocked", "mfa_required"
]


@dataclass(frozen=True)
class ConsumeResult:
    status: ConsumeStatus
    user: Any = None
    redirect_url: str | None = None
    new_magic_link_id: str | None = None


def _hash_code(code: str) -> str:
    return hashlib.sha256(code.encode("utf-8")).hexdigest()


def _ua_hash_full(user_agent: str) -> str:
    return hashlib.sha256((user_agent or "").encode("utf-8")).hexdigest()


def _mask_email(email: str) -> str:
    local, _, domain = email.partition("@")
    prefix = local[:2]
    return f"{prefix}***@{domain}" if domain else f"{prefix}***"


def _fail_key(ip: str, email: str) -> str:
    return f"fail:magiclink:{ip}:{email.lower()}"


def _block_key(ip: str, email: str) -> str:
    return f"block:magiclink:{ip}:{email.lower()}"


def _is_blocked(ip: str, email: str) -> bool:
    return cache.get(_block_key(ip, email)) is not None


def _register_invalid(ip: str, email: str) -> bool:
    """Incrementa contador de erros; retorna True se atingiu bloqueio."""
    key = _fail_key(ip, email)
    cache.add(key, 0, FAIL_WINDOW)
    try:
        count = int(cache.incr(key))
    except ValueError:
        cache.set(key, 1, FAIL_WINDOW)
        count = 1
    if count >= FAIL_MAX:
        cache.set(_block_key(ip, email), 1, BLOCK_TTL)
        cache.delete(key)
        return True
    return False


def _ip_net24(ip: str | None) -> str | None:
    if not ip:
        return None
    try:
        return str(ipaddress.ip_network(f"{ip}/24", strict=False).network_address)
    except (ValueError, TypeError):
        return None


def _context_matches(ml: MagicLink, ip: str, user_agent: str) -> bool:
    ip_sol = _ip_net24(ml.ip or "")
    ip_con = _ip_net24(ip or "")
    if ip_sol is not None and ip_con is not None and ip_sol != ip_con:
        return False
    ua_sol = _ua_hash_full(ml.user_agent or "")
    ua_con = _ua_hash_full(user_agent or "")
    if ua_sol != ua_con:
        return False
    return True


def _generate_code() -> str:
    return f"{secrets.randbelow(1_000_000):06d}"


def _resolve_redirect(user: Any) -> str:
    if not user.is_cadastro_completo:
        return "/auth/completar-perfil/"
    if getattr(user, "is_rh", False):
        return "/rh/"
    return "/gestor/"


def _get_or_create_user(email: str) -> Any:
    existing = User.objects.filter(email__iexact=email).first()
    if existing is not None:
        return existing
    return User.objects.create_user(email=email)


def consume_magic_link(
    email: str, code: str, ip: str, user_agent: str
) -> ConsumeResult:
    email_norm = (email or "").strip().lower()
    ip_key = ip or "unknown"

    if _is_blocked(ip_key, email_norm):
        return ConsumeResult(status="blocked")

    if not email_norm or not code or not code.isdigit() or len(code) != 6:
        if _register_invalid(ip_key, email_norm):
            return ConsumeResult(status="blocked")
        return ConsumeResult(status="invalid")

    code_hash = _hash_code(code)
    now = timezone.now()

    # MagicLink mais recente não usado com hash correspondente, ESCOPO LOGIN.
    # Story 3.6b — links de reauth (purpose != login) NÃO autenticam.
    ml = (
        MagicLink.objects.filter(
            email=email_norm,
            used_at__isnull=True,
            code_hash=code_hash,
            purpose=MagicLink.Purpose.LOGIN,
        )
        .order_by("-created_at")
        .first()
    )

    if ml is None:
        if _register_invalid(ip_key, email_norm):
            return ConsumeResult(status="blocked")
        return ConsumeResult(status="invalid")

    if ml.expires_at < now:
        return ConsumeResult(status="expired")

    # Valida contexto
    if not _context_matches(ml, ip, user_agent):
        new_code = _generate_code()
        new_ml = MagicLink.objects.create(
            email=email_norm,
            code_hash=_hash_code(new_code),
            ip=ip if ip else None,
            user_agent=(user_agent or "")[:512],
            expires_at=now + MAGIC_LINK_TTL,
        )
        send_mail(
            subject="Novo código gestao-vagas",
            message=(
                "Detectamos um novo dispositivo/rede. "
                f"Seu novo código é: {new_code}"
            ),
            from_email=None,
            recipient_list=[email_norm],
            fail_silently=False,
        )
        logger.info(
            "auth.magic_link_context_mismatch",
            email_masked=_mask_email(email_norm),
            ip_sol=ml.ip or "",
            ip_con=ip or "",
            ua_hash_sol=_ua_hash_full(ml.user_agent or ""),
            ua_hash_con=_ua_hash_full(user_agent or ""),
        )
        return ConsumeResult(
            status="context_mismatch",
            new_magic_link_id=str(new_ml.id),
        )

    # Consome
    ml.used_at = now
    ml.save(update_fields=["used_at", "updated_at"])
    # Limpa contador de falhas desse par
    cache.delete(_fail_key(ip_key, email_norm))

    user = _get_or_create_user(email_norm)

    # Story 2.5 — Se MFA habilitado ou forçado por flag, exige challenge antes de login.
    from apps.accounts.services.mfa import enforce_mfa_required

    if user.mfa_enabled or enforce_mfa_required(user):
        logger.info(
            "auth.magic_link_consumed_mfa_required",
            email_masked=_mask_email(email_norm),
            user_id=str(user.id),
        )
        return ConsumeResult(
            status="mfa_required", user=user, redirect_url="/auth/mfa/"
        )

    redirect_url = _resolve_redirect(user)

    logger.info(
        "auth.magic_link_consumed",
        email_masked=_mask_email(email_norm),
        user_id=str(user.id),
        redirect=redirect_url,
    )
    return ConsumeResult(status="ok", user=user, redirect_url=redirect_url)
