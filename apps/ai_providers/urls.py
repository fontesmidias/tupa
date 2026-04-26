"""URLs do /lab/ia/ — ADR-009 (kebab-PT-BR paths, snake-EN names)."""

from __future__ import annotations

from django.urls import path

from apps.ai_providers.views import (
    ai_lab_detail_view,
    ai_lab_historico_view,
    ai_lab_status_view,
    ai_lab_view,
)

root_urlpatterns = [
    path("lab/ia/", ai_lab_view, name="ai_lab"),
    path("lab/ia/historico/", ai_lab_historico_view, name="ai_lab_historico"),
    path("lab/ia/<uuid:log_id>/", ai_lab_detail_view, name="ai_lab_detail"),
    path("lab/ia/<uuid:log_id>/status/", ai_lab_status_view, name="ai_lab_status"),
]
