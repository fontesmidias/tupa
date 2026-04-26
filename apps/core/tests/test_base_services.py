"""Testes ServiceResult + DomainError."""

from __future__ import annotations

from apps.core.base_services import DomainError, ServiceResult


def test_service_result_success() -> None:
    r: ServiceResult[int] = ServiceResult.success(42)
    assert r.ok is True
    assert r.value == 42
    assert r.error is None


def test_service_result_failure() -> None:
    err = DomainError("boom")
    r: ServiceResult[int] = ServiceResult.failure(err)
    assert r.ok is False
    assert r.value is None
    assert r.error is err


def test_domain_error_default_code_and_context() -> None:
    err = DomainError("oops")
    assert err.code == "DOMAIN_ERROR"
    assert err.message == "oops"
    assert err.context == {}
    assert "DOMAIN_ERROR" in str(err)


def test_domain_error_override_code_and_context() -> None:
    err = DomainError("x", code="X", context={"k": "v"})
    assert err.code == "X"
    assert err.context == {"k": "v"}
