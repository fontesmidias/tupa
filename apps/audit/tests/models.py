"""Models concretos apenas para testar AuditableMixin (Story 3.2)."""

from __future__ import annotations

from django.db import models

from apps.core.base_models import AuditableMixin


class AuditableTestModel(AuditableMixin, models.Model):
    name = models.CharField(max_length=50)
    secret = models.CharField(max_length=50, default="")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "audit"


class AuditableWhitelistModel(AuditableMixin, models.Model):
    auditable_fields = ["id", "name"]  # exclui mfa_secret

    name = models.CharField(max_length=50)
    mfa_secret = models.CharField(max_length=50, default="")

    class Meta:
        app_label = "audit"


class AuditableExcludeModel(AuditableMixin, models.Model):
    auditable_exclude = ["updated_at"]

    name = models.CharField(max_length=50)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "audit"
