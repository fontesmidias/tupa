from django.core.cache import cache
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Valida conectividade com Redis via cache default (ADR-005)."

    def handle(self, *args, **options):
        try:
            cache.set("__healthcheck__", "ok", timeout=5)
            value = cache.get("__healthcheck__")
            if value != "ok":
                raise CommandError(f"Redis respondeu mas round-trip falhou (got {value!r}).")
            cache.delete("__healthcheck__")
            self.stdout.write(self.style.SUCCESS("Redis OK"))
        except CommandError:
            raise
        except Exception as exc:
            raise CommandError(f"Falha ao conectar no Redis: {exc}") from exc
