"""Fixtures locais para testes de accounts."""

from __future__ import annotations

import pytest
from django.core.cache import cache
from django.template.context import BaseContext, Context


# Workaround bug Django 5.0 + Python 3.14: BaseContext.__copy__ via super() falha
# porque BaseContext não é subclasse de object no mesmo sentido esperado. Patch
# garante que a cópia funciona nos testes (signal template_rendered).
def _basecontext_copy(self):  # type: ignore[no-untyped-def]
    duplicate = BaseContext.__new__(type(self))
    duplicate.__dict__.update(self.__dict__)
    duplicate.dicts = self.dicts[:]
    return duplicate


BaseContext.__copy__ = _basecontext_copy  # type: ignore[attr-defined, method-assign]


def _context_copy(self):  # type: ignore[no-untyped-def]
    duplicate = _basecontext_copy(self)
    duplicate.request = getattr(self, "request", None)
    return duplicate


Context.__copy__ = _context_copy  # type: ignore[attr-defined, method-assign]


@pytest.fixture
def redis_mock():
    """Limpa o cache Django entre testes (LocMemCache em settings.test)."""
    cache.clear()
    yield cache
    cache.clear()
