"""Exceções de domínio (ADR-008)."""

from __future__ import annotations

from apps.core.base_services import DomainError


class DomainValidationError(DomainError):
    code = "DOMAIN_VALIDATION"


class ProviderUnavailable(DomainError):
    code = "PROVIDER_UNAVAILABLE"


class ExtractionFailed(DomainError):
    code = "EXTRACTION_FAILED"


class DuplicateDetected(DomainError):
    code = "DUPLICATE_DETECTED"


class ConsentRequired(DomainError):
    code = "CONSENT_REQUIRED"
