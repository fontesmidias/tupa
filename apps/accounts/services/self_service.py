"""Serviços LGPD de auto-atendimento do titular — Stories 3.6a e 3.6b."""

from __future__ import annotations

import hashlib
import io
import json
import secrets
import zipfile
from datetime import timedelta
from typing import Any
from uuid import UUID

from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction
from django.utils import timezone

from apps.accounts.models import MagicLink, User
from apps.core.audit_bridge import list_audit_for_actor, log_event

REAUTH_CODE_TTL = timedelta(minutes=15)


def _user_dados_dict(user: User) -> dict[str, Any]:
    return {
        "id": str(user.pk),
        "email": user.email,
        "nome": user.nome,
        "role": user.role,
        "tipo_gestor": user.tipo_gestor,
        "tomador_id": str(user.tomador_id) if user.tomador_id else None,
        "circulo_id": str(user.circulo_id) if user.circulo_id else None,
        "date_joined": user.date_joined.isoformat() if user.date_joined else None,
        "mfa_enabled": user.mfa_enabled,
        "cpf": user.cpf or "",
        "opt_in_marketing": user.opt_in_marketing,
        "opt_in_analytics": user.opt_in_analytics,
        "anonimizado_em": (
            user.anonimizado_em.isoformat() if user.anonimizado_em else None
        ),
    }


def _audit_list(user: User) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in list_audit_for_actor(user.pk):
        row["id"] = str(row["id"])
        row["timestamp"] = row["timestamp"].isoformat()
        out.append(row)
    return out


def _legal_basis_dict() -> dict[str, Any]:
    """Retorna mapa campo → base legal (LGPD Art. 9º — direito à informação)."""
    from apps.core.legal_basis import USER_FIELD_LEGAL_BASIS

    return {
        "fields": {
            name: {
                "base_legal": str(meta["base_legal"]),
                "finalidade": meta["finalidade"],
            }
            for name, meta in USER_FIELD_LEGAL_BASIS.items()
        },
        "fonte": "apps.core.legal_basis (data-as-code)",
    }


def _policy_acceptances_list(user: User) -> list[dict[str, Any]]:
    """Lista aceites de políticas do titular via bridge (ADR-012 — Party Mode)."""
    from apps.core.policy_bridge import list_policy_acceptances

    return list_policy_acceptances(user.pk)


def build_user_export_zip(user: User) -> bytes:
    """Gera ZIP in-memory com dados pessoais + audit + base legal + aceites.

    LGPD Arts. 9º (informação sobre tratamento) + 18 V (portabilidade) + 19.
    Inclui `legal_basis.json` e `policy_acceptances.json` (Party Mode — Mary).
    """
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(
            "dados.json",
            json.dumps(_user_dados_dict(user), ensure_ascii=False, indent=2),
        )
        zf.writestr(
            "audit.json",
            json.dumps(_audit_list(user), ensure_ascii=False, indent=2),
        )
        zf.writestr(
            "legal_basis.json",
            json.dumps(_legal_basis_dict(), ensure_ascii=False, indent=2),
        )
        zf.writestr(
            "policy_acceptances.json",
            json.dumps(
                _policy_acceptances_list(user), ensure_ascii=False, indent=2
            ),
        )
        zf.writestr(
            "README.txt",
            (
                "Export LGPD — gestao-vagas\n"
                f"Gerado em: {timezone.now().isoformat()}\n"
                "Contém:\n"
                "  - dados.json: dados pessoais do titular\n"
                "  - audit.json: histórico de ações auditadas\n"
                "  - legal_basis.json: base legal por campo (LGPD Art. 9º)\n"
                "  - policy_acceptances.json: aceites de políticas versionadas\n"
                "Binários (CVs, áudios) serão incluídos quando disponíveis.\n"
            ),
        )
    return buf.getvalue()


