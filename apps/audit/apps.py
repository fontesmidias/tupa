from django.apps import AppConfig


class AuditConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.audit"
    label = "audit"

    def ready(self) -> None:  # pragma: no cover - hook Django
        from apps.audit import signals  # noqa: F401
