"""Manager e QuerySet append-only para AuditLog."""

from __future__ import annotations

from typing import Any, NoReturn

from django.db import models

from apps.audit.exceptions import AuditAppendOnlyError


class AuditLogQuerySet(models.QuerySet["Any"]):
    """QuerySet que bloqueia update/delete em massa."""

    def update(self, **kwargs: Any) -> NoReturn:
        raise AuditAppendOnlyError("AuditLog is append-only: update() bloqueado")

    def delete(self) -> NoReturn:
        raise AuditAppendOnlyError("AuditLog is append-only: delete() bloqueado")


class AuditLogManager(models.Manager["Any"]):
    """Manager append-only que retorna AuditLogQuerySet."""

    def get_queryset(self) -> AuditLogQuerySet:
        return AuditLogQuerySet(self.model, using=self._db)
