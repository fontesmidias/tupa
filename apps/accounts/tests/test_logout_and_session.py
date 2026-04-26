"""Story 2.6 — cookies seguros, logout, rotacao de sessao em mudanca de privilegio."""

from __future__ import annotations

import pytest
from django.conf import settings
from django.contrib.sessions.models import Session
from django.test import Client

from apps.accounts.tests.factories import UserFactory


@pytest.mark.django_db
def test_logout_post_destroi_sessao_e_redireciona() -> None:
    user = UserFactory()
    client = Client()
    client.force_login(user)
    assert client.session.session_key is not None

    response = client.post("/auth/sair/")
    assert response.status_code == 302
    assert response.url == "/auth/entrar/"
    # apos logout, client.session e' uma nova sessao anonima
    assert "_auth_user_id" not in client.session


@pytest.mark.django_db
def test_logout_get_nao_permitido() -> None:
    user = UserFactory()
    client = Client()
    client.force_login(user)

    response = client.get("/auth/sair/")
    assert response.status_code == 405


def test_session_cookie_settings_seguros() -> None:
    assert settings.SESSION_COOKIE_HTTPONLY is True
    assert settings.SESSION_COOKIE_SAMESITE == "Lax"
    assert settings.SESSION_COOKIE_AGE == 60 * 60 * 24 * 7
    assert settings.SESSION_SAVE_EVERY_REQUEST is True
    assert settings.CSRF_COOKIE_HTTPONLY is True
    assert settings.CSRF_COOKIE_SAMESITE == "Lax"


@pytest.mark.django_db
def test_mudanca_de_privilegio_invalida_sessao_do_user() -> None:
    user = UserFactory(is_staff=False)
    client = Client()
    client.force_login(user)
    session_key = client.session.session_key
    assert session_key is not None
    assert Session.objects.filter(session_key=session_key).exists()

    user.is_staff = True
    user.save()

    assert not Session.objects.filter(session_key=session_key).exists()


@pytest.mark.django_db
def test_save_sem_mudanca_de_privilegio_mantem_sessao() -> None:
    user = UserFactory(nome="Antes")
    client = Client()
    client.force_login(user)
    session_key = client.session.session_key
    assert session_key is not None

    user.nome = "Depois"
    user.save()

    assert Session.objects.filter(session_key=session_key).exists()
