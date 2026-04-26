"""Fixtures globais do projeto gestao-vagas (Story 1.6 / 2.1)."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from django.core.cache import cache
from django.test import Client
from freezegun import freeze_time as _freeze_time

from apps.accounts.tests.factories import (
    GestorUserFactory,
    RhAdminUserFactory,
    UserFactory,
)


@pytest.fixture
def user(db):
    """User comum."""
    return UserFactory()


@pytest.fixture
def rh_admin(db):
    """RH admin (is_staff=True)."""
    return RhAdminUserFactory()


@pytest.fixture
def gestor_b(db):
    """Gestor tipo B com tomador."""
    return GestorUserFactory()


@pytest.fixture
def authenticated_client(db, user):
    """Django test client autenticado como `user`."""
    client = Client()
    client.force_login(user)
    return client


@pytest.fixture
def mock_ai_provider():
    """Mock com interface OCRProvider/LLMProvider."""
    provider = MagicMock()
    provider.extract_text.return_value = "texto extraído stub"
    provider.transcribe.return_value = "transcrição stub"
    provider.complete.return_value = "completion stub"
    provider.embed.return_value = [0.0] * 8
    return provider


@pytest.fixture
def freeze_time():
    """Wrapper sobre freezegun.freeze_time para uso em testes."""
    return _freeze_time


@pytest.fixture
def redis_mock():
    """Wrapper do cache Django (LocMem em test.py). Limpa entre testes."""
    cache.clear()
    yield cache
    cache.clear()
