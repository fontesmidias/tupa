"""Testes Story 3.6b — Anonimizar / Revogar opt-ins (LGPD Arts. 18, 20)."""

from __future__ import annotations

from io import StringIO

import pytest
from django.core import mail
from django.core.management import call_command
from django.template import base as template_base
from django.test import Client

from apps.accounts.models import MagicLink, Tomador, User
from apps.accounts.services.magic_link import request_magic_link
from apps.accounts.services.mfa import activate_mfa, generate_secret
from apps.accounts.services.self_service import (
    anonymize_user,
    issue_reauth_code,
    revoke_consent,
    verify_reauth_code,
)
from apps.audit.models import AuditLog


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
    tomador = Tomador.objects.create(nome="T", dominio_email="x.com")
    return User.objects.create_user(
        email="u@x.com",
        password="x",
        nome="Bruno",
        tipo_gestor=User.TipoGestor.A,
        tomador=tomador,
    )


@pytest.fixture
def client_logged(user):
    c = Client()
    c.force_login(user)
    return c


# --- serviço -------------------------------------------------------------


@pytest.mark.django_db
def test_anonymize_user_substitui_pii_preserva_id(user):
    pk_antes = user.pk
    email_antes = user.email
    anonymize_user(user, ip="127.0.0.1", user_agent="ua")
    user.refresh_from_db()
    assert user.pk == pk_antes
    assert user.email != email_antes
    assert user.email.endswith("@anonimizado.local")
    assert user.nome.startswith("Usuário anonimizado")
    assert user.anonimizado_em is not None
    assert user.is_active is False
    assert user.opt_in_marketing is False
    assert user.opt_in_analytics is False
    assert user.mfa_enabled is False


@pytest.mark.django_db
def test_anonymize_registra_audit_log_sem_vazar_pii(user):
    """PII não pode aparecer em claro no audit (Party Mode — Amelia)."""
    anonymize_user(user, ip="1.1.1.1", user_agent="ua")
    log = AuditLog.objects.filter(action="user.anonymized").last()
    assert log is not None
    # apenas digest é persistido
    assert "nome_digest" in log.before
    assert "email_digest" in log.before
    assert log.before["nome_digest"] != ""
    assert log.after["nome_digest"] != log.before["nome_digest"]
    # PII NUNCA aparece em claro
    assert "Bruno" not in str(log.before)
    assert "u@x.com" not in str(log.before)


@pytest.mark.django_db
def test_anonymize_idempotente_noop(user):
    anonymize_user(user, ip=None, user_agent="")
    nome_apos = user.nome
    count_antes = AuditLog.objects.count()
    anonymize_user(user, ip=None, user_agent="")
    assert user.nome == nome_apos
    noop = AuditLog.objects.filter(action="user.anonymize.noop")
    assert noop.count() == 1
    # apenas um novo log (o noop) além do original
    assert AuditLog.objects.count() == count_antes + 1


@pytest.mark.django_db
def test_anonymize_preserva_audit_chain(user):
    AuditLog.seal(user, user, {}, {"v": 1}, "test.pre")
    AuditLog.seal(user, user, {}, {"v": 2}, "test.pre2")
    anonymize_user(user, ip=None, user_agent="")
    out = StringIO()
    call_command("verify_audit_chain", stdout=out)
    assert "Cadeia integra" in out.getvalue()
    # actor_user_id dos logs anteriores ainda aponta para o user anonimizado
    log = AuditLog.objects.filter(action="test.pre").first()
    assert log.actor_user_id == user.pk


@pytest.mark.django_db
def test_anonymize_dispara_email_dpo(user, settings):
    settings.DPO_EMAIL = "dpo@example.com"
    mail.outbox = []
    anonymize_user(user, ip=None, user_agent="")
    assuntos = [m.subject for m in mail.outbox]
    assert any("user.anonymized" in s for s in assuntos)


@pytest.mark.django_db
def test_dpo_notify_skipped_quando_vazio_audita(user, settings):
    """DPO_EMAIL vazio — não mais buraco negro (Mary). Audit registra skip."""
    settings.DPO_EMAIL = ""
    anonymize_user(user, ip=None, user_agent="")
    skip = AuditLog.objects.filter(action="system:dpo.notify.skipped").last()
    assert skip is not None
    assert "DPO_EMAIL não configurado" in str(skip.after)


