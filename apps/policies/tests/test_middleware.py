"""Testes do PolicyMiddleware + views (Story 3.5)."""

from __future__ import annotations

import pytest
from django.test import Client
from django.utils import timezone

from apps.accounts.models import Tomador, User
from apps.policies.models import PolicyAcceptance, PolicyKind, PolicyVersion


@pytest.fixture
def user(db):
    tomador = Tomador.objects.create(nome="T", dominio_email="x.com")
    return User.objects.create_user(
        email="u@x.com",
        password="x",
        nome="Fulano",
        tipo_gestor=User.TipoGestor.A,
        tomador=tomador,
    )


@pytest.fixture
def terms_v1(db):
    return PolicyVersion.objects.create(
        kind=PolicyKind.TERMS,
        version="1.0.0",
        effective_at=timezone.now(),
        full_text_md="# Termos v1",
        summary_of_changes_md="inicial",
    )


@pytest.fixture
def privacy_v1(db):
    return PolicyVersion.objects.create(
        kind=PolicyKind.PRIVACY,
        version="1.0.0",
        effective_at=timezone.now(),
        full_text_md="# Privacidade v1",
        summary_of_changes_md="inicial",
    )


@pytest.fixture
def client_logged(user):
    c = Client()
    c.force_login(user)
    return c


def _accept_all(user):
    for pv in PolicyVersion.objects.all():
        PolicyAcceptance.objects.create(user=user, policy_version=pv)


@pytest.mark.django_db
def test_anonimo_nao_ve_modal(terms_v1, privacy_v1):
    # AuthRequiredMiddleware bloqueia antes; PolicyMiddleware nem sequer avalia.
    resp = Client().get("/rh/")
    assert b"Atualiza" not in resp.content
    assert b"/politicas/aceitar/" not in resp.content


@pytest.mark.django_db
def test_bypass_paths_nao_interceptados(client_logged, terms_v1, privacy_v1):
    # /politicas/ deve bypassar PolicyMiddleware
    resp = client_logged.get("/politicas/terms/v1.0.0/")
    assert resp.status_code == 200
    assert b"Termos v1" in resp.content


@pytest.mark.django_db
def test_usuario_com_pendente_ve_modal(client_logged, terms_v1, privacy_v1):
    resp = client_logged.get("/rh/")
    assert resp.status_code == 200
    assert b"Atualiza" in resp.content
    assert b"Aceitar" in resp.content
    assert b"/politicas/aceitar/" in resp.content


@pytest.mark.django_db
def test_usuario_ja_aceitou_passa(client_logged, user, terms_v1, privacy_v1):
    _accept_all(user)
    resp = client_logged.get("/rh/")
    # /rh/ pode exigir is_rh ou retornar algo; o importante é NÃO ser o modal
    assert b"/politicas/aceitar/" not in resp.content


@pytest.mark.django_db
def test_aceitar_cria_policyacceptance_e_redireciona(
    client_logged, user, terms_v1, privacy_v1
):
    resp = client_logged.post("/politicas/aceitar/", {"next": "/rh/"})
    assert resp.status_code in (301, 302)
    assert resp["Location"] == "/rh/"
    assert PolicyAcceptance.objects.filter(user=user).count() == 2


@pytest.mark.django_db
def test_aceitar_next_externo_vira_root(client_logged, terms_v1, privacy_v1):
    resp = client_logged.post(
        "/politicas/aceitar/", {"next": "http://evil.com/x"}
    )
    assert resp["Location"] == "/"


@pytest.mark.django_db
def test_recusar_desloga_e_redireciona(client_logged, user, terms_v1, privacy_v1):
    resp = client_logged.post("/politicas/recusar/")
    assert resp.status_code in (301, 302)
    assert "/auth/entrar/" in resp["Location"]
    # sessão limpa — próxima request deve ser bloqueada por AuthRequiredMiddleware
    resp2 = client_logged.get("/rh/")
    assert resp2.status_code in (301, 302, 401, 403)


@pytest.mark.django_db
def test_full_text_404_versao_inexistente(client_logged, terms_v1):
    resp = client_logged.get("/politicas/terms/v9.9.9/")
    assert resp.status_code == 404


@pytest.mark.django_db
def test_aceite_apenas_de_pendentes(client_logged, user, terms_v1, privacy_v1):
    # Já aceitou terms; apenas privacy é pendente
    PolicyAcceptance.objects.create(user=user, policy_version=terms_v1)
    client_logged.post("/politicas/aceitar/", {"next": "/rh/"})
    assert (
        PolicyAcceptance.objects.filter(user=user, policy_version=terms_v1).count()
        == 1
    )
    assert PolicyAcceptance.objects.filter(
        user=user, policy_version=privacy_v1
    ).exists()
