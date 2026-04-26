"""URLs do app policies — ADR-009 (kebab-PT-BR paths, snake-EN names)."""

from __future__ import annotations

from django.urls import path

from apps.policies.views import (
    policy_accept_view,
    policy_full_text_view,
    policy_reject_view,
)

app_name = "policies"

urlpatterns = [
    path("aceitar/", policy_accept_view, name="policy_accept"),
    path("recusar/", policy_reject_view, name="policy_reject"),
    path(
        "<str:kind>/v<str:version>/",
        policy_full_text_view,
        name="policy_full_text",
    ),
]
