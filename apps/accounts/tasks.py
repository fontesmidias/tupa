"""Tasks do app accounts — export LGPD (Story 3.6a)."""

from __future__ import annotations

import logging
import os
from pathlib import Path

from django.conf import settings
from django.utils import timezone

from apps.core.tasks import idempotent_actor

logger = logging.getLogger("accounts.tasks")


@idempotent_actor(max_retries=3)
def generate_user_data_export(export_id: str) -> None:
    """Gera ZIP com dados do titular + audit e salva em MEDIA_ROOT/exports/<user>/."""
    from apps.accounts.models import UserDataExport
    from apps.accounts.services.self_service import build_user_export_zip

    export = UserDataExport.objects.select_related("user").get(pk=export_id)
    try:
        payload = build_user_export_zip(export.user)
        root = Path(settings.MEDIA_ROOT) / "exports" / str(export.user_id)
        root.mkdir(parents=True, exist_ok=True)
        fname = f"{timezone.now():%Y%m%d-%H%M%S}-{str(export.pk)[:8]}.zip"
        path = root / fname
        path.write_bytes(payload)
        export.status = UserDataExport.Status.READY
        export.file_path = str(path.relative_to(settings.MEDIA_ROOT).as_posix())
        export.size_bytes = len(payload)
        export.save(update_fields=["status", "file_path", "size_bytes", "updated_at"])
    except Exception as exc:  # noqa: BLE001
        logger.exception("generate_user_data_export falhou export=%s", export_id)
        export.status = UserDataExport.Status.FAILED
        export.error_text = str(exc)[:1000]
        export.save(update_fields=["status", "error_text", "updated_at"])
        raise
