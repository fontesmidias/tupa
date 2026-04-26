"""Testes do actor extract_rp_async — MVP.C.2."""

from __future__ import annotations

from pathlib import Path

import pytest

from apps.accounts.models import Tomador, User
from apps.ai_providers.models import AiExtractionLog
from apps.ai_providers.tasks import extract_rp_async, stash_pdf_for_job
from apps.ai_providers.tests.conftest import make_valid_response


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


@pytest.fixture(autouse=True)
def _key(settings, tmp_path):
    settings.OPENAI_API_KEY = "sk-test-fake"
    settings.MEDIA_ROOT = tmp_path


@pytest.mark.django_db
def test_actor_executa_e_popula_log(user, patch_openai, settings):
    settings.OPENAI_MODEL_ID = "gpt-4o-mini"
    patch_openai(make_valid_response())
    log = AiExtractionLog.objects.create(
        user=user, pdf_filename="rp.pdf", pdf_bytes=9
    )
    rel = stash_pdf_for_job(str(log.pk), b"%PDF-data")
    extract_rp_async.fn(str(log.pk), rel)
    log.refresh_from_db()
    assert log.status == AiExtractionLog.Status.READY
    assert log.parsed_ok is True
    assert log.confidence == 0.85
    assert log.result["titulo"] == "Assistente Administrativo"
    assert log.model_id == "gpt-4o-mini"
    assert log.prompt_version == "rp_extract_v3"


@pytest.mark.django_db
def test_actor_marca_failed_em_provider_error(user, patch_openai, settings):
    settings.OPENAI_API_KEY = ""  # forçar ProviderUnavailable
    log = AiExtractionLog.objects.create(user=user, pdf_filename="x.pdf")
    rel = stash_pdf_for_job(str(log.pk), b"%PDF-")
    extract_rp_async.fn(str(log.pk), rel)
    log.refresh_from_db()
    assert log.status == AiExtractionLog.Status.FAILED
    assert "ProviderUnavailable" in log.error_text


@pytest.mark.django_db
def test_actor_marca_failed_se_stash_ausente(user):
    log = AiExtractionLog.objects.create(user=user, pdf_filename="x.pdf")
    extract_rp_async.fn(str(log.pk), "ai_lab/nao-existe.pdf")
    log.refresh_from_db()
    assert log.status == AiExtractionLog.Status.FAILED
    assert "stash" in log.error_text.lower()


@pytest.mark.django_db
def test_actor_limpa_stash_apos_sucesso(user, patch_openai, settings):
    patch_openai(make_valid_response())
    log = AiExtractionLog.objects.create(user=user, pdf_filename="rp.pdf")
    rel = stash_pdf_for_job(str(log.pk), b"%PDF-data")
    full = Path(settings.MEDIA_ROOT) / rel
    assert full.exists()
    extract_rp_async.fn(str(log.pk), rel)
    assert not full.exists()


@pytest.mark.django_db
def test_actor_idempotente_segunda_chamada_skip(user, patch_openai):
    """@idempotent_actor: segunda chamada com mesmo args_hash vira SKIPPED_DUPLICATE."""
    from apps.core.models import JobExecutionLog

    patch_openai(make_valid_response())
    log = AiExtractionLog.objects.create(user=user, pdf_filename="rp.pdf")
    rel = stash_pdf_for_job(str(log.pk), b"%PDF-data")
    extract_rp_async.fn(str(log.pk), rel)
    # 2ª chamada com mesmos args
    extract_rp_async.fn(str(log.pk), rel)
    skipped = JobExecutionLog.objects.filter(
        actor_name="ai_providers.extract_rp",
        status=JobExecutionLog.Status.SKIPPED_DUPLICATE,
    )
    assert skipped.exists()
