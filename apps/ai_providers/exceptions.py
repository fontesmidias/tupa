"""Exceptions do app ai_providers. Epic 4 completo reaproveita."""

from __future__ import annotations


class ProviderError(Exception):
    """Erro genérico de provider IA."""


class ExtractionFailed(ProviderError):
    """Provider retornou, mas o resultado não é utilizável (schema, vazio, parse)."""


class ProviderUnavailable(ProviderError):
    """Provider indisponível — timeout, 5xx, rate-limit."""
