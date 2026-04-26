"""Registra models de teste para que o Django crie tabelas no setup do DB."""

from __future__ import annotations

# Import garante que os models sejam registrados antes do django_db_setup.
from apps.core.tests import models  # noqa: F401
