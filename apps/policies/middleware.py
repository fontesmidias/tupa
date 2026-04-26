"""PolicyMiddleware — modal estilo Nubank (Story 3.5).

Intercepta rotas protegidas quando o usuário autenticado não aceitou as versões
vigentes de Termos/Privacidade. Renderiza modal com summary_of_changes_md.
"""

from __future__ import annotations

from typing import Callable

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from apps.policies.services import get_pending_versions

_BYPASS_PREFIXES = (
    "/auth/",
    "/webhooks/",
    "/politicas/",
    "/admin/",
    "/static/",
    "/media/",
)

_BYPASS_EXACT = (
    "/healthz",
    "/readyz",
    "/metrics",
)


class PolicyMiddleware:
    """Deve ser instalado APÓS AuthRequiredMiddleware."""

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def _is_bypass(self, path: str) -> bool:
        for prefix in _BYPASS_PREFIXES:
            if path.startswith(prefix):
                return True
        return path in _BYPASS_EXACT

    def __call__(self, request: HttpRequest) -> HttpResponse:
        user = getattr(request, "user", None)
        if user is None or getattr(user, "is_anonymous", True):
            return self.get_response(request)
        if self._is_bypass(request.path):
            return self.get_response(request)

        pending = get_pending_versions(user)
        if not pending:
            return self.get_response(request)

        return render(
            request,
            "policies/modal.html",
            {"pending": pending, "next": request.get_full_path()},
            status=200,
        )
