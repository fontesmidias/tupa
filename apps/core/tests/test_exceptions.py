"""Testes exceptions."""

from __future__ import annotations

import pytest

from apps.core.base_services import DomainError
from apps.core.exceptions import (
    ConsentRequired,
    DomainValidationError,
    DuplicateDetected,
    ExtractionFailed,
    ProviderUnavailable,
)


@pytest.mark.parametrize(
    "cls, expected_code",
    [
        (DomainValidationError, "DOMAIN_VALIDATION"),
        (ProviderUnavailable, "PROVIDER_UNAVAILABLE"),
        (ExtractionFailed, "EXTRACTION_FAILED"),
        (DuplicateDetected, "DUPLICATE_DETECTED"),
        (ConsentRequired, "CONSENT_REQUIRED"),
    ],
)
def test_exception_has_correct_code_and_inherits_domain_error(
    cls: type[DomainError], expected_code: str
) -> None:
    err = cls("msg")
    assert isinstance(err, DomainError)
    assert err.code == expected_code
    assert err.message == "msg"
