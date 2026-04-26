"""Dramatiq actor — Epic 4.0-MVP (Winston: async desde o dia 1)."""

from __future__ import annotations

import base64
from pathlib import Path
from typing import Any

from django.conf import settings
from django.utils import timezone

from apps.ai_providers.exceptions import ExtractionFailed, ProviderUnavailable
from apps.ai_providers.models import AiExtractionLog
from apps.core.tasks import idempotent_actor

# PDFs in-flight são gravados em MEDIA_ROOT/ai_lab/<uuid>.pdf enquanto o job
# roda; o actor lê e apaga após extração. Evita passar bytes no broker.
_LAB_SUBDIR = "ai_lab"


def stash_pdf_for_job(log_id: str, pdf_bytes: bytes) -> str:
    media = Path(settings.MEDIA_ROOT) / _LAB_SUBDIR
    media.mkdir(parents=True, exist_ok=True)
    path = media / f"{log_id}.pdf"
    path.write_bytes(pdf_bytes)
    return str(path.relative_to(settings.MEDIA_ROOT))


def _resolve_stash_path(rel_path: str) -> Path:
    return Path(settings.MEDIA_ROOT) / rel_path


@idempotent_actor(actor_name="ai_providers.extract_rp")
def extract_rp_async(log_id: str, stash_rel_path: str) -> None:
    from apps.ai_providers.providers.openai_llm import extract_rp_from_pdf

    log = AiExtractionLog.objects.filter(pk=log_id).first()
    if log is None:
        return

    log.status = AiExtractionLog.Status.RUNNING
    log.save(update_fields=["status", "updated_at"])

    pdf_path = _resolve_stash_path(stash_rel_path)
    try:
        pdf_bytes = pdf_path.read_bytes()
    except FileNotFoundError:
        _mark_failed(log, "stash PDF ausente")
        return

    try:
        envelope = extract_rp_from_pdf(pdf_bytes, filename=log.pdf_filename)
    except (ExtractionFailed, ProviderUnavailable) as exc:
        _mark_failed(log, f"{type(exc).__name__}: {exc}")
        _cleanup(pdf_path)
        return
    except Exception as exc:  # noqa: BLE001
        _mark_failed(log, f"unexpected: {exc}")
        _cleanup(pdf_path)
        raise

    log.status = AiExtractionLog.Status.READY
    log.prompt_version = envelope.raw_response.get("prompt_version", "")
    log.model_id = envelope.stats.model_id
    log.input_tokens = envelope.stats.input_tokens
    log.output_tokens = envelope.stats.output_tokens
    log.latency_ms = envelope.stats.latency_ms
    log.confidence = envelope.result.confidence
    log.parsed_ok = True
    log.result = envelope.result.model_dump()
    log.raw_response = envelope.raw_response
    log.save()
    _cleanup(pdf_path)


def _mark_failed(log: AiExtractionLog, reason: str) -> None:
    log.status = AiExtractionLog.Status.FAILED
    log.parsed_ok = False
    log.error_text = reason[:2000]
    log.save(update_fields=["status", "parsed_ok", "error_text", "updated_at"])


def _cleanup(path: Path) -> None:
    try:
        path.unlink(missing_ok=True)
    except OSError:
        pass
