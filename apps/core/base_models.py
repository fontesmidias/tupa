"""Modelos abstratos reutilizáveis — Timestamped, UUID, SoftDelete (ADR-008)."""

from __future__ import annotations

import uuid
from typing import Any

from django.db import models
from django.utils import timezone


class TimestampedModel(models.Model):
    """Adiciona created_at e updated_at."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UUIDModel(models.Model):
    """PK UUID v4."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class SoftDeleteManager(models.Manager["SoftDeleteModel"]):
    """Manager que esconde registros soft-deleted."""

    def get_queryset(self) -> models.QuerySet[Any]:
        return super().get_queryset().filter(deleted_at__isnull=True)


class SoftDeleteModel(models.Model):
    """Soft delete via deleted_at."""

    deleted_at = models.DateTimeField(null=True, blank=True, default=None)

    objects: SoftDeleteManager = SoftDeleteManager()
    all_objects: models.Manager[Any] = models.Manager()

    class Meta:
        abstract = True

    def soft_delete(self) -> None:
        self.deleted_at = timezone.now()
        self.save(update_fields=["deleted_at"])

    def restore(self) -> None:
        self.deleted_at = None
        self.save(update_fields=["deleted_at"])


class AuditableMixin(models.Model):
    """Marca model para auditoria automática via signals (Story 3.2).

    Subclasses podem declarar como atributos de classe (Django valida Meta
    estritamente, então não é possível coloca-los lá):
    - `auditable_fields: list[str]` — whitelist de campos auditados. Default: todos.
    - `auditable_exclude: list[str]` — blacklist adicional (precedência sobre fields).

    O plumbing está em `apps.audit.signals`; este mixin é apenas um marcador + hints.
    """

    class Meta:
        abstract = True

