"""Testes do service promote_extraction_to_requisicao + transições FSM."""

from __future__ import annotations

import pytest
from django.template import base as template_base

from apps.accounts.models import Tomador, User
from apps.ai_providers.models import AiExtractionLog
from apps.core.exceptions import DomainValidationError
from apps.requisitions.models import Requisicao
from apps.requisitions.services import promote_extraction_to_requisicao


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


def _make_log_ready(user, **overrides):
    payload = {
        "titulo": "Auxiliar Administrativo",
        "tomador": "INEP",
        "descricao_vaga": "Atividades de apoio administrativo no setor X.",
        "requisitos": ["Ensino médio", "Pacote Office"],
        "motivo": "substituição",
        "confidence": 0.85,
    }
    payload.update(overrides)
    return AiExtractionLog.objects.create(
        user=user,
        pdf_filename="rp.pdf",
        status=AiExtractionLog.Status.READY,
        parsed_ok=True,
        result=payload,
        confidence=payload["confidence"],
        prompt_version="rp_extract_v3",
        model_id="gpt-4o-mini",
    )


@pytest.mark.django_db
def test_promote_extraction_cria_requisicao_em_revisao(user):
    log = _make_log_ready(user)
    req = promote_extraction_to_requisicao(log)
    assert req.status == Requisicao.Status.REVISAO
    assert req.titulo == "Auxiliar Administrativo"
    assert req.payload_ia["tomador"] == "INEP"
    assert req.score_confianca == 0.85
    assert req.ai_log_id == log.pk
    assert req.criado_por == user


@pytest.mark.django_db
def test_promote_extraction_log_nao_ready_falha(user):
    log = AiExtractionLog.objects.create(
        user=user, pdf_filename="x.pdf", status=AiExtractionLog.Status.RUNNING
    )
    with pytest.raises(DomainValidationError):
        promote_extraction_to_requisicao(log)


@pytest.mark.django_db
def test_promote_extraction_idempotencia(user):
    log = _make_log_ready(user)
    promote_extraction_to_requisicao(log)
    with pytest.raises(DomainValidationError):
        promote_extraction_to_requisicao(log)


@pytest.mark.django_db
def test_transicoes_validas_e_invalidas(user):
    log = _make_log_ready(user)
    req = promote_extraction_to_requisicao(log)

    # REVISAO → APROVADA permitido
    req.transition_to(Requisicao.Status.APROVADA)
    assert req.status == Requisicao.Status.APROVADA

    # APROVADA é terminal — qualquer transição falha
    with pytest.raises(DomainValidationError):
        req.transition_to(Requisicao.Status.REVISAO)


@pytest.mark.django_db
def test_promote_titulo_vazio_usa_default(user):
    log = _make_log_ready(user, titulo="")
    req = promote_extraction_to_requisicao(log)
    assert req.titulo == "Requisição sem título"
