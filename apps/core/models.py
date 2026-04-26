"""Core models — JobExecutionLog (ADR-010 idempotência)."""

from __future__ import annotations

import uuid

from django.db import models

from apps.core.base_models import TimestampedModel


class JobExecutionLog(TimestampedModel):
    """Registro de execução de jobs para idempotência (ADR-010)."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        SUCCESS = "success", "Success"
        FAILED = "failed", "Failed"
        SKIPPED_DUPLICATE = "skipped_duplicate", "Skipped (Duplicate)"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    actor_name = models.CharField(max_length=255)
    message_id = models.CharField(max_length=255, unique=True)
    args_hash = models.CharField(max_length=64)
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.PENDING)
    started_at = models.DateTimeField()
    finished_at = models.DateTimeField(null=True, blank=True)
    error_text = models.TextField(null=True, blank=True)

    class Meta:
        app_label = "core"
        indexes = [
            models.Index(fields=["actor_name", "args_hash", "status"]),
        ]

    def __str__(self) -> str:
        return f"{self.actor_name}:{self.message_id}[{self.status}]"
