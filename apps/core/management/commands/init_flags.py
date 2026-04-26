"""Cria/atualiza as 3 feature flags base (Story 1.10, ADR Fatia 1.1).

Idempotente. Sera chamado pelo seed_dev (Story 1.9) no futuro.
"""

from __future__ import annotations

from django.core.management.base import BaseCommand
from waffle.models import Flag

FLAGS = [
    (
        "enable_duplicate_llm_layer",
        "Camada 3 de duplicatas (LLM raciocinador). Fatia 1.1. Desligada no MVP.",
    ),
    (
        "enable_ux_llm_report",
        "Job LLM semanal de relatorio UX (Story 12.4). Fatia 1.1. Liga apos 30d de dados.",
    ),
    (
        "require_mfa_for_rh",
        "Forca MFA TOTP para todos rh_admin (Story 2.5). Fatia 2 por default.",
    ),
]


class Command(BaseCommand):
    help = "Cria/atualiza feature flags base (idempotente)."

    def handle(self, *args, **options):
        for name, note in FLAGS:
            flag, created = Flag.objects.get_or_create(
                name=name,
                defaults={"everyone": False, "note": note},
            )
            if not created and flag.note != note:
                flag.note = note
                flag.save(update_fields=["note"])
            self.stdout.write(
                self.style.SUCCESS(f"{'criada' if created else 'ja existia'}: {name}")
            )
