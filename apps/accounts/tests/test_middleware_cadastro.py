"""Testes Story 2.4 — CadastroCompletoMiddleware."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponse
from django.test import RequestFactory

from apps.accounts.middleware import CadastroCompletoMiddleware
from apps.accounts.tests.factories import GestorUserFactory, UserFactory


@pytest.fixture
def mw() -> CadastroCompletoMiddleware:
    return CadastroCompletoMiddleware(lambda r: HttpResponse("ok"))


def test_anon_skips(mw: CadastroCompletoMiddleware) -> None:
    request = RequestFactory().get("/gestor/")
    request.user = AnonymousUser()
    response = mw(request)
    assert response.status_code == 200
    assert response.content == b"ok"


@pytest.mark.django_db
def test_cadastro_completo_skips(mw: CadastroCompletoMiddleware) -> None:
    user = GestorUserFactory()
    assert user.is_cadastro_completo
    request = RequestFactory().get("/gestor/")
    request.user = user
    response = mw(request)
    assert response.status_code == 200


@pytest.mark.django_db
def test_bypass_path_skips(mw: CadastroCompletoMiddleware) -> None:
    user = UserFactory(nome="")
    assert not user.is_cadastro_completo
    request = RequestFactory().get("/gestor/requisicoes/nova/")
    request.user = user
    response = mw(request)
    assert response.status_code == 200
    assert response.content == b"ok"


@pytest.mark.django_db
def test_incompleto_redireciona(mw: CadastroCompletoMiddleware) -> None:
    user = UserFactory(nome="")
    assert not user.is_cadastro_completo
    request = RequestFactory().get("/gestor/?x=1")
    request.user = user
    response = mw(request)
    assert response.status_code == 302
    assert response["Location"].startswith("/auth/completar-perfil/?next=")
    assert "%2Fgestor%2F" in response["Location"]


@pytest.mark.django_db
def test_auth_prefix_bypass(mw: CadastroCompletoMiddleware) -> None:
    user = UserFactory(nome="")
    request = RequestFactory().get("/auth/completar-perfil/")
    request.user = user
    response = mw(request)
    assert response.status_code == 200


def test_user_none_skips(mw: CadastroCompletoMiddleware) -> None:
    request = MagicMock()
    request.user = None
    request.path = "/gestor/"
    response = mw(request)
    assert response.status_code == 200