def corrigir_user_nome(user: User, novo_nome: str, ip: str | None, user_agent: str) -> User:
    """Atualiza `nome` e dispara AuditLog explícito (Story 3.2)."""
    antigo = user.nome
    novo = (novo_nome or "").strip()
    if not novo:
        raise ValueError("nome não pode ser vazio")
    if novo == antigo:
        return user
    user.nome = novo
    user.save(update_fields=["nome"])
    log_event(
        actor=user,
        entity=user,
        before={"nome": antigo},
        after={"nome": novo},
        action="user.self_corrected",
        ip=ip,
        user_agent=user_agent,
    )
    return user


# --- Story 3.6b — anonimização e revogação de opt-ins ---------------------


def _hash_code(code: str) -> str:
    return hashlib.sha256(code.encode("utf-8")).hexdigest()


def issue_reauth_code(user: User, ip: str | None, user_agent: str) -> MagicLink:
    """Emite código dedicado de reauth (purpose=REAUTH_ANONYMIZE).

    Isola do escopo de login (Story 2.2): este link NÃO autentica sessão.
    """
    code = f"{secrets.randbelow(1_000_000):06d}"
    ml = MagicLink.objects.create(
        email=user.email.lower(),
        code_hash=_hash_code(code),
        purpose=MagicLink.Purpose.REAUTH_ANONYMIZE,
        ip=ip if ip else None,
        user_agent=(user_agent or "")[:512],
        expires_at=timezone.now() + REAUTH_CODE_TTL,
    )
    send_mail(
        subject="Código de confirmação — anonimização de conta",
        message=(
            f"Código de confirmação para anonimização: {code}\n"
            "Válido por 15 minutos. Se você não solicitou, ignore este email.\n"
        ),
        from_email=None,
        recipient_list=[user.email],
        fail_silently=False,
    )
    return ml


def verify_reauth_code(user: User, code: str) -> bool:
    """Valida código de reauth (escopo REAUTH_ANONYMIZE) e marca como usado."""
    if not code or not code.isdigit() or len(code) != 6:
        return False
    ml = (
        MagicLink.objects.filter(
            email=user.email.lower(),
            used_at__isnull=True,
            code_hash=_hash_code(code),
            purpose=MagicLink.Purpose.REAUTH_ANONYMIZE,
        )
        .order_by("-created_at")
        .first()
    )
    if ml is None or ml.expires_at < timezone.now():
        return False
    ml.used_at = timezone.now()
    ml.save(update_fields=["used_at", "updated_at"])
    return True


def _anon_hash(user_pk: Any) -> str:
    """Hash determinístico por usuário; inclui SECRET_KEY para não-reversibilidade."""
    secret = getattr(settings, "SECRET_KEY", "") or ""
    raw = f"{secret}:{user_pk}".encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:32]


def _notify_dpo(action: str, user: User, ip: str | None = None) -> None:
    """Envia email ao DPO; registra tentativa (sucesso ou falha) no audit chain.

    Mary (Party Mode): `fail_silently=True` + DPO_EMAIL vazio formava buraco
    negro de compliance. Agora qualquer falha de notificação fica auditada.
    """
    dpo = getattr(settings, "DPO_EMAIL", "") or ""
    if not dpo:
        log_event(
            actor=None,
            entity=user,
            before={},
            after={"action": action, "reason": "DPO_EMAIL não configurado"},
            action="dpo.notify.skipped",
            ip=ip,
            user_agent="",
        )
        return
    try:
        send_mail(
            subject=f"[LGPD] {action} — user {user.pk}",
            message=(
                f"Ação LGPD crítica: {action}\n"
                f"user_id: {user.pk}\n"
                f"timestamp: {timezone.now().isoformat()}\n"
            ),
            from_email=None,
            recipient_list=[dpo],
            fail_silently=False,
        )
    except Exception as exc:  # noqa: BLE001
        log_event(
            actor=None,
            entity=user,
            before={},
            after={"action": action, "error": str(exc)[:200]},
            action="dpo.notify.failed",
            ip=ip,
            user_agent="",
        )


