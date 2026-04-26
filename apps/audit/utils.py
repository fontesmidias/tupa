"""Utilitários de serialização canônica para AuditLog."""

from __future__ import annotations

import datetime as _dt
import json
import uuid
from typing import Any


def _to_json_safe(value: Any) -> Any:
    """Converte valores Python para forma JSON-safe preservando determinismo.

    - UUID -> str
    - datetime/date -> isoformat
    - dict -> dict com keys str e valores recursivamente safe
    - list/tuple/set -> list com itens recursivamente safe
    - outros -> passthrough (json.dumps com default=str trata o resto)
    """
    if isinstance(value, uuid.UUID):
        return str(value)
    if isinstance(value, (_dt.datetime, _dt.date)):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(k): _to_json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_to_json_safe(v) for v in value]
    return value


def compute_diff(
    before: dict[str, Any],
    after: dict[str, Any],
    fields: list[str] | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Retorna (before_diff, after_diff) contendo só chaves cujo valor mudou.

    Comparação feita via canonical_json de cada valor. `fields`, se provido,
    restringe quais chaves entram no diff.
    """
    keys: set[str] = set(before.keys()) | set(after.keys())
    if fields is not None:
        keys &= set(fields)

    before_diff: dict[str, Any] = {}
    after_diff: dict[str, Any] = {}
    for key in keys:
        b_val = before.get(key)
        a_val = after.get(key)
        if canonical_json({"_": b_val}) != canonical_json({"_": a_val}):
            before_diff[key] = b_val
            after_diff[key] = a_val
    return before_diff, after_diff


def canonical_json(payload: dict[str, Any]) -> str:
    """Serializa dict em JSON canônico determinístico.

    sort_keys=True, separators compactos, ensure_ascii=False (acentos literais),
    default=str para fallback.
    """
    safe = _to_json_safe(payload)
    return json.dumps(
        safe,
        sort_keys=True,
        default=str,
        ensure_ascii=False,
        separators=(",", ":"),
    )
