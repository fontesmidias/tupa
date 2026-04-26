"""Middlewares: TraceId, DomainException, AuthRequired (Story 1.5b)."""

from __future__ import annotations

import uuid
from typing import Callable

from django.conf import settings
from django.http import HttpRequest, HttpResponse, JsonResponse

from apps.core.base_services import DomainError
from apps.core.request_context import (
    RequestContext,
    reset_request_context,
    set_request_context,
)
from apps.core.exceptions import (
    ConsentRequired,
    DomainValidationError,
    DuplicateDetected,
    ExtractionFailed,
    ProviderUnavailable,
)

_DEFAULT_PUBLIC_PATHS = [
    "/",
    "/auth/",
    "/healthz",
    "/readyz",
    "/metrics",
    "/admin/login/",
    "/static/",
    "/media/",
]

_STATUS_MAP: dict[type[DomainError], int] = {
    DomainValidationError: 400,
    ProviderUnavailable: 503,
    ExtractionFailed: 422,
    DuplicateDetected: 409,
    ConsentRequired: 403,
}


def _is_valid_trace_id(value: str) -> bool:
    try:
        uuid.UUID(value)
        return True
    except (ValueError, AttributeError):
        return False


class TraceIdMiddleware:
    """Gera/reusa UUID4 em request.trace_id e injeta em X-Trace-Id."""

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        incoming = request.headers.get("X-Trace-Id", "")
        trace_id = incoming if _is_valid_trace_id(incoming) else str(uuid.uuid4())
        request.trace_id = trace_id  # type: ignore[attr-defined]
        response = self.get_response(request)
        response["X-Trace-Id"] = trace_id
        return response


class DomainExceptionMiddleware:
    """Converte DomainError em JSON response com status apropriado."""

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        return self.get_response(request)

    def process_exception(self, request: HttpRequest, exception: Exception) -> HttpResponse | None:
        if not isinstance(exception, DomainError):
            return None
        status = 500
        for exc_type, code in _STATUS_MAP.items():
            if isinstance(exception, exc_type):
                status = code
                break
        trace_id = getattr(request, "trace_id", None)
        payload = {
            "code": exception.code,
            "message": exception.message,
            "trace_id": trace_id,
        }
        response = JsonResponse(payload, status=status)
        if trace_id:
            response["X-Trace-Id"] = trace_id
        return response


class RequestContextMiddleware:
    """Popula ContextVar com user/ip/ua/trace_id para consumo por signals (Story 3.2).

    Deve ficar IMEDIATAMENTE após AuthenticationMiddleware (precisa request.user)
    e ANTES de AuthRequiredMiddleware.
    """

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def _client_ip(self, request: HttpRequest) -> str | None:
        xff = str(request.META.get("HTTP_X_FORWARDED_FOR", "") or "")
        if xff:
            return xff.split(",")[0].strip()
        remote = request.META.get("REMOTE_ADDR")
        if not remote:
            return None
        return str(remote)

    def __call__(self, request: HttpRequest) -> HttpResponse:
        user = getattr(request, "user", None)
        user_id = None
        if user is not None and getattr(user, "is_authenticated", False):
            user_id = getattr(user, "pk", None)
        ctx = RequestContext(
            user_id=user_id,
            ip=self._client_ip(request),
            user_agent=request.META.get("HTTP_USER_AGENT", "") or "",
            trace_id=getattr(request, "trace_id", None),
        )
        token = set_request_context(ctx)
        try:
            return self.get_response(request)
        finally:
            reset_request_context(token)


class AuthRequiredMiddleware:
    """Skeleton: bloqueia request anônimo fora de PUBLIC_PATHS com 401 JSON."""

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def _is_public(self, path: str) -> bool:
        public = getattr(settings, "PUBLIC_PATHS", _DEFAULT_PUBLIC_PATHS)
        for pub in public:
            # "/" casa apenas exatamente; demais prefixos com "/" casam path que comece por eles.
            if pub == "/":
                if path == "/":
                    return True
            elif pub.endswith("/"):
                if path == pub or path.startswith(pub):
                    return True
            elif path == pub:
                return True
        return False

    def __call__(self, request: HttpRequest) -> HttpResponse:
        user = getattr(request, "user", None)
        is_anon = user is None or getattr(user, "is_anonymous", True)
        if is_anon and not self._is_public(request.path):
            trace_id = getattr(request, "trace_id", None)
            return JsonResponse(
                {
                    "code": "AUTH_REQUIRED",
                    "message": "Autenticação requerida.",
                    "trace_id": trace_id,
                },
                status=401,
            )
        return self.get_response(request)
