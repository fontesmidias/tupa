"""Modelo Vaga — Story 6.5 enxuta.

Vaga é o consumidor final do pipeline: Requisicao APROVADA vira Vaga ATIVA via
service `promote_to_vaga`. Embedding e matching (Epic 8) virão depois;
publicação externa (portal de candidatura) também é fora do escopo MVP atual.
"""

from __future__ import annotations

import uuid

from django.db import models

from apps.core.base_models import AuditableMixin, TimestampedModel
from apps.core.exceptions import DomainValidationError


class Vaga(AuditableMixin, TimestampedModel):
    """Vaga ativa derivada de Requisicao aprovada."""

    class Status(models.TextChoices):
        ATIVA = "ativa", "Ativa"
        PAUSADA = "pausada", "Pausada"
        FECHADA = "fechada", "Fechada"

    _VALID_TRANSITIONS: dict[str, set[str]] = {
        Status.ATIVA: {Status.PAUSADA, Status.FECHADA},
        Status.PAUSADA: {Status.ATIVA, Status.FECHADA},
        Status.FECHADA: set(),
    }

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    requisicao = models.OneToOneField(
        "requisitions.Requisicao",
        on_delete=models.PROTECT,
        related_name="vaga",
    )
    titulo = models.CharField(max_length=255)
    tomador = models.CharField(max_length=255, blank=True, default="")
    descricao_md = models.TextField(blank=True, default="")
    requisitos = models.JSONField(default=list, blank=True)
    status = models.CharField(
        max_length=16, choices=Status.choices, default=Status.ATIVA
    )
    publicada_em = models.DateTimeField(null=True, blank=True)
    fechada_em = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = "vagas"
        indexes = [
            models.Index(fields=["status", "-publicada_em"], name="vaga_status_pub_idx"),
        ]

    def __str__(self) -> str:
        return f"Vaga({self.titulo}, {self.status})"

    def can_transition_to(self, new_status: str) -> bool:
        return new_status in self._VALID_TRANSITIONS.get(self.status, set())

    def transition_to(self, new_status: str) -> None:
        if not self.can_transition_to(new_status):
            raise DomainValidationError(
                f"Transição inválida: {self.status} → {new_status}"
            )
        self.status = new_status
