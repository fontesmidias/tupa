"""Views MFA TOTP — Story 2.5."""

from __future__ import annotations

import base64
import io

import qrcode
from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.core.cache import cache
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from apps.accounts.services.mfa import (
    activate_mfa,
    build_provisioning_uri,
    deactivate_mfa,
    enforce_mfa_required,
    generate_secret,
    verify_code,
)

User = get_user_model()

_SETUP_CACHE_TTL = 5 * 60
FAIL_MAX = 5
FAIL_WINDOW = 10 * 60
BLOCK_TTL = 15 * 60


def _setup_cache_key(user_id: str) -> str:
    return f"mfa:setup:{user_id}"


def _fail_key(user_id: str) -> str:
    return f"fail:mfa:{user_id}"


def _block_key(user_id: str) -> str:
    return f"block:mfa:{user_id}"


def _qr_base64(uri: str) -> str:
    img = qrcode.make(uri)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("ascii")


def _register_invalid(user_id: str) -> bool:
    key = _fail_key(user_id)
    cache.add(key, 0, FAIL_WINDOW)
    try:
        count = int(cache.incr(key))
    except ValueError:
        cache.set(key, 1, FAIL_WINDOW)
        count = 1
    if count >= FAIL_MAX:
        cache.set(_block_key(user_id), 1, BLOCK_TTL)
        cache.delete(key)
        return True
    return False


@require_http_methods(["GET", "POST"])
def mfa_setup_view(request: HttpRequest) -> HttpResponse:
    """Setup MFA — para rh_admin autenticado."""
    user = request.user
    if not user.is_authenticated:
        return redirect("/auth/entrar/")
    if not getattr(user, "is_rh", False):
        return JsonResponse(
            {"code": "FORBIDDEN", "message": "Apenas rh_admin"}, status=403
        )

    acao = request.GET.get("acao") or request.POST.get("acao") or ""
    reason = request.GET.get("reason") or ""

    if request.method == "GET":
        ctx = {
            "mfa_enabled": user.mfa_enabled,
            "reason": reason,
        }
        return render(request, "auth/mfa_setup.html", ctx)

    # POST
    if acao == "ativar":
        secret = generate_secret()
        cache.set(_setup_cache_key(str(user.id)), secret, _SETUP_CACHE_TTL)
        uri = build_provisioning_uri(secret, user.email)
        qr_b64 = _qr_base64(uri)
        return render(
            request,
            "auth/mfa_setup.html",
            {
                "mfa_enabled": user.mfa_enabled,
                "setup_mode": True,
                "qr_base64": qr_b64,
                "secret": secret,
                "provisioning_uri": uri,
            },
        )

    if acao == "confirmar_ativacao":
        secret = cache.get(_setup_cache_key(str(user.id)))
        code = request.POST.get("code", "")
        if not secret:
            messages.error(
                request, "Sessão de ativação expirou — recomece"
            )
            return redirect("/conta/seguranca/mfa/")
        result = activate_mfa(user, secret, code)
        if not result.ok:
            return render(
                request,
                "auth/mfa_setup.html",
                {
                    "mfa_enabled": False,
                    "setup_mode": True,
                    "qr_base64": _qr_base64(build_provisioning_uri(secret, user.email)),
                    "secret": secret,
                    "error": "código inválido",
                },
                status=200,
            )
        cache.delete(_setup_cache_key(str(user.id)))
        messages.success(request, "MFA ativado com sucesso")
        return redirect("/conta/seguranca/mfa/")

    if acao == "desativar":
        code = request.POST.get("code", "")
        result = deactivate_mfa(user, code)
        if not result.ok:
            return render(
                request,
                "auth/mfa_setup.html",
                {
                    "mfa_enabled": True,
                    "error": "código inválido",
                },
                status=200,
            )
        messages.success(request, "MFA desativado")
        return redirect("/conta/seguranca/mfa/")

    return JsonResponse({"code": "INVALID_ACAO", "message": "ação inválida"}, status=400)


@require_http_methods(["GET", "POST"])
def mfa_challenge_view(request: HttpRequest) -> HttpResponse:
    """Challenge MFA pós-magic-link."""
    pending_id = request.session.get("pending_mfa_user_id")
    if not pending_id:
        return redirect("/auth/entrar/")

    try:
        user = User.objects.get(pk=pending_id)
    except User.DoesNotExist:
        request.session.pop("pending_mfa_user_id", None)
        return redirect("/auth/entrar/")

    # Se usuário é rh_admin forçado por flag mas ainda não ativou, manda pro setup.
    if enforce_mfa_required(user, request) and not user.mfa_secret:
        # login parcial para acessar /conta/seguranca/mfa/
        login(request, user)
        request.session.pop("pending_mfa_user_id", None)
        messages.info(request, "MFA obrigatório — ative antes de continuar")
        return redirect("/conta/seguranca/mfa/?reason=required")

    if cache.get(_block_key(str(user.id))):
        return JsonResponse(
            {"code": "BLOCKED", "message": "Muitas tentativas. Aguarde 15 minutos."},
            status=429,
        )

    if request.method == "GET":
        return render(request, "auth/mfa_challenge.html", {})

    code = request.POST.get("code", "")
    secret = user.mfa_secret or ""
    if not verify_code(secret, code):
        blocked = _register_invalid(str(user.id))
        if blocked:
            return JsonResponse(
                {"code": "BLOCKED", "message": "Muitas tentativas. Aguarde 15 minutos."},
                status=429,
            )
        return render(
            request,
            "auth/mfa_challenge.html",
            {"error": "código inválido"},
            status=200,
        )

    cache.delete(_fail_key(str(user.id)))
    login(request, user)
    request.session.pop("pending_mfa_user_id", None)

    next_url = request.GET.get("next") or request.POST.get("next") or ""
    if next_url:
        return redirect(next_url)
    if getattr(user, "is_rh", False):
        return redirect("/rh/")
    return redirect("/gestor/")
