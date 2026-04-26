"""AiExtractionLog — Epic 4.0-MVP (Caminho C).

Log append-ish (status muda PENDING → RUNNING → READY/FAILED, mas só adiante-se).
Não confundir com `AiProviderConfig` do Epic 4 completo — responsabilidades
distintas: este registra experimentos; aquele registra credenciais/health.
"""

from __future__ import annotations

from django.conf import settings
from django.db import models

from apps.core.base_models import TimestampedModel, UUIDModel


class AiExtractionLog(UUIDModel, TimestampedModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Na fila"
        RUNNING = "running", "Executando"
        READY = "ready", "Pronto"
        FAILED = "failed", "Falhou"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="ai_extractions",
    )
    pdf_filename = models.CharField(max_length=255, blank=True, default="")
    pdf_bytes = models.BigIntegerField(default=0)
    prompt_version = models.CharField(max_length=64, blank=True, default="")
    model_id = models.CharField(max_length=128, blank=True, default="")
    status = models.CharField(
        max_length=16, choices=Status.choices, default=Status.PENDING
    )
    input_tokens = models.IntegerField(default=0)
    output_tokens = models.IntegerField(default=0)
    latency_ms = models.IntegerField(default=0)
    confidence = models.FloatField(null=True, blank=True)
    parsed_ok = models.BooleanField(default=False)
    result = models.JSONField(null=True, blank=True)
    raw_response = models.JSONField(null=True, blank=True)
    error_text = models.TextField(blank=True, default="")
    notes = models.TextField(blank=True, default="")

    class Meta:
        app_label = "ai_providers"
        indexes = [
            models.Index(fields=["user", "-created_at"], name="ai_extr_recent_idx"),
            models.Index(fields=["status"], name="ai_extr_status_idx"),
        ]

    def __str__(self) -> str:
        return f"AiExtractionLog({self.pk}, {self.status})"
