"""Serviço de cadastro progressivo — Story 2.4.

Helpers para pré-preencher tipo_gestor e tomador a partir do email do usuário.
"""

from __future__ import annotations

from apps.accounts.models import Tomador


def _extract_domain(email: str) -> str:
    if not email or "@" not in email:
        return ""
    return email.split("@", 1)[1].strip().lower()


def infer_tipo_gestor(email: str) -> str:
    """Infere tipo_gestor a partir do domínio do email.

    - `.gov.br` (qualquer subdomínio) -> 'B'
    - `greenhousedf.com.br` -> 'A'
    - outros -> 'C'
    """
    domain = _extract_domain(email)
    if domain == "gov.br" or domain.endswith(".gov.br"):
        return "B"
    if domain == "greenhousedf.com.br":
        return "A"
    return "C"


def match_tomador_by_email(email: str) -> Tomador | None:
    """Retorna Tomador cujo dominio_email bate com o domínio do email, ou None."""
    return Tomador.match_by_email_domain(email)
