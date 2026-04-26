"""Enforcement do grafo de dependencias definido no ADR-012.

5 camadas (N pode importar de M se M <= N):
    1 core
    2 accounts
    3 requisitions, ai_providers, curriculos, email_ingestion, policies (dominio)
    4 vagas, matching (composicao)
    5 audit, notifications, telemetry, help (folhas)

Regras:
    - upward imports sao proibidos (ex: core importando accounts)
    - apps/audit NAO pode ser importado por NINGUEM (folha terminal / append-only)
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

APPS_DIR = Path(__file__).resolve().parent.parent.parent / "apps"

LAYERS: dict[str, int] = {
    "core": 1,
    "accounts": 2,
    "requisitions": 3,
    "ai_providers": 3,
    "curriculos": 3,
    "email_ingestion": 3,
    "policies": 3,
    "vagas": 4,
    "matching": 4,
    "audit": 5,
    "notifications": 5,
    "telemetry": 5,
    "help": 5,
}


def _collect_app_imports(app_name: str) -> set[tuple[str, str, int]]:
    """Retorna tuplas (from_app, imported_app, line) de imports cross-app."""
    imports: set[tuple[str, str, int]] = set()
    app_root = APPS_DIR / app_name
    for py_file in app_root.rglob("*.py"):
        # Ignora pastas de teste — testes podem importar livremente.
        if "tests" in py_file.parts:
            continue
        try:
            tree = ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                mod = node.module
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.startswith("apps."):
                        parts = alias.name.split(".")
                        if len(parts) >= 2 and parts[1] != app_name:
                            imports.add((app_name, parts[1], node.lineno))
                continue
            else:
                continue
            if mod.startswith("apps."):
                parts = mod.split(".")
                if len(parts) >= 2 and parts[1] != app_name:
                    imports.add((app_name, parts[1], node.lineno))
    return imports


def _all_imports() -> set[tuple[str, str, int]]:
    result: set[tuple[str, str, int]] = set()
    for app in LAYERS:
        result |= _collect_app_imports(app)
    return result


def test_no_upward_imports() -> None:
    """App em camada N so importa de camada M onde M <= N."""
    violations: list[str] = []
    for src, dst, line in _all_imports():
        if LAYERS[src] < LAYERS[dst]:
            violations.append(
                f"apps.{src} (layer {LAYERS[src]}) importa apps.{dst} "
                f"(layer {LAYERS[dst]}) em linha {line}"
            )
    assert not violations, "Imports upward proibidos (ADR-012):\n  " + "\n  ".join(violations)


def test_audit_is_terminal_leaf() -> None:
    """apps.audit nao pode ser importado por nenhum outro app (append-only)."""
    violations: list[str] = []
    for src, dst, line in _all_imports():
        if dst == "audit":
            violations.append(f"apps.{src} importa apps.audit em linha {line}")
    assert not violations, "apps.audit e folha terminal (ADR-012):\n  " + "\n  ".join(violations)


def test_all_apps_mapped() -> None:
    """Sanity: todo diretorio em apps/ tem entrada em LAYERS."""
    apps_on_disk = {p.name for p in APPS_DIR.iterdir() if p.is_dir() and (p / "apps.py").exists()}
    missing = apps_on_disk - set(LAYERS)
    extra = set(LAYERS) - apps_on_disk
    assert not missing, f"Apps sem camada em LAYERS: {missing}"
    assert not extra, f"Camadas para apps inexistentes: {extra}"


@pytest.mark.parametrize("app_name", list(LAYERS.keys()))
def test_app_has_appconfig(app_name: str) -> None:
    """Todo app tem AppConfig registrado."""
    assert (APPS_DIR / app_name / "apps.py").exists(), f"apps.{app_name} sem apps.py"
