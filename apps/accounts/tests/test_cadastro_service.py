"""Testes Story 2.4 — helpers de cadastro."""

from __future__ import annotations

import pytest

from apps.accounts.services.cadastro import infer_tipo_gestor, match_tomador_by_email
from apps.accounts.tests.factories import TomadorFactory


@pytest.mark.parametrize(
    ("email", "expected"),
    [
        ("x@gov.br", "B"),
        ("a@min.gov.br", "B"),
        ("b@sub.min.gov.br", "B"),
        ("c@greenhousedf.com.br", "A"),
        ("d@outrodominio.com", "C"),
        ("e@GOV.BR", "B"),
        ("", "C"),
    ],
)
def test_infer_tipo_gestor(email: str, expected: str) -> None:
    assert infer_tipo_gestor(email) == expected


@pytest.mark.django_db
def test_match_tomador_existing() -> None:
    t = TomadorFactory(dominio_email="empresa.com")
    result = match_tomador_by_email("alguem@empresa.com")
    assert result is not None and result.pk == t.pk


@pytest.mark.django_db
def test_match_tomador_case_insensitive() -> None:
    t = TomadorFactory(dominio_email="empresa.com")
    result = match_tomador_by_email("X@EMPRESA.COM")
    assert result is not None and result.pk == t.pk


@pytest.mark.django_db
def test_match_tomador_none() -> None:
    TomadorFactory(dominio_email="outro.com")
    assert match_tomador_by_email("x@naotem.com") is None


@pytest.mark.django_db
def test_match_tomador_invalid_email() -> None:
    assert match_tomador_by_email("semarroba") is None
    assert match_tomador_by_email("") is None
