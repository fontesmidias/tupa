"""Views de autenticação — Stories 2.2 e 2.3."""

from __future__ import annotations

from urllib.parse import urlencode

from django.contrib import messages
from django.contrib.auth import login, logout
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from apps.accounts.forms import (
    CompleteProfileForm,
    MagicLinkConsumeForm,
    MagicLinkRequestForm,
)
from apps.accounts.services.magic_link import (
    RATE_LIMIT_WINDOW_SECONDS,
    request_magic_link,
)
from apps.accounts.services.magic_link_consume import consume_magic_link

GENERIC_MESSAGE = "Se o email estiver cadastrado, enviaremos um código."


def _client_ip(request: HttpRequest) -> str:
    xff: str = request.META.get("HTTP_X_FORWARDED_FOR", "") or ""
    if xff:
        return xff.split(",")[0].strip()
    remote: str = request.META.get("REMOTE_ADDR", "") or ""
    return remote


@require_http_methods(["GET", "POST"])
def signin_view(request: HttpRequest) -> HttpResponse:
    """GET renderiza form; POST solicita link mágico."""
    if request.method == "GET":
        form = MagicLinkRequestForm()
        return render(request, "auth/entrar.html", {"form": form})

    form = MagicLinkRequestForm(request.POST)
    if not form.is_valid():
        return render(
            request,
            "auth/entrar.html",
            {"form": form, "generic_message": GENERIC_MESSAGE},
            status=200,
        )

    email = form.cleaned_data["email"]
    ip = _client_ip(request)
    ua = request.META.get("HTTP_USER_AGENT", "")
    result = request_magic_link(email=email, ip=ip, user_agent=ua)

    if not result.ok and result.error is not None and result.error.code == "RATE_LIMITED":
        response = JsonResponse(
            {"code": "RATE_LIMITED", "message": result.error.message},
            status=429,
        )
        response["Retry-After"] = str(RATE_LIMIT_WINDOW_SECONDS)
        return response

    query = urlencode({"email": email})
    return redirect(f"/auth/codigo/?{query}")


@require_http_methods(["GET", "POST"])
def consume_code_view(request: HttpRequest) -> HttpResponse:
    """GET renderiza form; POST consome o código."""
    if request.method == "GET":
        email = request.GET.get("email", "")
        form = MagicLinkConsumeForm(initial={"email": email})
        return render(request, "auth/codigo.html", {"form": form, "email": email})

    form = MagicLinkConsumeForm(request.POST)
    email = request.POST.get("email", "")
    if not form.is_valid():
        return render(
            request,
            "auth/codigo.html",
            {"form": form, "email": email, "error": "código inválido"},
            status=200,
        )

    ip = _client_ip(request)
    ua = request.META.get("HTTP_USER_AGENT", "")
    result = consume_magic_link(
        email=form.cleaned_data["email"],
        code=form.cleaned_data["code"],
        ip=ip,
        user_agent=ua,
    )

    if result.status == "blocked":
        return JsonResponse(
            {
                "code": "BLOCKED",
                "message": "Muitas tentativas erradas. Aguarde 15 minutos.",
            },
            status=429,
        )

    if result.status == "expired":
        return render(
            request,
            "auth/codigo.html",
            {"form": form, "email": email, "error": "código expirado"},
            status=200,
        )

    if result.status == "invalid":
        return render(
            request,
            "auth/codigo.html",
            {"form": form, "email": email, "error": "código inválido"},
            status=200,
        )

    if result.status == "context_mismatch":
        new_form = MagicLinkConsumeForm(initial={"email": email})
        return render(
            request,
            "auth/codigo.html",
            {
                "form": new_form,
                "email": email,
                "info": "Novo código enviado — use o que acabou de chegar",
            },
            status=200,
        )

    if result.status == "mfa_required":
        assert result.user is not None
        request.session["pending_mfa_user_id"] = str(result.user.id)
        return redirect(result.redirect_url or "/auth/mfa/")

    # status == "ok"
    assert result.user is not None and result.redirect_url is not None
    login(request, result.user)
    messages.success(request, "Bem-vindo!")
    return redirect(result.redirect_url)


def _fallback_redirect(request: HttpRequest) -> str:
    user = request.user
    if getattr(user, "is_rh", False):
        return "/rh/"
    return "/gestor/"


@require_http_methods(["GET", "POST"])
def complete_profile_view(request: HttpRequest) -> HttpResponse:
    """Cadastro progressivo valor-primeiro — Story 2.4."""
    user = request.user
    if not user.is_authenticated:
        return redirect("/auth/entrar/")

    next_url = request.GET.get("next") or request.POST.get("next") or ""

    if request.method == "POST":
        if request.GET.get("skip") == "1" or request.POST.get("skip") == "1":
            return redirect(next_url or _fallback_redirect(request))

        form = CompleteProfileForm(request.POST, user=user)
        if form.is_valid():
            form.save()
            return redirect(next_url or _fallback_redirect(request))
        return render(
            request,
            "auth/completar_perfil.html",
            {"form": form, "next": next_url},
            status=200,
        )

    form = CompleteProfileForm(user=user)
    return render(
        request,
        "auth/completar_perfil.html",
        {"form": form, "next": next_url},
    )


@require_http_methods(["GET"])
def rh_home_view(request: HttpRequest) -> HttpResponse:
    """Placeholder home RH."""
    return HttpResponse("home RH")


@require_http_methods(["GET"])
def gestor_home_view(request: HttpRequest) -> HttpResponse:
    """Placeholder home gestor."""
    return HttpResponse("home gestor")


@require_http_methods(["POST"])
def logout_view(request: HttpRequest) -> HttpResponse:
    """Logout explicito — Story 2.6. Destroi sessao e redireciona para /auth/entrar/."""
    logout(request)
    messages.success(request, "Sessao encerrada.")
    return redirect("/auth/entrar/")
