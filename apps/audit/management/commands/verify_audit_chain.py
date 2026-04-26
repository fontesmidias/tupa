"""Valida integridade da cadeia de hashes do AuditLog (Story 3.3)."""

from __future__ import annotations

import hashlib
from datetime import datetime
from typing import Any

from django.core.management.base import BaseCommand, CommandError, CommandParser
from django.utils.dateparse import parse_datetime

from apps.audit.models import ZERO_HASH, AuditLog
from apps.audit.utils import canonical_json


class Command(BaseCommand):
    help = "Valida integridade da cadeia de hashes do AuditLog (Story 3.3)."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--since",
            dest="since",
            help="ISO 8601 datetime; valida apenas registros com timestamp >= since.",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        since_raw: str | None = options.get("since")
        since: datetime | None = None
        if since_raw:
            since = parse_datetime(since_raw)
            if since is None:
                raise CommandError(f"--since invalido: '{since_raw}' (use ISO 8601)")

        qs = AuditLog.objects.all().order_by("timestamp", "id")
        if since is not None:
            qs = qs.filter(timestamp__gte=since)

        expected_prev = ZERO_HASH
        if since is not None:
            earlier = (
                AuditLog.objects.filter(timestamp__lt=since)
                .order_by("-timestamp", "-id")
                .first()
            )
            if earlier is not None:
                expected_prev = earlier.hash_curr

        count = 0
        for record in qs.iterator():
            count += 1
            if record.hash_prev != expected_prev:
                self._fail(record, "hash_prev nao bate com hash_curr anterior", expected_prev)
            payload: dict[str, Any] = {
                "actor_user_id": str(record.actor_user_id) if record.actor_user_id else None,
                "ip": record.ip,
                "user_agent": record.user_agent,
                "action": record.action,
                "entity_type": record.entity_type,
                "entity_id": record.entity_id,
                "before": record.before,
                "after": record.after,
                "timestamp_iso": record.timestamp.isoformat(),
            }
            recomputed = hashlib.sha256(
                f"{record.hash_prev}{canonical_json(payload)}".encode("utf-8")
            ).hexdigest()
            if recomputed != record.hash_curr:
                self._fail(record, "hash_curr recomputado nao bate", recomputed)
            expected_prev = record.hash_curr

        self.stdout.write(self.style.SUCCESS(f"Cadeia integra: {count} registros"))

    def _fail(self, record: AuditLog, reason: str, expected: str) -> None:
        raise CommandError(
            "CADEIA CORROMPIDA\n"
            f"  motivo: {reason}\n"
            f"  id: {record.id}\n"
            f"  timestamp: {record.timestamp.isoformat()}\n"
            f"  action: {record.action}\n"
            f"  entity: {record.entity_type} {record.entity_id}\n"
            f"  hash_prev armazenado: {record.hash_prev}\n"
            f"  hash_curr armazenado: {record.hash_curr}\n"
            f"  esperado: {expected}"
        )
