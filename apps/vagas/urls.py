"""URLs de vagas (RH) — ADR-009."""

from __future__ import annotations

from django.urls import path

from apps.vagas import views

root_urlpatterns = [
    path("rh/vagas/", views.vagas_list, name="vagas_list"),
    path("rh/vagas/<uuid:vaga_id>/", views.vaga_detail, name="vaga_detail"),
    path(
        "rh/vagas/<uuid:vaga_id>/status/",
        views.vaga_alterar_status,
        name="vaga_alterar_status",
    ),
    path(
        "rh/requisicoes/<uuid:req_id>/aprovar/",
        views.aprovar_requisicao_publicar,
        name="requisicao_aprovar",
    ),
]
