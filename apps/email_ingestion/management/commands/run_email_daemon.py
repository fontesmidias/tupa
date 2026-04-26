"""Placeholder do daemon IMAP. Implementacao real chega na Story 7.2a."""

from __future__ import annotations

import time

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Daemon IMAP IDLE para ingestao de curriculos (placeholder ate Story 7.2a)."

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.WARNING(
                "gv-email-ingestion placeholder: daemon real sera implementado na Story 7.2a."
            )
        )
        while True:
            self.stdout.write("email-daemon heartbeat (placeholder)")
            time.sleep(60)
