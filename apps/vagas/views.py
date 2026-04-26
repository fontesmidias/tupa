"""Views Vaga — lista e detalhe (RH staff-only).

Publicação externa (portal candidato) é fora do escopo desta etapa MVP.
"""

from __future__ import annotations

from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from apps.core.exceptions import DomainValidationError
from apps.requisitions.models import Requisicao
from apps.vagas.models import Vaga
from apps.vagas.services import promote_to_vaga


def _require_staff(request: HttpRequest) -> HttpResponse | None:
    user = getattr(request, "user", None)
    if user is None or not getattr(user, "is_staff", False):
        return HttpResponse(status=403)
    return None


@require_http_methods(["GET"])
def vagas_list(request: HttpRequest) -> HttpResponse:
    resp = _require_staff(request)
    if resp is not None:
        return resp
    qs = Vaga.objects.all().select_related("requisicao").order_by("-publicada_em")
    status_filter = request.GET.get("status", "")
    if status_filter and status_filter in {s.value for s in Vaga.Status}:
        qs = qs.filter(status=status_filter)
    return render(
        request,
        "vagas/list.html",
        {
            "vagas": qs[:100],
            "status_filter": status_filter,
            "status_choices": Vaga.Status.choices,
        },
    )


@require_http_methods(["GET"])
def vaga_detail(request: HttpRequest, vaga_id: str) -> HttpResponse:
    resp = _require_staff(request)
    if resp is not None:
        return resp
    vaga = get_object_or_404(Vaga.objects.select_related("requisicao"), pk=vaga_id)
    return render(request, "vagas/detail.html", {"vaga": vaga})


@require_http_methods(["POST"])
def aprovar_requisicao_publicar(request: HttpRequest, req_id: str) -> HttpResponse:
    """Aprova Requisicao e publica como Vaga ativa (transacional via service)."""
    resp = _require_staff(request)
    if resp is not None:
        return resp
    req = get_object_or_404(Requisicao, pk=req_id)
    try:
        vaga = promote_to_vaga(req)
    except DomainValidationError as exc:
        messages.error(request, str(exc))
        return redirect("requisicao_detail", req_id=req.pk)
    messages.success(request, f"Requisição aprovada e vaga criada: {vaga.titulo}")
    return redirect("vaga_detail", vaga_id=vaga.pk)


@require_http_methods(["POST"])
def vaga_alterar_status(request: HttpRequest, vaga_id: str) -> HttpResponse:
    resp = _require_staff(request)
    if resp is not None:
        return resp
    vaga = get_object_or_404(Vaga, pk=vaga_id)
    target = (request.POST.get("status") or "").strip()
    try:
        vaga.transition_to(target)
    except DomainValidationError as exc:
        messages.error(request, str(exc))
        return redirect("vaga_detail", vaga_id=vaga.pk)
    update_fields = ["status", "updated_at"]
    if target == Vaga.Status.FECHADA:
        from django.utils import timezone

        vaga.fechada_em = timezone.now()
        update_fields.append("fechada_em")
    vaga.save(update_fields=update_fields)
    messages.success(request, f"Vaga atualizada para {vaga.get_status_display()}.")
    return redirect("vaga_detail", vaga_id=vaga.pk)
