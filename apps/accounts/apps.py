from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.accounts"
    label = "accounts"

    def ready(self) -> None:
        from apps.accounts import checks  # noqa: F401
        from apps.accounts import signals  # noqa: F401
