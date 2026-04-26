"""AuditLog com hash-chain append-only (ADR-012 / Story 3.1)."""

from __future__ import annotations

import hashlib
import uuid
from typing import Any, NoReturn

from django.db import models, transaction
from django.utils import timezone

from apps.audit.exceptions import AuditAppendOnlyError
from apps.audit.managers import AuditLogManager
from apps.audit.utils import canonical_json

ZERO_HASH: str = "0" * 64


class AuditLog(models.Model):
    """Registro imutável de auditoria com cadeia de hashes SHA-256."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    actor_user_id = models.UUIDField(null=True, blank=True)
    ip = models.CharField(max_length=45, null=True, blank=True)
    user_agent = models.TextField(blank=True, default="")
    action = models.CharField(max_length=64)
    entity_type = models.CharField(max_length=64)
    entity_id = models.CharField(max_length=64)
    before = models.JSONField(default=dict, blank=True)
    after = models.JSONField(default=dict, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)
    hash_prev = models.CharField(max_length=64)
    hash_curr = models.CharField(max_length=64, unique=True)

    objects: AuditLogManager = AuditLogManager()

    class Meta:
        db_table = "audit_log"
        indexes = [
            models.Index(
                fields=["entity_type", "entity_id", "timestamp"],
                name="audit_entity_ts_idx",
            ),
            models.Index(
                fields=["actor_user_id", "timestamp"],
                name="audit_actor_ts_idx",
            ),
        ]
        constraints = [
            models.UniqueConstraint(fields=["hash_curr"], name="audit_hash_curr_unique"),
        ]

    # --- append-only enforcement ----------------------------------------

    def save(self, *args: Any, **kwargs: Any) -> None:
        if self.pk and type(self).objects.filter(pk=self.pk).exists():
            raise AuditAppendOnlyError("AuditLog is append-only: save() em registro existente")
        super().save(*args, **kwargs)

    def delete(self, *args: Any, **kwargs: Any) -> NoReturn:
        raise AuditAppendOnlyError("AuditLog is append-only: delete() bloqueado")

    # --- API pública ----------------------------------------------------

    @classmethod
    def seal(
        cls,
        actor: Any | None,
        entity: Any,
        before: dict[str, Any],
        after: dict[str, Any],
        action: str,
        ip: str | None = None,
        user_agent: str = "",
    ) -> "AuditLog":
        """Sela um novo registro de auditoria na cadeia de hashes.

        Atomic + select_for_update no último registro para evitar race condition.
        """
        entity_type = f"{entity._meta.app_label}.{entity.__class__.__name__}"
        entity_id = str(entity.pk)
        actor_user_id = getattr(actor, "pk", None) if actor is not None else None
        now = timezone.now()

        with transaction.atomic():
            last = (
                cls.objects.select_for_update()
                .order_by("-timestamp", "-id")
                .first()
            )
            hash_prev = last.hash_curr if last is not None else ZERO_HASH

            payload: dict[str, Any] = {
                "actor_user_id": str(actor_user_id) if actor_user_id is not None else None,
                "ip": ip,
                "user_agent": user_agent,
                "action": action,
                "entity_type": entity_type,
                "entity_id": entity_id,
                "before": before,
                "after": after,
                "timestamp_iso": now.isoformat(),
            }
            payload_json = canonical_json(payload)
            hash_curr = hashlib.sha256(
                f"{hash_prev}{payload_json}".encode("utf-8")
            ).hexdigest()

            log = cls(
                actor_user_id=actor_user_id,
                ip=ip,
                user_agent=user_agent,
                action=action,
                entity_type=entity_type,
                entity_id=entity_id,
                before=before,
                after=after,
                timestamp=now,
                hash_prev=hash_prev,
                hash_curr=hash_curr,
            )
            super(AuditLog, log).save(force_insert=True)
            return log
