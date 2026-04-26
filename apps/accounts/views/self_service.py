"""Views LGPD de auto-atendimento do titular — Stories 3.6a e 3.6b."""

from __future__ import annotations

import mimetypes
from pathlib import Path
from typing import Any

from django.conf import settings  # noqa: F401 — usado em runtime
from django.contrib import messages
from django.contrib.auth import logout
from django.http import FileResponse, Http404, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from apps.accounts.models import UserDataExport
from apps.accounts.services.mfa import verify_code as verify_mfa_code
from apps.accounts.services.self_service import (
    _audit_list,
    _user_dados_dict,
    anonymize_user,
    corrigir_user_nome,
    issue_reauth_code,
    revoke_consent,
    verify_reauth_code,
)
from apps.accounts.views.auth import _client_ip


def _require_login(request: HttpRequest) -> HttpResponse | None:
    user = getattr(request, "user", None)
    if user is None or user.is_anonymous:
        return redirect("/auth/entrar/")
    return None


@require_http_methods(["GET"])
def meus_dados_view(request: HttpRequest) -> HttpResponse:
    resp = _require_login(request)
    if resp is not None:
        return resp
    exports = (
        UserDataExport.objects.filter(user=request.user)
        .order_by("-created_at")[:10]
    )
    ctx: dict[str, Any] = {
        "dados": _user_dados_dict(request.user),
        "audit": _audit_list(request.user),
        "exports": exports,
    }
    return render(request, "accounts/meus_dados.html", ctx)


@require_http_methods(["POST"])
def meus_dados_corrigir_view(request: HttpRequest) -> HttpResponse:
    resp = _require_login(request)
    if resp is not None:
        return resp
    novo_nome = request.POST.get("nome", "").strip()
    try:
        corrigir_user_nome(
            request.user,
            novo_nome,
            ip=_client_ip(request),
            user_agent=request.META.get("HTTP_USER_AGENT", "")[:500],
        )
        messages.success(request, "Dados atualizados.")
    except ValueError as exc:
        messages.error(request, str(exc))
    return redirect("/conta/meus-dados/")


@require_http_methods(["POST"])
def meus_dados_exportar_view(request: HttpRequest) -> HttpResponse:
    resp = _require_login(request)
    if resp is not None:
        return resp
    from apps.accounts.tasks import generate_user_data_export

    export = UserDataExport.objects.create(user=request.user)
    if getattr(settings, "DRAMATIQ_EAGER", False):
        generate_user_data_export.fn(str(export.pk))
    else:
        try:
            generate_user_data_export.send(str(export.pk))
        except Exception:  # noqa: BLE001 — fallback síncrono se broker offline (dev)
            generate_user_data_export.fn(str(export.pk))
    messages.info(
        request,
        "Exportação solicitada. O arquivo aparecerá aqui quando estiver pronto.",
    )
    return redirect("/conta/meus-dados/")


@require_http_methods(["GET", "POST"])
def meus_dados_anonimizar_view(request: HttpRequest) -> HttpResponse:
    """Anonimização com reauth dedicada.

    Fluxo (Amelia/Party Mode — AC 3.6b: dupla reauth):
    - MFA ativo: exige CÓDIGO TOTP + CÓDIGO emitido por email (scope reauth).
    - MFA ausente: exige CÓDIGO emitido por email (scope reauth).
    - Códigos de reauth têm `purpose=REAUTH_ANONYMIZE` e NÃO autenticam sessão.
    """
    resp = _require_login(request)
    if resp is not None:
        return resp
    user = request.user

    ctx: dict[str, Any] = {
        "mfa_enabled": bool(getattr(user, "mfa_enabled", False)),
        "anonimizado_em": user.anonimizado_em,
        "email_masked": _mask_email(user.email),
    }

    if user.anonimizado_em is not None:
        return render(request, "accounts/anonimizar.html", ctx)

    if request.method == "GET":
        return render(request, "accounts/anonimizar.html", ctx)

    acao = request.POST.get("acao", "")
    ip = _client_ip(request)
    ua = request.META.get("HTTP_USER_AGENT", "")[:500]

    if acao == "send_link":
        issue_reauth_code(user, ip=ip, user_agent=ua)
        messages.info(
            request,
            "Enviamos um código de confirmação para o seu email.",
        )
        ctx["link_sent"] = True
        return render(request, "accounts/anonimizar.html", ctx)

    if acao == "confirm":
        email_code = request.POST.get("email_code", "").strip()
        totp_code = request.POST.get("totp_code", "").strip()

        ok_email = verify_reauth_code(user, email_code)
        if ctx["mfa_enabled"]:
            ok_totp = verify_mfa_code(user.mfa_secret or "", totp_code)
            ok = ok_email and ok_totp
        else:
            ok = ok_email

        if not ok:
            ctx["error"] = (
                "código(s) inválido(s) ou expirado(s) — solicite um novo código"
            )
            return render(request, "accounts/anonimizar.html", ctx, status=200)

        anonymize_user(user, ip=ip, user_agent=ua)
        logout(request)
        messages.success(
            request,
            "Conta anonimizada. Para acessar é necessário um novo cadastro.",
        )
        return redirect("/auth/entrar/")

    return redirect("/conta/meus-dados/anonimizar/")


@require_http_methods(["POST"])
def meus_dados_revogar_view(request: HttpRequest) -> HttpResponse:
    resp = _require_login(request)
    if resp is not None:
        return resp
    marketing = request.POST.get("marketing") == "1"
    analytics = request.POST.get("analytics") == "1"
    revoke_consent(
        request.user,
        marketing=marketing,
        analytics=analytics,
        ip=_client_ip(request),
        user_agent=request.META.get("HTTP_USER_AGENT", "")[:500],
    )
    messages.success(request, "Consentimentos atualizados.")
    return redirect("/conta/meus-dados/")


def _mask_email(email: str) -> str:
    local, _, domain = email.partition("@")
    prefix = local[:2]
    return f"{prefix}***@{domain}" if domain else f"{prefix}***"


@require_http_methods(["GET"])
def meus_dados_download_view(
    request: HttpRequest, export_id: str
) -> HttpResponse:
    resp = _require_login(request)
    if resp is not None:
        return resp
    export = get_object_or_404(UserDataExport, pk=export_id, user=request.user)
    if export.status != UserDataExport.Status.READY or not export.file_path:
        raise Http404("Export indisponível")
    full = Path(settings.MEDIA_ROOT) / export.file_path
    if not full.exists():
        raise Http404("Arquivo ausente")
    content_type, _ = mimetypes.guess_type(full.name)
    return FileResponse(
        full.open("rb"),
        as_attachment=True,
        filename=full.name,
        content_type=content_type or "application/zip",
    )