@pytest.mark.django_db
def test_dpo_notify_failure_registrada(user, settings, monkeypatch):
    """Falha de SMTP — audita em vez de engolir (Mary)."""
    settings.DPO_EMAIL = "dpo@example.com"

    def _raise(*args, **kwargs):
        raise RuntimeError("SMTP down")

    monkeypatch.setattr(
        "apps.accounts.services.self_service.send_mail", _raise
    )
    anonymize_user(user, ip=None, user_agent="")
    fail = AuditLog.objects.filter(action="system:dpo.notify.failed").last()
    assert fail is not None
    assert "SMTP down" in str(fail.after)


@pytest.mark.django_db
def test_revoke_consent_desativa_flags(user):
    revoke_consent(user, marketing=True, analytics=True, ip=None, user_agent="")
    user.refresh_from_db()
    assert user.opt_in_marketing is False
    assert user.opt_in_analytics is False
    log = AuditLog.objects.filter(action="consent.revoked").last()
    assert log is not None
    assert log.before["opt_in_marketing"] is True
    assert log.after["opt_in_marketing"] is False


@pytest.mark.django_db
def test_revoke_consent_parcial_apenas_marketing(user):
    revoke_consent(user, marketing=True, analytics=False, ip=None, user_agent="")
    user.refresh_from_db()
    assert user.opt_in_marketing is False
    assert user.opt_in_analytics is True


@pytest.mark.django_db
def test_revoke_consent_noop_sem_log(user):
    # já revogado
    revoke_consent(user, marketing=True, analytics=True, ip=None, user_agent="")
    count_antes = AuditLog.objects.filter(action="consent.revoked").count()
    revoke_consent(user, marketing=True, analytics=True, ip=None, user_agent="")
    count_depois = AuditLog.objects.filter(action="consent.revoked").count()
    assert count_depois == count_antes


# --- views ---------------------------------------------------------------


@pytest.mark.django_db
def test_anonimizar_view_get_renderiza(client_logged):
    resp = client_logged.get("/conta/meus-dados/anonimizar/")
    assert resp.status_code == 200
    assert b"Anonimizar" in resp.content


def _extract_reauth_code(body: str) -> str:
    """Captura o código do email de reauth com marcador explícito (evita frágil)."""
    import re

    m = re.search(r"Código de confirmação para anonimização:\s*(\d{6})", body)
    assert m is not None, f"código não encontrado em: {body!r}"
    return m.group(1)


@pytest.mark.django_db
def test_anonimizar_send_link_gera_magic_link_purpose_reauth(client_logged, user):
    mail.outbox = []
    resp = client_logged.post(
        "/conta/meus-dados/anonimizar/", {"acao": "send_link"}
    )
    assert resp.status_code == 200
    mls = MagicLink.objects.filter(email=user.email)
    assert mls.count() == 1
    # escopo de reauth — não serve para login
    assert mls.first().purpose == MagicLink.Purpose.REAUTH_ANONYMIZE
    assert len(mail.outbox) >= 1


@pytest.mark.django_db
def test_anonimizar_confirm_codigo_invalido(client_logged):
    resp = client_logged.post(
        "/conta/meus-dados/anonimizar/",
        {"acao": "confirm", "email_code": "000000"},
    )
    assert resp.status_code == 200
    assert b"inv" in resp.content.lower()


@pytest.mark.django_db
def test_anonimizar_confirm_requer_send_link_previo(client_logged, user):
    """Sem send_link prévio, não existe MagicLink com purpose reauth → confirm falha."""
    resp = client_logged.post(
        "/conta/meus-dados/anonimizar/",
        {"acao": "confirm", "email_code": "123456"},
    )
    assert resp.status_code == 200
    user.refresh_from_db()
    assert user.anonimizado_em is None


@pytest.mark.django_db
def test_anonimizar_nao_aceita_magic_link_de_login(client_logged, user):
    """Bug reportado por Amelia: link de login NÃO deve autenticar reauth."""
    # cria link de login normal (purpose=LOGIN)
    request_magic_link(email=user.email, ip="127.0.0.1", user_agent="ua")
    # captura código
    body = mail.outbox[-1].body
    import re

    m = re.search(r"(\d{6})", body)
    assert m is not None
    login_code = m.group(1)

    # tenta usar o código de login na reauth — deve FALHAR
    resp = client_logged.post(
        "/conta/meus-dados/anonimizar/",
        {"acao": "confirm", "email_code": login_code},
    )
    assert resp.status_code == 200
    user.refresh_from_db()
    assert user.anonimizado_em is None


