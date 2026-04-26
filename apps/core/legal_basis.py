"""Base legal por campo/finalidade (LGPD Art. 7º) — Party Mode Mary.

Data como código. Vive em `apps.core` (camada 1) para respeitar ADR-012:
qualquer app da camada 2+ pode consumir sem violar o grafo.
"""

from __future__ import annotations

from django.db import models


class LegalBasis(models.TextChoices):
    CONSENTIMENTO = "consentimento", "Consentimento (Art. 7º I)"
    EXEC_CONTRATO = "exec_contrato", "Execução de contrato (Art. 7º V)"
    OBRIG_LEGAL = "obrig_legal", "Obrigação legal/regulatória (Art. 7º II)"
    LEGIT_INTERESSE = "legit_interesse", "Legítimo interesse — LIA (Art. 7º IX)"
    POLITICAS_PUBLICAS = "politicas_publicas", "Políticas públicas (Art. 7º III)"


# Mapa campo → (base_legal, finalidade). Decidido com DPO.
# ⚠️ Itens com base legal provisória precisam ratificação formal (Appendix B).
USER_FIELD_LEGAL_BASIS: dict[str, dict[str, str]] = {
    "email": {
        "base_legal": LegalBasis.EXEC_CONTRATO,
        "finalidade": "autenticação e comunicação operacional",
    },
    "nome": {
        "base_legal": LegalBasis.EXEC_CONTRATO,
        "finalidade": "identificação do titular em requisições",
    },
    "cpf": {
        "base_legal": LegalBasis.OBRIG_LEGAL,
        "finalidade": "identificação fiscal em contratação",
    },
    "role": {
        "base_legal": LegalBasis.EXEC_CONTRATO,
        "finalidade": "controle de acesso",
    },
    "tipo_gestor": {
        "base_legal": LegalBasis.EXEC_CONTRATO,
        "finalidade": "segregação de fluxos operacionais",
    },
    "tomador_id": {
        "base_legal": LegalBasis.EXEC_CONTRATO,
        "finalidade": "vinculação com o tomador contratante",
    },
    "mfa_enabled": {
        "base_legal": LegalBasis.LEGIT_INTERESSE,
        "finalidade": "segurança da conta",
    },
    "opt_in_marketing": {
        "base_legal": LegalBasis.CONSENTIMENTO,
        "finalidade": "comunicações promocionais (revogável)",
    },
    "opt_in_analytics": {
        "base_legal": LegalBasis.CONSENTIMENTO,
        "finalidade": "métricas de uso (revogável)",
    },
}
