"""ServiceResult + DomainError — padrão Result para camada de serviço (ADR-008)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")


class DomainError(Exception):
    """Erro base de domínio com code + message + context opcional."""

    code: str = "DOMAIN_ERROR"

    def __init__(
        self,
        message: str,
        code: str | None = None,
        context: dict[str, object] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        if code is not None:
            self.code = code
        self.context: dict[str, object] = context or {}

    def __str__(self) -> str:
        return f"[{self.code}] {self.message}"


@dataclass(frozen=True)
class ServiceResult(Generic[T]):
    """Resultado de serviço: sucesso ou falha."""

    ok: bool
    value: T | None = None
    error: DomainError | None = None

    @classmethod
    def success(cls, value: T) -> ServiceResult[T]:
        return cls(ok=True, value=value, error=None)

    @classmethod
    def failure(cls, error: DomainError) -> ServiceResult[T]:
        return cls(ok=False, value=None, error=error)