def _pii_digest(value: str | None) -> str:
    """Digest SHA-256 truncado — prova de valor antigo sem persistir plaintext.

    Amelia (Party Mode): `user.anonymized` logava email/nome em claro no
    `before`, atacando o direito ao esquecimento. Agora o audit registra
    apenas o digest — auditor vê "algo mudou" sem ler PII.
    """
    if not value:
        return ""
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]


def anonymize_user(
    user: User, ip: str | None = None, user_agent: str = ""
) -> User:
    """Anonimiza PII do titular preservando `id` e hash-chain (LGPD Art. 18).

    Idempotência sob concorrência: usa `select_for_update` para evitar race
    entre duas requisições simultâneas (Amelia — Party Mode).
    PII não é persistida em claro no audit — apenas digest (Amelia).
    """
    with transaction.atomic():
        locked = User.objects.select_for_update().filter(pk=user.pk).first()
        if locked is None:
            return user
        user = locked

        if user.anonimizado_em is not None:
            log_event(
                actor=user,
                entity=user,
                before={},
                after={"noop": True},
                action="user.anonymize.noop",
                ip=ip,
                user_agent=user_agent,
            )
            return user

        h = _anon_hash(user.pk)
        before = {
            "nome_digest": _pii_digest(user.nome),
            "email_digest": _pii_digest(user.email),
            "cpf_set": bool(user.cpf),
            "opt_in_marketing": user.opt_in_marketing,
            "opt_in_analytics": user.opt_in_analytics,
            "mfa_enabled": user.mfa_enabled,
            "is_active": user.is_active,
        }

        user.nome = f"Usuário anonimizado {h[:8]}"
        user.email = f"anon-{h}@anonimizado.local"
        user.cpf = None
        user.opt_in_marketing = False
        user.opt_in_analytics = False
        user.mfa_enabled = False
        user.mfa_secret = None
        user.is_active = False
        user.anonimizado_em = timezone.now()
        user.save(
            update_fields=[
                "nome",
                "email",
                "cpf",
                "opt_in_marketing",
                "opt_in_analytics",
                "mfa_enabled",
                "mfa_secret",
                "is_active",
                "anonimizado_em",
            ]
        )
        after = {
            "nome_digest": _pii_digest(user.nome),
            "email_digest": _pii_digest(user.email),
            "cpf_set": False,
            "opt_in_marketing": False,
            "opt_in_analytics": False,
            "mfa_enabled": False,
            "is_active": False,
            "anonimizado_em": user.anonimizado_em.isoformat(),
        }
        log_event(
            actor=user,
            entity=user,
            before=before,
            after=after,
            action="user.anonymized",
            ip=ip,
            user_agent=user_agent,
        )

    _notify_dpo("user.anonymized", user, ip=ip)
    return user


def revoke_consent(
    user: User,
    marketing: bool = False,
    analytics: bool = False,
    ip: str | None = None,
    user_agent: str = "",
) -> User:
    """Desativa flags de opt-in sem deletar conta (LGPD Art. 8 §5)."""
    before = {
        "opt_in_marketing": user.opt_in_marketing,
        "opt_in_analytics": user.opt_in_analytics,
    }
    changed = False
    if marketing and user.opt_in_marketing:
        user.opt_in_marketing = False
        changed = True
    if analytics and user.opt_in_analytics:
        user.opt_in_analytics = False
        changed = True

    if not changed:
        return user

    user.save(update_fields=["opt_in_marketing", "opt_in_analytics"])
    after = {
        "opt_in_marketing": user.opt_in_marketing,
        "opt_in_analytics": user.opt_in_analytics,
    }
    log_event(
        actor=user,
        entity=user,
        before=before,
        after=after,
        action="consent.revoked",
        ip=ip,
        user_agent=user_agent,
    )
    _notify_dpo("consent.revoked", user, ip=ip)
    return user
