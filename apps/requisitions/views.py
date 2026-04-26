"""Views RH para Requisicao — lista, detalhe, ações de revisão.

Acesso: staff-only (mesmo padrão do /lab/ia/ — Bruno e RH).
URLs montadas em apps.requisitions.urls.
"""

from __future__ import annotations

from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from apps.ai_providers.models import AiExtractionLog
from apps.core.exceptions import DomainValidationError
from apps.requisitions.models import Requisicao
from apps.requisitions.services import promote_extraction_to_requisicao


def _require_staff(request: HttpRequest) -> HttpResponse | None:
    user = getattr(request, "user", None)
    if user is None or not getattr(user, "is_staff", False):
        return HttpResponse(status=403)
    return None


@require_http_methods(["GET"])
def requisicoes_list(request: HttpRequest) -> HttpResponse:
    resp = _require_staff(request)
    if resp is not None:
        return resp
    qs = Requisicao.objects.all().order_by("-created_at")
    status_filter = request.GET.get("status", "")
    if status_filter and status_filter in {s.value for s in Requisicao.Status}:
        qs = qs.filter(status=status_filter)
    return render(
        request,
        "requisitions/list.html",
        {
            "requisicoes": qs[:100],
            "status_filter": status_filter,
            "status_choices": Requisicao.Status.choices,
        },
    )


@require_http_methods(["GET"])
def requisicao_detail(request: HttpRequest, req_id: str) -> HttpResponse:
    resp = _require_staff(request)
    if resp is not None:
        return resp
    req = get_object_or_404(Requisicao, pk=req_id)
    vaga = getattr(req, "vaga", None)
    return render(
        request,
        "requisitions/detail.html",
        {"req": req, "vaga": vaga},
    )


@require_http_methods(["POST"])
def requisicao_rejeitar(request: HttpRequest, req_id: str) -> HttpResponse:
    resp = _require_staff(request)
    if resp is not None:
        return resp
    req = get_object_or_404(Requisicao, pk=req_id)
    motivo = (request.POST.get("motivo") or "").strip()
    if not motivo:
        messages.error(request, "Motivo da rejeição é obrigatório.")
        return redirect("requisicao_detail", req_id=req.pk)
    try:
        req.transition_to(Requisicao.Status.REJEITADA)
    except DomainValidationError as exc:
        messages.error(request, str(exc))
        return redirect("requisicao_detail", req_id=req.pk)
    req.motivo_rejeicao = motivo[:5000]
    req.save(update_fields=["status", "motivo_rejeicao", "updated_at"])
    messages.success(request, "Requisição rejeitada.")
    return redirect("requisicao_detail", req_id=req.pk)


@require_http_methods(["POST"])
def promover_de_extracao(request: HttpRequest, log_id: str) -> HttpResponse:
    """Cria uma Requisicao a partir de um AiExtractionLog READY (vindo do /lab/ia/)."""
    resp = _require_staff(request)
    if resp is not None:
        return resp
    log = get_object_or_404(AiExtractionLog, pk=log_id)
    try:
        req = promote_extraction_to_requisicao(log)
    except DomainValidationError as exc:
        messages.error(request, str(exc))
        return redirect("ai_lab")
    messages.success(request, f"Requisição criada: {req.titulo}")
    return redirect("requisicao_detail", req_id=req.pk)
