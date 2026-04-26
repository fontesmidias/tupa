"""Cliente isolado OpenAI GPT-4o-mini — Epic 4.0-MVP (Caminho C).

Substitui claude_llm.py como provider ativo (escolha Bruno 2026-04-22).
Mantém a assinatura `extract_rp_from_pdf(bytes) → ExtractionEnvelope` para
compatibilidade total com o restante do app (tasks.py, views.py, testes).

Usa a Responses API do OpenAI SDK (v2.x) com:
- upload do PDF via Files API + `input_file` no content
- Structured Outputs (JSON schema com `strict=True`) forçando o shape do RP
"""

from __future__ import annotations

import io
import time
from typing import Any

from django.conf import settings

from apps.ai_providers.exceptions import (
    ExtractionFailed,
    ProviderUnavailable,
)
from apps.ai_providers.prompts.rp_extract_v3 import (
    PROMPT_VERSION,
    build_extract_prompt,
)
from apps.ai_providers.schemas import (
    ExtractionEnvelope,
    ExtractionStats,
    RPExtractResult,
)

# JSON Schema equivalente ao tool do Claude — forçado via Structured Outputs.
EXTRACT_JSON_SCHEMA: dict[str, Any] = {
    "name": "extract_rp",
    "schema": {
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
    "strict": True,
}

DEFAULT_TIMEOUT_SECONDS = 60
DEFAULT_MAX_TOKENS = 2048


def _build_client() -> Any:
    from openai import OpenAI  # lazy: Django pode bootar sem key em dev

    api_key = getattr(settings, "OPENAI_API_KEY", "") or ""
    if not api_key:
        raise ProviderUnavailable(
            "OPENAI_API_KEY não configurada — Epic 4.0-MVP bloqueado."
        )
    return OpenAI(api_key=api_key, timeout=DEFAULT_TIMEOUT_SECONDS)


def _resolve_model_id() -> str:
    return getattr(settings, "OPENAI_MODEL_ID", "") or "gpt-4o-mini"


def extract_rp_from_pdf(
    pdf_bytes: bytes, filename: str = "document.pdf"
) -> ExtractionEnvelope:
    """Envia PDF ao GPT-4o-mini e devolve `RPExtractResult` + telemetria.

    Raises:
        ProviderUnavailable: SDK error, timeout, 5xx, ausência de chave.
        ExtractionFailed: resposta sem saída válida ou schema inválido.
    """
    from openai import APIError

    if not pdf_bytes:
        raise ExtractionFailed("PDF vazio.")

    client = _build_client()
    model_id = _resolve_model_id()
    system = build_extract_prompt()

    t0 = time.monotonic()
    try:
        uploaded = client.files.create(
            file=(filename or "document.pdf", io.BytesIO(pdf_bytes), "application/pdf"),
            purpose="user_data",
        )
    except APIError as exc:
        raise ProviderUnavailable(f"OpenAI file upload error: {exc}") from exc

    try:
        response = client.responses.create(
            model=model_id,
            instructions=system,
            input=[
                {
                    "role": "user",
                    "content": [
                        {"type": "input_file", "file_id": uploaded.id},
                        {
                            "type": "input_text",
                            "text": (
                                "Extraia os campos da Requisição de Pessoal no "
                                "PDF acima. Retorne APENAS no formato JSON exigido."
                            ),
                        },
                    ],
                }
            ],
            text={"format": {"type": "json_schema", **EXTRACT_JSON_SCHEMA}},
            max_output_tokens=DEFAULT_MAX_TOKENS,
        )
    except APIError as exc:
        _safe_delete_file(client, uploaded.id)
        raise ProviderUnavailable(f"OpenAI API error: {exc}") from exc
    finally:
        latency_ms = int((time.monotonic() - t0) * 1000)

    _safe_delete_file(client, uploaded.id)

    payload = _extract_json_payload(response)
    if payload is None:
        raise ExtractionFailed(
            f"Resposta sem saída JSON (status={getattr(response, 'status', '?')})"
        )

    try:
        result = RPExtractResult.model_validate(payload)
    except Exception as exc:  # pydantic.ValidationError
        raise ExtractionFailed(f"Schema inválido: {exc}") from exc

    usage = getattr(response, "usage", None)
    input_tokens = getattr(usage, "input_tokens", 0) if usage else 0
    output_tokens = getattr(usage, "output_tokens", 0) if usage else 0

    stats = ExtractionStats(
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        latency_ms=latency_ms,
        model_id=model_id,
    )

    return ExtractionEnvelope(
        result=result,
        stats=stats,
        raw_response={
            "prompt_version": PROMPT_VERSION,
            "status": getattr(response, "status", None),
            "payload": payload,
        },
    )


def _extract_json_payload(response: Any) -> dict[str, Any] | None:
    """Resgata o JSON estruturado da Responses API.

    A SDK 2.x expõe `response.output_text` (string consolidada) e
    `response.output` (lista de blocos). Usamos `output_text` + parse JSON.
    """
    import json

    text = getattr(response, "output_text", None)
    if text:
        try:
            obj = json.loads(text)
            if isinstance(obj, dict):
                return obj
        except (ValueError, TypeError):
            pass

    for item in getattr(response, "output", []) or []:
        for block in getattr(item, "content", []) or []:
            t = getattr(block, "text", None)
            if not t:
                continue
            try:
                obj = json.loads(t)
                if isinstance(obj, dict):
                    return obj
            except (ValueError, TypeError):
                continue
    return None


def _safe_delete_file(client: Any, file_id: str) -> None:
    try:
        client.files.delete(file_id)
    except Exception:  # noqa: BLE001 — cleanup best-effort
        pass
