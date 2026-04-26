"""Testes do service promote_to_vaga + transições da Vaga."""

from __future__ import annotations

import pytest
from django.template import base as template_base

from apps.accounts.models import Tomador, User
from apps.core.exceptions import DomainValidationError
from apps.requisitions.models import Requisicao
from apps.vagas.models import Vaga
from apps.vagas.services import promote_to_vaga


@pytest.fixture(autouse=True)
def _bypass_template_signal():
    patched = template_base.Template._render
    template_base.Template._render = lambda self, ctx: self.nodelist.render(ctx)
    try:
        yield
    finally:
        template_base.Template._render = patched


@pytest.fixture
def user(db):
    t = Tomador.objects.create(nome="T", dominio_email="x.com")
    u = User.objects.create_user(
        email="rh@x.com", password="x", nome="RH",
        tipo_gestor=User.TipoGestor.A, tomador=t,
    )
    u.is_staff = True
    u.save()
    return u


def _make_req_revisao(user):
    return Requisicao.objects.create(
        criado_por=user,
        titulo="Auxiliar Administrativo",
        descricao="Apoio administrativo no setor.",
        payload_ia={
            "titulo": "Auxiliar Administrativo",
            "tomador": "INEP",
            "descricao_vaga": "Apoio administrativo.",
            "requisitos": ["Ensino médio", "Pacote Office"],
        },
        status=Requisicao.Status.REVISAO,
    )


@pytest.mark.django_db
def test_promote_to_vaga_a_partir_de_revisao(user):
    req = _make_req_revisao(user)
    vaga = promote_to_vaga(req)
    req.refresh_from_db()
    assert req.status == Requisicao.Status.APROVADA
    assert vaga.status == Vaga.Status.ATIVA
    assert vaga.titulo == "Auxiliar Administrativo"
    assert vaga.tomador == "INEP"
    assert vaga.requisitos == ["Ensino médio", "Pacote Office"]
    assert vaga.publicada_em is not None


@pytest.mark.django_db
def test_promote_to_vaga_idempotencia(user):
    req = _make_req_revisao(user)
    promote_to_vaga(req)
    with pytest.raises(DomainValidationError):
        promote_to_vaga(req)


@pytest.mark.django_db
def test_promote_to_vaga_requisicao_rejeitada_falha(user):
    req = _make_req_revisao(user)
    req.transition_to(Requisicao.Status.REJEITADA)
    req.save()
    with pytest.raises(DomainValidationError):
        promote_to_vaga(req)


@pytest.mark.django_db
def test_vaga_transicoes(user):
    req = _make_req_revisao(user)
    vaga = promote_to_vaga(req)

    vaga.transition_to(Vaga.Status.PAUSADA)
    assert vaga.status == Vaga.Status.PAUSADA

    vaga.transition_to(Vaga.Status.ATIVA)
    assert vaga.status == Vaga.Status.ATIVA

    vaga.transition_to(Vaga.Status.FECHADA)
    assert vaga.status == Vaga.Status.FECHADA

    # FECHADA é terminal
    with pytest.raises(DomainValidationError):
        vaga.transition_to(Vaga.Status.ATIVA)


@pytest.mark.django_db
def test_promote_to_vaga_requisitos_invalidos_vira_lista_vazia(user):
    req = _make_req_revisao(user)
    req.payload_ia["requisitos"] = "string ao invés de lista"
    req.save()
    vaga = promote_to_vaga(req)
    assert vaga.requisitos == []
