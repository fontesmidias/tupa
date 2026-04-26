"""Services do app vagas.

`promote_to_vaga(req)` — converte Requisicao APROVADA em Vaga ATIVA. Transacional:
muda status da Requisicao + cria Vaga em 1 transaction.
"""

from __future__ import annotations

from django.db import transaction
from django.utils import timezone

from apps.core.exceptions import DomainValidationError
from apps.requisitions.models import Requisicao
from apps.vagas.models import Vaga


@transaction.atomic
def promote_to_vaga(req: Requisicao) -> Vaga:
    """Cria Vaga ativa a partir de Requisicao aprovada.

    Pode ser chamada DURANTE a aprovação (req em REVISAO, transition para APROVADA
    + criação da Vaga atomicamente) ou APÓS (req já em APROVADA, só cria Vaga
    se não existir).
    """
    # Se ainda em revisão, aprovar agora.
    if req.status == Requisicao.Status.REVISAO:
        req.transition_to(Requisicao.Status.APROVADA)
        req.save(update_fields=["status", "updated_at"])

    if req.status != Requisicao.Status.APROVADA:
        raise DomainValidationError(
            f"Requisicao {req.pk} não está APROVADA (status={req.status})."
        )

    if hasattr(req, "vaga") and req.vaga is not None:
        raise DomainValidationError(
            f"Já existe Vaga para a Requisicao {req.pk}."
        )

    payload = req.payload_ia or {}
    requisitos = payload.get("requisitos") or []
    if not isinstance(requisitos, list):
        requisitos = []

    vaga = Vaga.objects.create(
        requisicao=req,
        titulo=req.titulo[:255],
        tomador=(payload.get("tomador") or "")[:255],
        descricao_md=req.descricao or (payload.get("descricao_vaga") or ""),
        requisitos=requisitos,
        status=Vaga.Status.ATIVA,
        publicada_em=timezone.now(),
    )
    return vaga
