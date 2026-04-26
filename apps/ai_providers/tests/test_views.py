"""Testes das views do /lab/ia/ — MVP.C.3."""

from __future__ import annotations

from io import BytesIO

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client

from apps.accounts.models import Tomador, User
from apps.ai_providers.models import AiExtractionLog
from apps.ai_providers.tests.conftest import make_valid_response


@pytest.fixture
def staff_user(db):
    t = Tomador.objects.create(nome="T", dominio_email="x.com")
    u = User.objects.create_user(
        email="rh@x.com", password="x", nome="RH",
        tipo_gestor=User.TipoGestor.A, tomador=t,
    )
    u.is_staff = True
    u.save()
    return u


@pytest.fixture
def regular_user(db):
    t = Tomador.objects.create(nome="T2", dominio_email="y.com")
    return User.objects.create_user(
        email="u@y.com", password="x", nome="U",
        tipo_gestor=User.TipoGestor.A, tomador=t,
    )


@pytest.fixture
def client_staff(staff_user):
    c = Client()
    c.force_login(staff_user)
    return c


@pytest.fixture(autouse=True)
def _key(settings, tmp_path):
    settings.OPENAI_API_KEY = "sk-test-fake"
    settings.AI_LAB_ENABLED = True
    settings.MEDIA_ROOT = tmp_path


@pytest.mark.django_db
def test_get_lab_staff_ok(client_staff):
    resp = client_staff.get("/lab/ia/")
    assert resp.status_code == 200
    assert b"Extra" in resp.content  # "Extrair" / "Extração"


@pytest.mark.django_db
def test_get_lab_nao_staff_403(regular_user):
    c = Client()
    c.force_login(regular_user)
    resp = c.get("/lab/ia/")
    assert resp.status_code == 403


@pytest.mark.django_db
def test_get_lab_feature_flag_off_404(client_staff, settings):
    settings.AI_LAB_ENABLED = False
    resp = client_staff.get("/lab/ia/")
    assert resp.status_code == 404


@pytest.mark.django_db
def test_post_sem_pdf_retorna_400(client_staff):
    resp = client_staff.post("/lab/ia/", {})
    assert resp.status_code == 400


@pytest.mark.django_db
def test_post_com_pdf_cria_log_e_executa(client_staff, patch_openai):
    patch_openai(make_valid_response())
    pdf = SimpleUploadedFile(
        "rp.pdf", b"%PDF-fake", content_type="application/pdf"
    )
    resp = client_staff.post("/lab/ia/", {"pdf": pdf})
    assert resp.status_code == 200
    logs = AiExtractionLog.objects.all()
    assert logs.count() == 1
    log = logs.first()
    # DRAMATIQ_EAGER em test settings → actor executou síncrono
    assert log.status == AiExtractionLog.Status.READY
    assert log.parsed_ok is True


@pytest.mark.django_db
def test_status_view_retorna_partial(client_staff, staff_user):
    log = AiExtractionLog.objects.create(
        user=staff_user, pdf_filename="x.pdf",
        status=AiExtractionLog.Status.RUNNING,
    )
    resp = client_staff.get(f"/lab/ia/{log.pk}/status/")
    assert resp.status_code == 200
    assert b"executando" in resp.content.lower()


@pytest.mark.django_db
def test_status_outro_user_404(client_staff, regular_user):
    log = AiExtractionLog.objects.create(
        user=regular_user, pdf_filename="x.pdf"
    )
    resp = client_staff.get(f"/lab/ia/{log.pk}/status/")
    assert resp.status_code == 404


@pytest.mark.django_db
def test_detail_view_salva_notes(client_staff, staff_user):
    log = AiExtractionLog.objects.create(
        user=staff_user, pdf_filename="x.pdf",
        status=AiExtractionLog.Status.READY,
        result={"titulo": "X"},
    )
    resp = client_staff.post(
        f"/lab/ia/{log.pk}/", {"notes": "tomador errado"}
    )
    assert resp.status_code == 200
    log.refresh_from_db()
    assert log.notes == "tomador errado"


@pytest.mark.django_db
def test_historico_filter_failed(client_staff, staff_user):
    AiExtractionLog.objects.create(
        user=staff_user, pdf_filename="ok.pdf",
        status=AiExtractionLog.Status.READY, parsed_ok=True,
    )
    AiExtractionLog.objects.create(
        user=staff_user, pdf_filename="fail.pdf",
        status=AiExtractionLog.Status.FAILED, parsed_ok=False,
    )
    resp = client_staff.get("/lab/ia/historico/?failed=1")
    assert resp.status_code == 200
    assert b"fail.pdf" in resp.content
    assert b"ok.pdf" not in resp.content


@pytest.mark.django_db
def test_lab_anonimo_bloqueado():
    resp = Client().get("/lab/ia/")
    # AuthRequiredMiddleware → 401
    assert resp.status_code in (301, 302, 401, 403)