@pytest.mark.django_db
def test_anonimizar_sem_mfa_fluxo_completo(client_logged, user):
    mail.outbox = []
    client_logged.post(
        "/conta/meus-dados/anonimizar/", {"acao": "send_link"}
    )
    assert mail.outbox
    code = _extract_reauth_code(mail.outbox[-1].body)

    resp = client_logged.post(
        "/conta/meus-dados/anonimizar/",
        {"acao": "confirm", "email_code": code},
    )
    assert resp.status_code in (301, 302)
    user.refresh_from_db()
    assert user.anonimizado_em is not None
    assert user.email.endswith("@anonimizado.local")


@pytest.mark.django_db
def test_anonimizar_com_mfa_exige_dupla_factor(user):
    """AC 3.6b: MFA ativo exige TOTP + código email (Amelia — Party Mode)."""
    import pyotp

    secret = generate_secret()
    activate_mfa(user, secret, pyotp.TOTP(secret).now())
    user.refresh_from_db()
    assert user.mfa_enabled is True

    c = Client()
    c.force_login(user)

    # 1) TOTP sozinho NÃO basta
    totp = pyotp.TOTP(secret).now()
    resp = c.post(
        "/conta/meus-dados/anonimizar/",
        {"acao": "confirm", "totp_code": totp},
    )
    assert resp.status_code == 200
    user.refresh_from_db()
    assert user.anonimizado_em is None

    # 2) envia código por email
    mail.outbox = []
    c.post("/conta/meus-dados/anonimizar/", {"acao": "send_link"})
    email_code = _extract_reauth_code(mail.outbox[-1].body)

    # 3) email code sozinho NÃO basta
    resp = c.post(
        "/conta/meus-dados/anonimizar/",
        {"acao": "confirm", "email_code": email_code},
    )
    assert resp.status_code == 200
    user.refresh_from_db()
    assert user.anonimizado_em is None

    # 4) ambos juntos — sucesso
    # reemite email_code (o anterior foi consumido na tentativa 3)
    mail.outbox = []
    c.post("/conta/meus-dados/anonimizar/", {"acao": "send_link"})
    email_code = _extract_reauth_code(mail.outbox[-1].body)
    totp = pyotp.TOTP(secret).now()
    resp = c.post(
        "/conta/meus-dados/anonimizar/",
        {"acao": "confirm", "email_code": email_code, "totp_code": totp},
    )
    assert resp.status_code in (301, 302)
    user.refresh_from_db()
    assert user.anonimizado_em is not None


@pytest.mark.django_db
def test_reauth_code_service_roundtrip(user):
    """issue_reauth_code/verify_reauth_code — contrato direto."""
    mail.outbox = []
    issue_reauth_code(user, ip=None, user_agent="")
    code = _extract_reauth_code(mail.outbox[-1].body)
    assert verify_reauth_code(user, code) is True
    # segunda tentativa falha (consumido)
    assert verify_reauth_code(user, code) is False


@pytest.mark.django_db
def test_reauth_code_rejeita_login_scope(user):
    """verify_reauth_code não aceita MagicLink de login (Party Mode)."""
    request_magic_link(email=user.email, ip="1.1.1.1", user_agent="ua")
    body = mail.outbox[-1].body
    import re

    m = re.search(r"(\d{6})", body)
    assert m is not None
    assert verify_reauth_code(user, m.group(1)) is False


@pytest.mark.django_db
def test_revogar_view_toggle(client_logged, user):
    resp = client_logged.post(
        "/conta/meus-dados/revogar/",
        {"marketing": "1", "analytics": "1"},
    )
    assert resp.status_code in (301, 302)
    user.refresh_from_db()
    assert user.opt_in_marketing is False
    assert user.opt_in_analytics is False


@pytest.mark.django_db
def test_revogar_view_requer_login():
    resp = Client().post("/conta/meus-dados/revogar/")
    assert resp.status_code in (301, 302, 401, 403)


@pytest.mark.django_db
def test_anonimizar_view_requer_login():
    resp = Client().get("/conta/meus-dados/anonimizar/")
    assert resp.status_code in (301, 302, 401, 403)
