from django.apps import AppConfig


class EmailIngestionConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.email_ingestion"
    label = "email_ingestion"
