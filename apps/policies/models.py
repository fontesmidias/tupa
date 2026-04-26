"""PolicyVersion + PolicyAcceptance (Story 3.4)."""

from __future__ import annotations

import uuid
from typing import Any, NoReturn

from django.conf import settings
from django.db import models

from apps.policies.exceptions import PolicyAcceptanceAppendOnlyError


class PolicyKind(models.TextChoices):
    TERMS = "terms", "Termos de Uso"
    PRIVACY = "privacy", "Política de Privacidade"


class PolicyVersion(models.Model):
    """Versão imutável de um documento legal (Termos/Privacidade)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    kind = models.CharField(max_length=16, choices=PolicyKind.choices)
    version = models.CharField(max_length=32, help_text="Semver, ex: 1.0.0")
    effective_at = models.DateTimeField()
    full_text_md = models.TextField()
    summary_of_changes_md = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "policy_version"
        constraints = [
            models.UniqueConstraint(
                fields=["kind", "version"],
                name="policy_version_kind_version_unique",
            ),
        ]
        indexes = [
            models.Index(fields=["kind", "-effective_at"], name="policy_kind_eff_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.get_kind_display()} v{self.version}"


class PolicyAcceptanceQuerySet(models.QuerySet["PolicyAcceptance"]):
    def update(self, **kwargs: Any) -> NoReturn:
        raise PolicyAcceptanceAppendOnlyError(
            "PolicyAcceptance is append-only: update() bloqueado"
        )

    def delete(self) -> NoReturn:
        raise PolicyAcceptanceAppendOnlyError(
            "PolicyAcceptance is append-only: delete() bloqueado"
        )


class PolicyAcceptanceManager(models.Manager["PolicyAcceptance"]):
    def get_queryset(self) -> PolicyAcceptanceQuerySet:
        return PolicyAcceptanceQuerySet(self.model, using=self._db)


class PolicyAcceptance(models.Model):
    """Aceite imutável de um usuário a uma PolicyVersion."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="policy_acceptances",
    )
    policy_version = models.ForeignKey(
        PolicyVersion,
        on_delete=models.PROTECT,
        related_name="acceptances",
    )
    accepted_at = models.DateTimeField(auto_now_add=True)
    ip = models.CharField(max_length=45, null=True, blank=True)
    user_agent = models.TextField(blank=True, default="")
    summary_shown_version = models.CharField(max_length=32, blank=True, default="")

    objects: PolicyAcceptanceManager = PolicyAcceptanceManager()

    class Meta:
        db_table = "policy_acceptance"
        indexes = [
            models.Index(fields=["user", "-accepted_at"], name="policy_user_acc_idx"),
        ]

    def save(self, *args: Any, **kwargs: Any) -> None:
        if self.pk and type(self).objects.filter(pk=self.pk).exists():
            raise PolicyAcceptanceAppendOnlyError(
                "PolicyAcceptance is append-only: save() em registro existente"
            )
        super().save(*args, **kwargs)

    def delete(self, *args: Any, **kwargs: Any) -> NoReturn:
        raise PolicyAcceptanceAppendOnlyError(
            "PolicyAcceptance is append-only: delete() bloqueado"
        )

    def __str__(self) -> str:
        return f"{self.user_id} → {self.policy_version_id} @ {self.accepted_at:%Y-%m-%d}"
