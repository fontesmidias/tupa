"""Views do app policies (Story 3.5)."""

from __future__ import annotations

from django.contrib import messages
from django.contrib.auth import logout
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from apps.policies.models import PolicyAcceptance, PolicyVersion
from apps.policies.services import get_pending_versions


@require_http_methods(["GET"])
def policy_full_text_view(
    request: HttpRequest, kind: str, version: str
) -> HttpResponse:
    pv = get_object_or_404(PolicyVersion, kind=kind, version=version)
    return render(request, "policies/full_text.html", {"policy": pv})


@require_http_methods(["POST"])
def policy_accept_view(request: HttpRequest) -> HttpResponse:
    user = getattr(request, "user", None)
    if user is None or user.is_anonymous:
        return redirect("/auth/entrar/")
    pending = get_pending_versions(user)
    ip = request.META.get("REMOTE_ADDR")
    ua = request.META.get("HTTP_USER_AGENT", "")
    for pv in pending:
        PolicyAcceptance.objects.create(
            user=user,
            policy_version=pv,
            ip=ip,
            user_agent=ua,
            summary_shown_version=pv.version,
        )
    next_url = request.POST.get("next") or "/"
    if not next_url.startswith("/"):
        next_url = "/"
    return redirect(next_url)


@require_http_methods(["POST"])
def policy_reject_view(request: HttpRequest) -> HttpResponse:
    logout(request)
    messages.info(
        request,
        "Para acessar a plataforma é necessário aceitar os Termos e a Política de Privacidade.",
    )
    return redirect("/auth/entrar/")
