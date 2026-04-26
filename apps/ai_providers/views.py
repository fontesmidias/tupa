"""Views do /lab/ia/ — Epic 4.0-MVP (Caminho C).

- Staff-only + feature flag `AI_LAB_ENABLED`.
- Upload síncrono-chega/async-processa: POST cria log + dispara Dramatiq actor.
- HTMX poll em /status/<uuid>/ para ver progresso.
"""

from __future__ import annotations

import json
from typing import Any

from django.conf import settings
from django.http import HttpRequest, HttpResponse, HttpResponseNotFound
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_http_methods

from apps.ai_providers.models import AiExtractionLog
from apps.ai_providers.tasks import extract_rp_async, stash_pdf_for_job


def _lab_enabled() -> bool:
    return bool(getattr(settings, "AI_LAB_ENABLED", False))


def _require_staff(request: HttpRequest) -> HttpResponse | None:
    if not _lab_enabled():
        return HttpResponseNotFound("lab desabilitado")
    user = getattr(request, "user", None)
    if user is None or not getattr(user, "is_staff", False):
        return HttpResponse(status=403)
    return None


def _estimated_cost_usd(input_tokens: int, output_tokens: int) -> float:
    # GPT-4o-mini é o provider ativo do MVP; preços ANTHROPIC_* ficam
    # disponíveis para quando um segundo driver for plugado (Amelia opção b).
    inp_price = float(
        getattr(settings, "OPENAI_PRICE_INPUT_PER_MTOKENS", 0.15)
    )
    out_price = float(
        getattr(settings, "OPENAI_PRICE_OUTPUT_PER_MTOKENS", 0.60)
    )
    return (input_tokens * inp_price + output_tokens * out_price) / 1_000_000


def _log_row(log: AiExtractionLog) -> dict[str, Any]:
    return {
        "id": str(log.pk),
        "created_at": log.created_at,
        "pdf_filename": log.pdf_filename,
        "status": log.status,
        "status_label": log.get_status_display(),
        "confidence": log.confidence,
        "latency_ms": log.latency_ms,
        "cost_usd": _estimated_cost_usd(log.input_tokens, log.output_tokens),
        "prompt_version": log.prompt_version,
        "parsed_ok": log.parsed_ok,
    }


@require_http_methods(["GET", "POST"])
def ai_lab_view(request: HttpRequest) -> HttpResponse:
    resp = _require_staff(request)
    if resp is not None:
        return resp

    if request.method == "GET":
        recent = (
            AiExtractionLog.objects.filter(user=request.user)
            .order_by("-created_at")[:10]
        )
        return render(
            request,
            "lab/ia.html",
            {"recent": [_log_row(r) for r in recent]},
        )

    upload = request.FILES.get("pdf")
    if upload is None:
        return render(
            request,
            "lab/ia.html",
            {"error": "envie um PDF", "recent": []},
            status=400,
        )

    pdf_bytes = upload.read()
    log = AiExtractionLog.objects.create(
        user=request.user,
        pdf_filename=upload.name[:255],
        pdf_bytes=len(pdf_bytes),
        status=AiExtractionLog.Status.PENDING,
    )
    stash_rel = stash_pdf_for_job(str(log.pk), pdf_bytes)

    if getattr(settings, "DRAMATIQ_EAGER", False):
        extract_rp_async.fn(str(log.pk), stash_rel)
    else:
        try:
            extract_rp_async.send(str(log.pk), stash_rel)
        except Exception:  # noqa: BLE001 — broker offline em dev → síncrono
            extract_rp_async.fn(str(log.pk), stash_rel)

    log.refresh_from_db()
    return render(
        request,
        "lab/_job_row.html",
        {"log": _log_row(log)},
    )


@require_http_methods(["GET"])
def ai_lab_status_view(request: HttpRequest, log_id: str) -> HttpResponse:
    resp = _require_staff(request)
    if resp is not None:
        return resp
    log = get_object_or_404(
        AiExtractionLog, pk=log_id, user=request.user
    )
    return render(request, "lab/_job_row.html", {"log": _log_row(log)})


@require_http_methods(["GET", "POST"])
def ai_lab_detail_view(request: HttpRequest, log_id: str) -> HttpResponse:
    resp = _require_staff(request)
    if resp is not None:
        return resp
    log = get_object_or_404(
        AiExtractionLog, pk=log_id, user=request.user
    )

    if request.method == "POST":
        log.notes = request.POST.get("notes", "")[:5000]
        log.save(update_fields=["notes", "updated_at"])

    ctx = {
        "log": log,
        "row": _log_row(log),
        "result_pretty": (
            json.dumps(log.result, ensure_ascii=False, indent=2)
            if log.result
            else None
        ),
        "cost_usd": _estimated_cost_usd(log.input_tokens, log.output_tokens),
    }
    return render(request, "lab/ia_detail.html", ctx)


@require_http_methods(["GET"])
def ai_lab_historico_view(request: HttpRequest) -> HttpResponse:
    resp = _require_staff(request)
    if resp is not None:
        return resp
    qs = AiExtractionLog.objects.filter(user=request.user).order_by(
        "-created_at"
    )
    only_failed = request.GET.get("failed") == "1"
    low_conf = request.GET.get("low_conf") == "1"
    if only_failed:
        qs = qs.filter(parsed_ok=False)
    if low_conf:
        qs = qs.filter(confidence__lt=0.7)
    return render(
        request,
        "lab/ia_historico.html",
        {
            "rows": [_log_row(r) for r in qs[:50]],
            "filter_failed": only_failed,
            "filter_low_conf": low_conf,
        },
    )
