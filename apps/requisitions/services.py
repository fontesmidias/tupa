"""Services do app requisitions.

`promote_extraction_to_requisicao(log)` — converte AiExtractionLog READY em
Requisicao em REVISAO, copiando o resultado da IA como payload_ia editável.
"""

from __future__ import annotations

from django.db import transaction

from apps.ai_providers.models import AiExtractionLog
from apps.core.exceptions import DomainValidationError
from apps.requisitions.models import Requisicao


@transaction.atomic
def promote_extraction_to_requisicao(log: AiExtractionLog) -> Requisicao:
    """Cria uma Requisicao em REVISAO a partir de um AiExtractionLog pronto.

    O usuário criador é o dono do log (geralmente o RH que fez upload no /lab/ia/).
    Idempotente em relação a logs duplicados — se já existir Requisicao para o log,
    levanta DomainValidationError ao invés de duplicar.
    """
    if log.status != AiExtractionLog.Status.READY:
        raise DomainValidationError(
            f"Log {log.pk} não está READY (status={log.status})."
        )
    if not log.parsed_ok or not log.result:
        raise DomainValidationError(
            f"Log {log.pk} não tem resultado válido (parsed_ok={log.parsed_ok})."
        )
    if Requisicao.objects.filter(ai_log=log).exists():
        raise DomainValidationError(
            f"Já existe Requisicao para o log {log.pk}."
        )

    payload = log.result
    titulo = (payload.get("titulo") or "").strip() or "Requisição sem título"

    req = Requisicao.objects.create(
        criado_por=log.user,
        ai_log=log,
        titulo=titulo[:255],
        descricao=(payload.get("descricao_vaga") or "")[:10000],
        payload_ia=payload,
        score_confianca=log.confidence,
        status=Requisicao.Status.REVISAO,
    )
    return req
