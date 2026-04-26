"""Decorators de autorização por role — Story 2.7.

`@require_role('rh_admin')` e `@require_role_any('rh_admin', 'rh_operator')`
aplicam-se a function-based views. Anônimo → 401; role insuficiente → 403.
Resposta JSON se `Accept: application/json`; caso contrário HTML/plain.
"""

from __future__ import annotations

from functools import wraps
from typing import Callable

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.template import TemplateDoesNotExist
from django.template.loader import render_to_string

ViewFn = Callable[..., HttpResponse]


def _wants_json(request: HttpRequest) -> bool:
    accept = request.META.get("HTTP_ACCEPT", "") or ""
    return "application/json" in accept.lower()


def _forbidden(request: HttpRequest, message: str = "Acesso negado") -> HttpResponse:
    if _wants_json(request):
        return JsonResponse({"code": "FORBIDDEN", "message": message}, status=403)
    try:
        html = render_to_string("errors/403.html", {"message": message}, request=request)
        return HttpResponse(html, status=403)
    except TemplateDoesNotExist:
        return HttpResponse("403 Forbidden", status=403, content_type="text/plain")


def _unauthorized(request: HttpRequest) -> HttpResponse:
    if _wants_json(request):
        return JsonResponse(
            {"code": "UNAUTHORIZED", "message": "Autenticação requerida"},
            status=401,
        )
    return HttpResponse("401 Unauthorized", status=401, content_type="text/plain")


def require_role(role: str) -> Callable[[ViewFn], ViewFn]:
    """Permite apenas usuários cujo `role` seja exatamente `role`."""

    def decorator(view: ViewFn) -> ViewFn:
        @wraps(view)
        def wrapped(request: HttpRequest, *args: object, **kwargs: object) -> HttpResponse:
            user = getattr(request, "user", None)
            if user is None or getattr(user, "is_anonymous", True):
                return _unauthorized(request)
            if getattr(user, "role", None) != role:
                return _forbidden(request, f"Requer papel {role}")
            return view(request, *args, **kwargs)

        return wrapped

    return decorator


def require_role_any(*roles: str) -> Callable[[ViewFn], ViewFn]:
    """Permite usuários cujo `role` esteja em `roles`."""

    allowed = set(roles)

    def decorator(view: ViewFn) -> ViewFn:
        @wraps(view)
        def wrapped(request: HttpRequest, *args: object, **kwargs: object) -> HttpResponse:
            user = getattr(request, "user", None)
            if user is None or getattr(user, "is_anonymous", True):
                return _unauthorized(request)
            if getattr(user, "role", None) not in allowed:
                return _forbidden(
                    request, f"Requer um dos papéis: {', '.join(sorted(allowed))}"
                )
            return view(request, *args, **kwargs)

        return wrapped

    return decorator
