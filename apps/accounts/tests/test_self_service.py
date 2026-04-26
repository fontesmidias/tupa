"""Testes Story 3.6a — Ver / Corrigir / Exportar."""

from __future__ import annotations

import json
import zipfile
from io import BytesIO
from pathlib import Path

import pytest
from django.conf import settings
from django.template import base as template_base
from django.test import Client

from apps.accounts.models import Tomador, User, UserDataExport
from apps.accounts.services.self_service import (
    build_user_export_zip,
    corrigir_user_nome,
)
from apps.audit.models import AuditLog


@pytest.fixture(autouse=True)
def _bypass_template_signal():
    """Python 3.14 quebra Context.__copy__ em render instrumentado."""
    patched = template_base.Template._render
    template_base.Template._render = lambda self, ctx: self.nodelist.render(ctx)
    try:
        yield
    finally:
        template_base.Template._render = patched


@pytest.fixture
def user(db):
    tomador = Tomador.objects.create(nome="T", dominio_email="x.com")
    return User.objects.create_user(
        email="u@x.com",
        password="x",
        nome="Antigo",
        tipo_gestor=User.TipoGestor.A,
        tomador=tomador,
    )


@pytest.fixture
def client_logged(user):
    c = Client()
    c.force_login(user)
    return c


@pytest.mark.django_db
def test_build_user_export_zip_contem_dados_audit_legal_aceites(user):
    AuditLog.seal(user, user, {}, {"v": 1}, "test.action")
    payload = build_user_export_zip(user)
    with zipfile.ZipFile(BytesIO(payload)) as zf:
        names = set(zf.namelist())
        assert {
            "dados.json",
            "audit.json",
            "legal_basis.json",
            "policy_acceptances.json",
            "README.txt",
        } <= names
        dados = json.loads(zf.read("dados.json"))
        audit = json.loads(zf.read("audit.json"))
        legal = json.loads(zf.read("legal_basis.json"))
        aceites = json.loads(zf.read("policy_acceptances.json"))
    assert dados["email"] == "u@x.com"
    assert dados["nome"] == "Antigo"
    assert len(audit) == 1
    assert audit[0]["action"] == "test.action"
    assert "email" in legal["fields"]
    assert legal["fields"]["email"]["base_legal"]
    assert isinstance(aceites, list)


@pytest.mark.django_db
def test_corrigir_user_nome_persiste_e_auditoria(user):
    corrigir_user_nome(user, "Novo Nome", ip="127.0.0.1", user_agent="ua")
    user.refresh_from_db()
    assert user.nome == "Novo Nome"
    log = AuditLog.objects.filter(action="user.self_corrected").last()
    assert log is not None
    assert log.before == {"nome": "Antigo"}
    assert log.after == {"nome": "Novo Nome"}


@pytest.mark.django_db
def test_corrigir_nome_vazio_erro(user):
    with pytest.raises(ValueError):
        corrigir_user_nome(user, "   ", ip=None, user_agent="")


@pytest.mark.django_db
def test_corrigir_nome_igual_noop(user):
    before_count = AuditLog.objects.count()
    corrigir_user_nome(user, "Antigo", ip=None, user_agent="")
    assert AuditLog.objects.count() == before_count


@pytest.mark.django_db
def test_meus_dados_view_renderiza(client_logged, user):
    resp = client_logged.get("/conta/meus-dados/")
    assert resp.status_code == 200
    assert b"Meus dados" in resp.content
    assert b"u@x.com" in resp.content


@pytest.mark.django_db
def test_meus_dados_anonimo_redireciona(db):
    resp = Client().get("/conta/meus-dados/")
    # AuthRequiredMiddleware trata antes — aceita 301/302/401
    assert resp.status_code in (301, 302, 401, 403)


@pytest.mark.django_db
def test_corrigir_view_atualiza(client_logged, user):
    resp = client_logged.post("/conta/meus-dados/corrigir/", {"nome": "Renomeado"})
    assert resp.status_code in (301, 302)
    user.refresh_from_db()
    assert user.nome == "Renomeado"


@pytest.mark.django_db
def test_exportar_view_cria_export_e_gera_arquivo(
    client_logged, user, tmp_path, settings
):
    settings.MEDIA_ROOT = tmp_path
    resp = client_logged.post("/conta/meus-dados/exportar/")
    assert resp.status_code in (301, 302)
    exports = UserDataExport.objects.filter(user=user)
    assert exports.count() == 1
    e = exports.first()
    # Broker inexistente em testes → fallback síncrono → status READY
    assert e.status == UserDataExport.Status.READY
    assert e.size_bytes > 0
    full = Path(settings.MEDIA_ROOT) / e.file_path
    assert full.exists()


@pytest.mark.django_db
def test_download_export_ready(client_logged, user, tmp_path, settings):
    settings.MEDIA_ROOT = tmp_path
    client_logged.post("/conta/meus-dados/exportar/")
    e = UserDataExport.objects.filter(user=user).first()
    resp = client_logged.get(f"/conta/meus-dados/exports/{e.pk}/")
    assert resp.status_code == 200
    assert resp["Content-Type"] in ("application/zip", "application/x-zip-compressed")


@pytest.mark.django_db
def test_download_export_pending_404(client_logged, user):
    e = UserDataExport.objects.create(user=user, status=UserDataExport.Status.PENDING)
    resp = client_logged.get(f"/conta/meus-dados/exports/{e.pk}/")
    assert resp.status_code == 404


@pytest.mark.django_db
def test_download_export_outro_user_404(client_logged, user):
    tomador = Tomador.objects.create(nome="T2")
    outro = User.objects.create_user(
        email="o@x.com", password="x", nome="N", tipo_gestor="A", tomador=tomador
    )
    e = UserDataExport.objects.create(user=outro, status=UserDataExport.Status.READY)
    resp = client_logged.get(f"/conta/meus-dados/exports/{e.pk}/")
    assert resp.status_code == 404
