"""Middlewares de accounts — Story 2.4 (cadastro) + Story 2.5 (MFA)."""

from __future__ import annotations

from typing import Callable
from urllib.parse import urlencode

from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect

from apps.accounts.services.mfa import enforce_mfa_required

_DEFAULT_BYPASS_PROFILE_PATHS = [
    "/auth/",
    "/admin/",
    "/static/",
    "/media/",
    "/healthz",
    "/readyz",
    "/metrics",
    # Story 5.2 adiciona view real desta rota
    "/gestor/requisicoes/nova/",
]

_PREFIX_BYPASS = ("/auth/", "/admin/", "/static/", "/media/")


class CadastroCompletoMiddleware:
    """Redireciona usuários autenticados sem cadastro completo para /auth/completar-perfil/.

    Deve ser instalado APÓS AuthRequiredMiddleware.
    """

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def _is_bypass(self, path: str) -> bool:
        bypass = getattr(settings, "BYPASS_PROFILE_PATHS", _DEFAULT_BYPASS_PROFILE_PATHS)
        for entry in bypass:
            if entry in _PREFIX_BYPASS:
                if path.startswith(entry):
                    return True
            elif path == entry:
                return True
        return False

    def __call__(self, request: HttpRequest) -> HttpResponse:
        user = getattr(request, "user", None)
        if user is None or getattr(user, "is_anonymous", True):
            return self.get_response(request)
        if getattr(user, "is_cadastro_completo", False):
            return self.get_response(request)
        if self._is_bypass(request.path):
            return self.get_response(request)

        query = urlencode({"next": request.get_full_path()})
        return redirect(f"/auth/completar-perfil/?{query}")


_MFA_BYPASS_PATHS = (
    "/auth/",
    "/admin/",
    "/static/",
    "/media/",
    "/conta/seguranca/mfa/",
    "/healthz",
    "/readyz",
    "/metrics",
)


class MfaRequiredMiddleware:
    """Força MFA para rh_admin quando flag require_mfa_for_rh está ativa.

    Deve ser instalado APÓS CadastroCompletoMiddleware.
    """

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def _is_bypass(self, path: str) -> bool:
        for entry in _MFA_BYPASS_PATHS:
            if entry.endswith("/"):
                if path.startswith(entry):
                    return True
            elif path == entry:
                return True
        return False

    def __call__(self, request: HttpRequest) -> HttpResponse:
        user = getattr(request, "user", None)
        if user is None or getattr(user, "is_anonymous", True):
            return self.get_response(request)
        if not getattr(user, "is_rh", False):
            return self.get_response(request)
        if getattr(user, "mfa_enabled", False):
            return self.get_response(request)
        if self._is_bypass(request.path):
            return self.get_response(request)
        if not enforce_mfa_required(user, request):
            return self.get_response(request)
        return redirect("/conta/seguranca/mfa/?reason=required")
