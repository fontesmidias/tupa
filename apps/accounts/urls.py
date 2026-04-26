"""URLs do app accounts — ADR-009 (kebab-PT-BR paths, snake-EN names)."""

from __future__ import annotations

from django.urls import path

from apps.accounts.views.auth import (
    complete_profile_view,
    consume_code_view,
    gestor_home_view,
    logout_view,
    rh_home_view,
    signin_view,
)
from apps.accounts.views.mfa import mfa_challenge_view, mfa_setup_view
from apps.accounts.views.self_service import (
    meus_dados_anonimizar_view,
    meus_dados_corrigir_view,
    meus_dados_download_view,
    meus_dados_exportar_view,
    meus_dados_revogar_view,
    meus_dados_view,
)

app_name = "accounts"

urlpatterns = [
    path("entrar/", signin_view, name="auth_signin"),
    path("codigo/", consume_code_view, name="auth_consume_code"),
    path("completar-perfil/", complete_profile_view, name="accounts_complete_profile"),
    path("mfa/", mfa_challenge_view, name="auth_mfa_challenge"),
    path("sair/", logout_view, name="auth_logout"),
]

# Rotas fora do namespace "accounts" para nomes root-level
root_urlpatterns = [
    path("rh/", rh_home_view, name="rh_home"),
    path("gestor/", gestor_home_view, name="gestor_home"),
    path("conta/seguranca/mfa/", mfa_setup_view, name="mfa_setup"),
    path("conta/meus-dados/", meus_dados_view, name="self_meus_dados"),
    path(
        "conta/meus-dados/corrigir/",
        meus_dados_corrigir_view,
        name="self_corrigir",
    ),
    path(
        "conta/meus-dados/exportar/",
        meus_dados_exportar_view,
        name="self_exportar",
    ),
    path(
        "conta/meus-dados/exports/<uuid:export_id>/",
        meus_dados_download_view,
        name="self_export_download",
    ),
    path(
        "conta/meus-dados/anonimizar/",
        meus_dados_anonimizar_view,
        name="self_anonimizar",
    ),
    path(
        "conta/meus-dados/revogar/",
        meus_dados_revogar_view,
        name="self_revogar",
    ),
]
