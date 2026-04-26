"""Testes Story 2.4 — complete_profile_view."""

from __future__ import annotations

import pytest
from django.test import Client

from apps.accounts.tests.factories import TomadorFactory, UserFactory


@pytest.mark.django_db
def test_get_preenche_tomador_por_dominio() -> None:
    tomador = TomadorFactory(dominio_email="greenhousedf.com.br")
    user = UserFactory(email="novo@greenhousedf.com.br", nome="", tipo_gestor=None, tomador=None)
    client = Client()
    client.force_login(user)
    response = client.get("/auth/completar-perfil/")
    assert response.status_code == 200
    form = response.context["form"]
    assert form.initial.get("tipo_gestor") == "A"
    assert form.initial.get("tomador") == tomador.pk


@pytest.mark.django_db
def test_get_preenche_tipo_gestor_gov() -> None:
    user = UserFactory(email="user@algo.gov.br", nome="", tipo_gestor=None, tomador=None)
    client = Client()
    client.force_login(user)
    response = client.get("/auth/completar-perfil/")
    form = response.context["form"]
    assert form.initial.get("tipo_gestor") == "B"


@pytest.mark.django_db
def test_post_salva_e_redireciona_next() -> None:
    tomador = TomadorFactory()
    user = UserFactory(email="user@algo.gov.br", nome="", tipo_gestor=None, tomador=None)
    client = Client()
    client.force_login(user)
    response = client.post(
        "/auth/completar-perfil/?next=/gestor/",
        {
            "nome": "Fulano",
            "tipo_gestor": "B",
            "tomador": str(tomador.pk),
            "next": "/gestor/",
        },
    )
    assert response.status_code == 302
    assert response["Location"] == "/gestor/"
    user.refresh_from_db()
    assert user.is_cadastro_completo
    assert user.nome == "Fulano"
    assert user.tipo_gestor == "B"
    assert user.tomador_id == tomador.pk


@pytest.mark.django_db
def test_post_fallback_rh_is_staff() -> None:
    tomador = TomadorFactory()
    user = UserFactory(email="rh@greenhousedf.com.br", nome="", tipo_gestor=None, tomador=None, is_staff=True, role="rh_admin")
    client = Client()
    client.force_login(user)
    response = client.post(
        "/auth/completar-perfil/",
        {"nome": "RH", "tipo_gestor": "A", "tomador": str(tomador.pk)},
    )
    assert response.status_code == 302
    assert response["Location"] == "/rh/"


@pytest.mark.django_db
def test_post_skip_nao_salva() -> None:
    user = UserFactory(email="x@outro.com", nome="", tipo_gestor=None, tomador=None)
    client = Client()
    client.force_login(user)
    response = client.post("/auth/completar-perfil/?skip=1", {"skip": "1"})
    assert response.status_code == 302
    user.refresh_from_db()
    assert not user.is_cadastro_completo


@pytest.mark.django_db
def test_post_invalido_rerender() -> None:
    user = UserFactory(email="x@outro.com", nome="", tipo_gestor=None, tomador=None)
    client = Client()
    client.force_login(user)
    response = client.post(
        "/auth/completar-perfil/",
        {"nome": "", "tipo_gestor": "", "tomador": ""},
    )
    assert response.status_code == 200
    assert response.context["form"].errors
