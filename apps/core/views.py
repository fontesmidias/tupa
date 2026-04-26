"""Views do app core — alicerce da Camada 1 (ADR-012)."""

from django.http import HttpRequest, HttpResponse


def hello(request: HttpRequest) -> HttpResponse:
    """AC#4 Story 1.1 — smoke view."""
    return HttpResponse("Hello, gestao-vagas")
