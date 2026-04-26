"""Smoke test de types.py — garante que aliases são importáveis e são UUID/str."""

from __future__ import annotations

import uuid

from apps.core import types


def test_uuid_aliases_are_uuid() -> None:
    for alias in (
        types.UserId,
        types.TomadorId,
        types.CirculoId,
        types.RequisicaoId,
        types.VagaId,
        types.CandidatoId,
    ):
        assert alias is uuid.UUID


def test_trace_id_is_str() -> None:
    assert types.TraceId is str
