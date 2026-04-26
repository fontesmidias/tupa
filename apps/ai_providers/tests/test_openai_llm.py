"""Testes do cliente OpenAI isolado — MVP.C.1 (GPT-4o-mini)."""

from __future__ import annotations

import pytest

from apps.ai_providers.exceptions import ExtractionFailed, ProviderUnavailable
from apps.ai_providers.providers.openai_llm import extract_rp_from_pdf
from apps.ai_providers.tests.conftest import (
    FakeResponse,
    FakeUsage,
    make_valid_response,
)


@pytest.fixture(autouse=True)
def _key(settings):
    settings.OPENAI_API_KEY = "sk-test-fake"
    settings.OPENAI_MODEL_ID = "gpt-4o-mini"


def test_happy_path_extrai_rp_estruturada(patch_openai):
    patch_openai(make_valid_response())
    envelope = extract_rp_from_pdf(b"%PDF-fake-bytes", filename="rp.pdf")
    assert envelope.result.titulo == "Assistente Administrativo"
    assert envelope.result.tomador == "SESI-DF"
    assert envelope.result.confidence == 0.85
    assert envelope.stats.model_id == "gpt-4o-mini"
    assert envelope.stats.input_tokens == 1200
    assert envelope.raw_response["prompt_version"] == "rp_extract_v3"


def test_pdf_vazio_raises():
    with pytest.raises(ExtractionFailed):
        extract_rp_from_pdf(b"")


def test_key_ausente_raises(settings):
    settings.OPENAI_API_KEY = ""
    with pytest.raises(ProviderUnavailable):
        extract_rp_from_pdf(b"%PDF-")


def test_resposta_sem_json_raises(patch_openai):
    # output_text não-JSON, sem output blocks → falha
    patch_openai(
        FakeResponse(output_text="desculpe, nao entendi", usage=FakeUsage())
    )
    with pytest.raises(ExtractionFailed, match="JSON"):
        extract_rp_from_pdf(b"%PDF-")


def test_schema_invalido_raises(patch_openai):
    import json

    # confidence fora do range [0,1] + campos obrigatórios ausentes
    patch_openai(
        FakeResponse(
            output_text=json.dumps({"titulo": "X", "tomador": "Y"}),
            usage=FakeUsage(),
        )
    )
    with pytest.raises(ExtractionFailed, match="Schema inválido"):
        extract_rp_from_pdf(b"%PDF-")


def test_api_error_no_responses_raises_provider_unavailable(patch_openai):
    import openai

    class _FakeRequest:
        method = "POST"
        url = "https://api.openai.com"

    err = openai.APIError(
        message="boom", request=_FakeRequest(), body=None
    )
    patch_openai(err)
    with pytest.raises(ProviderUnavailable, match="OpenAI API error"):
        extract_rp_from_pdf(b"%PDF-")


def test_api_error_no_upload_raises_provider_unavailable(patch_openai):
    import openai

    class _FakeRequest:
        method = "POST"
        url = "https://api.openai.com"

    err = openai.APIError(
        message="upload falhou", request=_FakeRequest(), body=None
    )
    patch_openai(response=make_valid_response(), file_error=err)
    with pytest.raises(ProviderUnavailable, match="file upload"):
        extract_rp_from_pdf(b"%PDF-")


def test_request_envia_pdf_como_input_file_com_instructions(patch_openai):
    client = patch_openai(make_valid_response())
    extract_rp_from_pdf(b"%PDF-abc", filename="x.pdf")
    # files.create foi chamado com purpose=user_data
    assert client.files.created
    assert client.files.created[0]["purpose"] == "user_data"
    # responses.create recebeu instructions + input_file + json_schema
    call = client.responses.calls[0]
    assert "Green House" in call["instructions"]
    content = call["input"][0]["content"]
    assert any(b.get("type") == "input_file" for b in content)
    fmt = call["text"]["format"]
    assert fmt["type"] == "json_schema"
    assert fmt["name"] == "extract_rp"
    assert fmt["strict"] is True


def test_cleanup_deleta_file_apos_sucesso(patch_openai):
    client = patch_openai(make_valid_response())
    extract_rp_from_pdf(b"%PDF-")
    assert client.files.deleted == ["file_fake_001"]


def test_cleanup_deleta_file_apos_api_error(patch_openai):
    import openai

    class _FakeRequest:
        method = "POST"
        url = "https://api.openai.com"

    err = openai.APIError(
        message="boom", request=_FakeRequest(), body=None
    )
    client = patch_openai(err)
    with pytest.raises(ProviderUnavailable):
        extract_rp_from_pdf(b"%PDF-")
    # mesmo em erro da responses.create, o arquivo deve ser limpado
    assert client.files.deleted == ["file_fake_001"]
