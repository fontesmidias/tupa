"""Serviço de link mágico — Story 2.2.

Regras:
- Código 6 dígitos via ``secrets.randbelow(1_000_000)``.
- Hash SHA-256 armazenado em ``code_hash``.
- Expira em 15 minutos.
- Rate-limit: 5 requisições por (IP, email_lower) em 10 minutos via cache Django.
- Criação do MagicLink é desacoplada da existência do User (cadastro progressivo).
- Resposta NUNCA revela se o email existe (responsabilidade da view).
"""

from __future__ import annotations

import hashlib
import secrets
from dataclasses import dataclass
from datetime import timedelta
from typing import Any

import structlog
from django.core.cache import cache
from django.core.mail import send_mail
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.accounts.models import MagicLink
from apps.core.base_services import DomainError, ServiceResult

logger: Any = structlog.get_logger(__name__)

MAGIC_LINK_TTL = timedelta(minutes=15)
RATE_LIMIT_MAX = 5
RATE_LIMIT_WINDOW_SECONDS = 10 * 60


@dataclass(frozen=True)
class MagicLinkRequest:
    """Input do serviço."""

    email: str
    ip: str
    user_agent: str


class RateLimitedError(DomainError):
    """Excesso de solicitações para o par (IP, email)."""

    code = "RATE_LIMITED"


class InvalidEmailError(DomainError):
    """Email com formato inválido."""

    code = "INVALID_EMAIL"


def _generate_code() -> str:
    return f"{secrets.randbelow(1_000_000):06d}"


def _hash_code(code: str) -> str:
    return hashlib.sha256(code.encode("utf-8")).hexdigest()


def _mask_email(email: str) -> str:
    local, _, domain = email.partition("@")
    prefix = local[:2]
    return f"{prefix}***@{domain}" if domain else f"{prefix}***"


def _ua_hash(user_agent: str) -> str:
    return hashlib.sha256(user_agent.encode("utf-8")).hexdigest()[:16]


def _rate_limit_key(ip: str, email: str) -> str:
    return f"rl:magiclink:{ip}:{email.lower()}"


def _check_and_increment_rate_limit(ip: str, email: str) -> bool:
    """Retorna True se dentro do limite; False se excedeu. Incremento atômico."""
    key = _rate_limit_key(ip, email)
    # ``add`` só grava se a chave não existe; define TTL na criação.
    cache.add(key, 0, RATE_LIMIT_WINDOW_SECONDS)
    try:
        count = int(cache.incr(key))
    except ValueError:
        # Race condition: chave expirou entre add e incr — recomeça.
        cache.set(key, 1, RATE_LIMIT_WINDOW_SECONDS)
        count = 1
    return count <= RATE_LIMIT_MAX


def request_magic_link(
    email: str, ip: str, user_agent: str
) -> ServiceResult[MagicLink]:
    """Solicita código de link mágico para o email informado."""
    normalized = (email or "").strip().lower()
    try:
        validate_email(normalized)
    except ValidationError:
        return ServiceResult.failure(InvalidEmailError("Email inválido."))

    ip_key = ip or "unknown"
    if not _check_and_increment_rate_limit(ip_key, normalized):
        return ServiceResult.failure(
            RateLimitedError(
                "Muitas tentativas, tente novamente em alguns minutos.",
                context={"retry_after": RATE_LIMIT_WINDOW_SECONDS},
            )
        )

    code = _generate_code()
    magic_link = MagicLink.objects.create(
        email=normalized,
        code_hash=_hash_code(code),
        ip=ip if ip else None,
        user_agent=(user_agent or "")[:512],
        expires_at=timezone.now() + MAGIC_LINK_TTL,
    )

    send_mail(
        subject="Seu código gestao-vagas",
        message=f"Seu código é: {code} (expira em 15 minutos)",
        from_email=None,
        recipient_list=[normalized],
        fail_silently=False,
    )

    logger.info(
        "auth.magic_link_requested",
        email_masked=_mask_email(normalized),
        ip=ip_key,
        ua_hash=_ua_hash(user_agent or ""),
        created_magic_link_id=str(magic_link.id),
    )
    return ServiceResult.success(magic_link)
