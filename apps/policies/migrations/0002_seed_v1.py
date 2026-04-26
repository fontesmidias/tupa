"""Seed idempotente v1 de Termos + Privacidade (Story 3.4 AC)."""

from __future__ import annotations

from django.db import migrations
from django.utils import timezone


TERMS_V1_MD = """# Termos de Uso — v1.0.0

Uso interno da plataforma gestao-vagas restrito a funcionários autorizados.
Substituível por versão posterior aprovada pelo DPO.
"""

PRIVACY_V1_MD = """# Política de Privacidade — v1.0.0

Tratamos dados pessoais conforme a LGPD. Consulte o DPO para dúvidas.
Substituível por versão posterior aprovada pelo DPO.
"""


def seed(apps, schema_editor):
    PolicyVersion = apps.get_model("policies", "PolicyVersion")
    now = timezone.now()
    PolicyVersion.objects.get_or_create(
        kind="terms",
        version="1.0.0",
        defaults={
            "effective_at": now,
            "full_text_md": TERMS_V1_MD,
            "summary_of_changes_md": "Versão inicial.",
        },
    )
    PolicyVersion.objects.get_or_create(
        kind="privacy",
        version="1.0.0",
        defaults={
            "effective_at": now,
            "full_text_md": PRIVACY_V1_MD,
            "summary_of_changes_md": "Versão inicial.",
        },
    )


def unseed(apps, schema_editor):
    PolicyVersion = apps.get_model("policies", "PolicyVersion")
    PolicyVersion.objects.filter(
        kind__in=["terms", "privacy"], version="1.0.0"
    ).delete()


class Migration(migrations.Migration):
    dependencies = [("policies", "0001_initial")]
    operations = [migrations.RunPython(seed, unseed)]
