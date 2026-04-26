"""Settings test — pytest-django."""

from .base import *  # noqa: F401,F403

DEBUG = False
ALLOWED_HOSTS = ["*"]
DRAMATIQ_EAGER = True

# Chave Fernet fixa para testes (Story 2.5).
FIELD_ENCRYPTION_KEY = "-F3oEeDso6Lh7pdVkcmgz7TDHy2LtQ48QUZv2ngHKGg="
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

# Story 2.2: backend locmem em tests (usar django.core.mail.outbox).
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
DEFAULT_FROM_EMAIL = "no-reply@gestao-vagas.test"

# SQLite em memória — isola testes de Postgres/pgvector. Story 1.5a.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# Cache local — não precisa Redis em unit tests.
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}


# Story 1.5b: desabilita migrations em unit tests — cria schema via syncdb
# a partir dos models, incluindo models só-de-teste em apps/core/tests/models.py.
class _DisableMigrations:
    def __contains__(self, item: str) -> bool:
        return True

    def __getitem__(self, item: str) -> None:
        return None


MIGRATION_MODULES = _DisableMigrations()
