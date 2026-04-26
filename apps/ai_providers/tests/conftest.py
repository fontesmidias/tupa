"""Fixtures compartilhadas — Epic 4.0-MVP."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

import pytest
from django.template import base as template_base


@pytest.fixture(autouse=True)
def _bypass_template_signal():
    """Python 3.14 quebra Context.__copy__ em render instrumentado."""
    patched = template_base.Template._render
    template_base.Template._render = lambda self, ctx: self.nodelist.render(ctx)
    try:
        yield
    finally:
        template_base.Template._render = patched


# -------- OpenAI Responses API fakes --------


@dataclass
class FakeFile:
    id: str = "file_fake_001"


@dataclass
class FakeUsage:
    input_tokens: int = 1200
    output_tokens: int = 180


@dataclass
class FakeResponse:
    output_text: str = ""
    status: str = "completed"
    usage: FakeUsage = field(default_factory=FakeUsage)
    output: list[Any] = field(default_factory=list)


def make_valid_response(**overrides: Any) -> FakeResponse:
    data = {
        "titulo": "Assistente Administrativo",
        "tomador": "SESI-DF",
        "descricao_vaga": "Atividades administrativas gerais.",
        "requisitos": ["Ensino superior", "CNH B"],
        "motivo": "Substituição de funcionário desligado",
        "confidence": 0.85,
    }
    data.update(overrides)
    return FakeResponse(
        output_text=json.dumps(data, ensure_ascii=False),
        usage=FakeUsage(),
    )


class FakeFilesAPI:
    def __init__(self, file_obj: FakeFile) -> None:
        self._file = file_obj
        self.created: list[dict[str, Any]] = []
        self.deleted: list[str] = []

    def create(self, **kwargs: Any) -> FakeFile:
        self.created.append(kwargs)
        return self._file

    def delete(self, file_id: str) -> None:
        self.deleted.append(file_id)


class FakeResponsesAPI:
    def __init__(self, response_or_error: Any) -> None:
        self._response_or_error = response_or_error
        self.calls: list[dict[str, Any]] = []

    def create(self, **kwargs: Any) -> Any:
        self.calls.append(kwargs)
        if isinstance(self._response_or_error, Exception):
            raise self._response_or_error
        return self._response_or_error


class FakeOpenAI:
    def __init__(
        self,
        response: Any = None,
        file_error: Exception | None = None,
        **_: Any,
    ) -> None:
        self.files = FakeFilesAPI(FakeFile())
        self.responses = FakeResponsesAPI(response)
        if file_error is not None:
            def _raise(**_kw: Any) -> FakeFile:
                raise file_error

            self.files.create = _raise  # type: ignore[method-assign]


@pytest.fixture
def patch_openai(monkeypatch):
    """Helper: substitui `openai.OpenAI` por fábrica controlada."""

    def _apply(
        response: Any = None, file_error: Exception | None = None
    ) -> FakeOpenAI:
        client = FakeOpenAI(response=response, file_error=file_error)
        monkeypatch.setattr("openai.OpenAI", lambda *a, **kw: client)
        return client

    return _apply
