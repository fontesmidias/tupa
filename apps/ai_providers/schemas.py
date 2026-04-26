"""Pydantic schemas — Epic 4.0-MVP (Caminho C)."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class RPExtractResult(BaseModel):
    """Resultado de extração de uma Requisição de Pessoal via LLM."""

    model_config = ConfigDict(extra="forbid")

    titulo: str = Field(..., description="Título/cargo da vaga")
    tomador: str = Field(..., description="Nome do tomador/órgão contratante")
    descricao_vaga: str = Field(..., description="Descrição das atribuições")
    requisitos: list[str] = Field(
        default_factory=list, description="Lista de requisitos técnicos/formais"
    )
    motivo: str = Field(
        ..., description="Motivo da requisição (substituição, ampliação, novo projeto)"
    )
    confidence: float = Field(
        ..., ge=0.0, le=1.0, description="Confiança agregada 0-1"
    )


class ExtractionStats(BaseModel):
    """Estatísticas operacionais de uma chamada ao provider."""

    model_config = ConfigDict(extra="forbid")

    input_tokens: int
    output_tokens: int
    latency_ms: int
    model_id: str


class ExtractionEnvelope(BaseModel):
    """Retorno de `extract_rp_from_pdf` — resultado + telemetria."""

    model_config = ConfigDict(extra="forbid")

    result: RPExtractResult
    stats: ExtractionStats
    raw_response: dict
