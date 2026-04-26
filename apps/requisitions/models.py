"""Modelo Requisicao — Story 5.1 enxuta para fechar ciclo PDF→Requisicao→Vaga.

Estados simplificados (sem django-fsm): RASCUNHO → REVISAO → APROVADA | REJEITADA.
Transições válidas em `transition_to()`; inválida levanta DomainValidationError.

A versão completa do Epic 5 prevê estados extras (enviado, processando,
esclarecimento) — entrarão quando a UI do gestor (Stories 5.2-5.7) for
implementada. Para uso atual o pipeline é: AiExtractionLog (RH faz upload no
/lab/ia/) → promote_extraction_to_requisicao → Requisicao em REVISAO.
"""

from __future__ import annotations

import uuid

from django.conf import settings
from django.db import models

from apps.core.base_models import AuditableMixin, TimestampedModel
from apps.core.exceptions import DomainValidationError


class Requisicao(AuditableMixin, TimestampedModel):
    """Requisição de Pessoal — rascunho IA editável pelo RH antes de virar Vaga."""

    class Status(models.TextChoices):
        RASCUNHO = "rascunho", "Rascunho"
        REVISAO = "revisao", "Em revisão"
        APROVADA = "aprovada", "Aprovada"
        REJEITADA = "rejeitada", "Rejeitada"

    _VALID_TRANSITIONS: dict[str, set[str]] = {
        Status.RASCUNHO: {Status.REVISAO},
        Status.REVISAO: {Status.APROVADA, Status.REJEITADA, Status.RASCUNHO},
        Status.APROVADA: set(),
        Status.REJEITADA: {Status.REVISAO},
    }

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    criado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="requisicoes_criadas",
    )
    ai_log = models.ForeignKey(
        "ai_providers.AiExtractionLog",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="requisicoes",
        help_text="Log da extração IA que originou esta requisição (opcional).",
    )
    titulo = models.CharField(max_length=255)
    descricao = models.TextField(blank=True, default="")
    payload_ia = models.JSONField(
        default=dict,
        blank=True,
        help_text="Snapshot dos campos extraídos pela IA — editável pelo RH.",
    )
    score_confianca = models.FloatField(null=True, blank=True)
    status = models.CharField(
        max_length=16, choices=Status.choices, default=Status.RASCUNHO
    )
    motivo_rejeicao = models.TextField(blank=True, default="")

    class Meta:
        app_label = "requisitions"
        indexes = [
            models.Index(fields=["status", "-created_at"], name="req_status_recent_idx"),
            models.Index(fields=["criado_por", "-created_at"], name="req_user_recent_idx"),
        ]

    def __str__(self) -> str:
        return f"Requisicao({self.titulo}, {self.status})"

    def can_transition_to(self, new_status: str) -> bool:
        return new_status in self._VALID_TRANSITIONS.get(self.status, set())

    def transition_to(self, new_status: str) -> None:
        """Valida e aplica transição. Não persiste — caller faz save()."""
        if not self.can_transition_to(new_status):
            raise DomainValidationError(
                f"Transição inválida: {self.status} → {new_status}"
            )
        self.status = new_status
