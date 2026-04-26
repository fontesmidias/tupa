"""Admin de PolicyVersion + PolicyAcceptance (Story 3.4)."""

from __future__ import annotations

from typing import Any

from django.contrib import admin
from django.http import HttpRequest

from apps.policies.models import PolicyAcceptance, PolicyVersion


@admin.register(PolicyVersion)
class PolicyVersionAdmin(admin.ModelAdmin):
    list_display = ("kind", "version", "effective_at", "created_at")
    list_filter = ("kind",)
    search_fields = ("version",)
    ordering = ("-effective_at",)


@admin.register(PolicyAcceptance)
class PolicyAcceptanceAdmin(admin.ModelAdmin):
    list_display = ("user", "policy_version", "accepted_at", "ip")
    list_filter = ("policy_version__kind",)
    search_fields = ("user__email",)
    ordering = ("-accepted_at",)
    readonly_fields = (
        "id",
        "user",
        "policy_version",
        "accepted_at",
        "ip",
        "user_agent",
        "summary_shown_version",
    )

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    def has_change_permission(
        self, request: HttpRequest, obj: Any = None
    ) -> bool:
        return False

    def has_delete_permission(
        self, request: HttpRequest, obj: Any = None
    ) -> bool:
        return False
