"""Cliente isolado Claude — Epic 4.0-MVP (Caminho C).

Fronteira de módulo (Winston): assinatura estável para permitir promoção a
driver `LLMProvider` no Epic 4 completo sem reescrita. A chave vem de
`settings.ANTHROPIC_API_KEY` (env/docker secret) — sem `AiProviderConfig`.
"""

from __future__ import annotations

import base64
import time
from typing import Any

from django.conf import settings

from apps.ai_providers.exceptions import (
    ExtractionFailed,
    ProviderUnavailable,
)
from apps.ai_providers.prompts.rp_extract_v1 import (
    PROMPT_VERSION,
    build_extract_prompt,
)
from apps.ai_providers.schemas import (
    ExtractionEnvelope,
    ExtractionStats,
    RPExtractResult,
)

EXTRACT_TOOL_SCHEMA: dict[str, Any] = {
    "name": "extract_rp",
    "description": "Retorna os campos estruturados da Requisição de Pessoal.",
    "input_schema": {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "titulo": {"type": "string"},
            "tomador": {"type": "string"},
            "descricao_vaga": {"type": "string"},
            "requisitos": {"type": "array", "items": {"type": "string"}},
            "motivo": {"type": "string"},
            "confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0},
        },
        "required": [
            "titulo",
            "tomador",
            "descricao_vaga",
            "requisitos",
            "motivo",
            "confidence",
        ],
    },
}

DEFAULT_TIMEOUT_SECONDS = 60
DEFAULT_MAX_TOKENS = 2048


def _build_client() -> Any:
    """Factory — isola `from anthropic import Anthropic` para facilitar mock."""
    from anthropic import Anthropic  # lazy: Django pode bootar sem key em dev

    api_key = getattr(settings, "ANTHROPIC_API_KEY", "") or ""
    if not api_key:
        raise ProviderUnavailable(
            "ANTHROPIC_API_KEY não configurada — Epic 4.0-MVP bloqueado."
        )
    return Anthropic(api_key=api_key, timeout=DEFAULT_TIMEOUT_SECONDS)


def _resolve_model_id() -> str:
    return (
        getattr(settings, "ANTHROPIC_MODEL_ID", "") or "claude-sonnet-4-5"
    )


def extract_rp_from_pdf(
    pdf_bytes: bytes, filename: str = "document.pdf"
) -> ExtractionEnvelope:
    """Envia PDF ao Claude e devolve `RPExtractResult` + telemetria.

    Raises:
        ProviderUnavailable: SDK error, timeout, 5xx, ausência de chave.
        ExtractionFailed: resposta sem `tool_use` ou schema inválido.
    """
    from anthropic import APIError

    if not pdf_bytes:
        raise ExtractionFailed("PDF vazio.")

    client = _build_client()
    model_id = _resolve_model_id()
    system = build_extract_prompt()
    pdf_b64 = base64.standard_b64encode(pdf_bytes).decode("ascii")

    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "document",
                    "source": {
                        "type": "base64",
                        "media_type": "application/pdf",
                        "data": pdf_b64,
                    },
                },
                {
                    "type": "text",
                    "text": (
                        "Extraia os campos da Requisição de Pessoal no PDF "
                        "acima usando a ferramenta `extract_rp`."
                    ),
                },
            ],
        }
    ]

    t0 = time.monotonic()
    try:
        response = client.messages.create(
            model=model_id,
            max_tokens=DEFAULT_MAX_TOKENS,
            system=system,
            tools=[EXTRACT_TOOL_SCHEMA],
            tool_choice={"type": "tool", "name": "extract_rp"},
            messages=messages,
        )
    except APIError as exc:
        raise ProviderUnavailable(f"Anthropic API error: {exc}") from exc
    latency_ms = int((time.monotonic() - t0) * 1000)

    tool_use_block = _first_tool_use(response)
    if tool_use_block is None:
        raise ExtractionFailed(
            f"Resposta sem tool_use (stop_reason={getattr(response, 'stop_reason', '?')})"
        )

    try:
        result = RPExtractResult.model_validate(tool_use_block.input)
    except Exception as exc:  # pydantic.ValidationError
        raise ExtractionFailed(f"Schema inválido: {exc}") from exc

    usage = getattr(response, "usage", None)
    stats = ExtractionStats(
        input_tokens=getattr(usage, "input_tokens", 0) if usage else 0,
        output_tokens=getattr(usage, "output_tokens", 0) if usage else 0,
        latency_ms=latency_ms,
        model_id=model_id,
    )

    return ExtractionEnvelope(
        result=result,
        stats=stats,
        raw_response={
            "prompt_version": PROMPT_VERSION,
            "stop_reason": getattr(response, "stop_reason", None),
            "tool_input": tool_use_block.input,
        },
    )


def _first_tool_use(response: Any) -> Any | None:
    for block in getattr(response, "content", []) or []:
        if getattr(block, "type", None) == "tool_use":
            return block
    return None
