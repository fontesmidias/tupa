from django.core.management.base import BaseCommand, CommandError
from django.db import connection


class Command(BaseCommand):
    help = "Valida conectividade com Postgres e presenca da extensao pgvector (ADR-003)."

    def handle(self, *args, **options):
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT version();")
                version = cursor.fetchone()[0]
                self.stdout.write(self.style.SUCCESS(f"Postgres OK: {version}"))

                cursor.execute("SELECT extversion FROM pg_extension WHERE extname = 'vector';")
                row = cursor.fetchone()
                if row is None:
                    raise CommandError(
                        "Extensao 'vector' (pgvector) ausente. "
                        "Rode: CREATE EXTENSION vector; no banco."
                    )
                self.stdout.write(self.style.SUCCESS(f"pgvector OK: v{row[0]}"))
        except CommandError:
            raise
        except Exception as exc:
            raise CommandError(f"Falha ao conectar no Postgres: {exc}") from exc
