"""URLs RH para requisições — ADR-009: kebab-PT-BR / snake-EN."""

from __future__ import annotations

from django.urls import path

from apps.requisitions import views

# Caminhos a montar via *root_urlpatterns no urls root.
root_urlpatterns = [
    path("rh/requisicoes/", views.requisicoes_list, name="requisicoes_list"),
    path(
        "rh/requisicoes/<uuid:req_id>/",
        views.requisicao_detail,
        name="requisicao_detail",
    ),
    path(
        "rh/requisicoes/<uuid:req_id>/rejeitar/",
        views.requisicao_rejeitar,
        name="requisicao_rejeitar",
    ),
    path(
        "rh/requisicoes/promover-de-extracao/<uuid:log_id>/",
        views.promover_de_extracao,
        name="requisicao_promover_de_extracao",
    ),
]
