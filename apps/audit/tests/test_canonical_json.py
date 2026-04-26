"""Testes de canonical_json / _to_json_safe."""

from __future__ import annotations

import datetime as dt
import json
import uuid

from apps.audit.utils import _to_json_safe, canonical_json


def test_canonical_json_ordena_keys():
    out = canonical_json({"b": 1, "a": 2, "c": 3})
    assert out == '{"a":2,"b":1,"c":3}'


def test_canonical_json_uuid_para_str():
    u = uuid.uuid4()
    out = canonical_json({"id": u})
    assert str(u) in out


def test_canonical_json_datetime_para_isoformat():
    d = dt.datetime(2026, 4, 21, 12, 0, 0)
    out = canonical_json({"t": d})
    assert "2026-04-21T12:00:00" in out


def test_canonical_json_preserva_acentos():
    out = canonical_json({"nome": "João Ação"})
    assert "João" in out
    assert "Ação" in out


def test_canonical_json_separators_compactos():
    out = canonical_json({"a": 1, "b": 2})
    assert " " not in out


def test_to_json_safe_recursivo():
    u = uuid.uuid4()
    d = dt.date(2026, 1, 1)
    safe = _to_json_safe({"u": u, "lista": [u, d], "nested": {"x": u}})
    assert safe["u"] == str(u)
    assert safe["lista"][0] == str(u)
    assert safe["lista"][1] == d.isoformat()
    assert safe["nested"]["x"] == str(u)


def test_to_json_safe_tuple_set_para_lista():
    safe = _to_json_safe((1, 2, 3))
    assert safe == [1, 2, 3]
    safe2 = _to_json_safe({1, 2})
    assert isinstance(safe2, list)


def test_canonical_json_determinismo():
    p1 = {"b": 1, "a": {"z": 9, "y": 8}}
    p2 = {"a": {"y": 8, "z": 9}, "b": 1}
    assert canonical_json(p1) == canonical_json(p2)


def test_canonical_json_passthrough_primitivos():
    assert json.loads(canonical_json({"n": 1, "f": 1.5, "s": "x", "b": True, "nil": None}))
