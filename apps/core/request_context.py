"""Context var para propagar dados da request a signals/jobs (Story 3.2).

Uso `contextvars` (thread-safe + asyncio-safe) — nunca `threading.local`.
Em testes e jobs async o context fica vazio e signals devem tolerar ausência.
"""

from __future__ import annotations

from contextvars import ContextVar, Token
from dataclasses import dataclass
from typing import Optional
from uuid import UUID


@dataclass(frozen=True)
class RequestContext:
    """Snapshot imutável de dados da HTTP request em curso."""

    user_id: UUID | None
    ip: str | None
    user_agent: str
    trace_id: str | None


_request_context: ContextVar[Optional[RequestContext]] = ContextVar(
    "request_context", default=None
)


def get_request_context() -> RequestContext | None:
    """Retorna o contexto ativo ou None."""
    return _request_context.get()


def set_request_context(ctx: RequestContext) -> Token[Optional[RequestContext]]:
    """Injeta contexto, retornando Token para reset posterior."""
    return _request_context.set(ctx)


def reset_request_context(token: Token[Optional[RequestContext]]) -> None:
    """Restaura valor anterior do ContextVar."""
    _request_context.reset(token)


def clear_request_context() -> None:
    """Helper para testes: zera o context."""
    _request_context.set(None)
