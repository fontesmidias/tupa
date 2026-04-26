"""Settings base — compartilhado entre dev/prod/test. ADRs 001, 003, 008."""

from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env(
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, ["localhost", "127.0.0.1"]),
)

environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("SECRET_KEY", default="insecure-dev-key-change-me")
DEBUG = env("DEBUG")
ALLOWED_HOSTS = env("ALLOWED_HOSTS")

FIELD_ENCRYPTION_KEY = env("FIELD_ENCRYPTION_KEY", default="")

# Story 3.6b — email do DPO para notificações de ações LGPD críticas.
DPO_EMAIL = env("DPO_EMAIL", default="")

# Epic 4.0-MVP (Caminho C) — OpenAI GPT-4o-mini para extração de RP.
# Mantemos ANTHROPIC_* para permitir switch via driver no futuro (Amelia opção b).
OPENAI_API_KEY = env("OPENAI_API_KEY", default="")
OPENAI_MODEL_ID = env("OPENAI_MODEL_ID", default="gpt-4o-mini")
OPENAI_PRICE_INPUT_PER_MTOKENS = env.float(
    "OPENAI_PRICE_INPUT_PER_MTOKENS", default=0.15
)
OPENAI_PRICE_OUTPUT_PER_MTOKENS = env.float(
    "OPENAI_PRICE_OUTPUT_PER_MTOKENS", default=0.60
)

ANTHROPIC_API_KEY = env("ANTHROPIC_API_KEY", default="")
ANTHROPIC_MODEL_ID = env("ANTHROPIC_MODEL_ID", default="claude-sonnet-4-5")
ANTHROPIC_PRICE_INPUT_PER_MTOKENS = env.float(
    "ANTHROPIC_PRICE_INPUT_PER_MTOKENS", default=3.0
)
ANTHROPIC_PRICE_OUTPUT_PER_MTOKENS = env.float(
    "ANTHROPIC_PRICE_OUTPUT_PER_MTOKENS", default=15.0
)

AI_LAB_ENABLED = env.bool("AI_LAB_ENABLED", default=False)

DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "waffle",
]

# ADR-012: grafo de 5 camadas (core -> accounts -> dominio -> composicao -> folhas)
LOCAL_APPS = [
    # Camada 1 — core
    "apps.core",
    # Camada 2 — accounts
    "apps.accounts",
    # Camada 3 — dominio
    "apps.requisitions",
    "apps.ai_providers",
    "apps.curriculos",
    "apps.email_ingestion",
    "apps.policies",
    # Camada 4 — composicao
    "apps.vagas",
    "apps.matching",
    # Camada 5 — folhas
    "apps.audit",
    "apps.notifications",
    "apps.telemetry",
    "apps.help",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    "apps.core.middleware.TraceIdMiddleware",
    "apps.core.middleware.DomainExceptionMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "apps.core.middleware.RequestContextMiddleware",
    "apps.core.middleware.AuthRequiredMiddleware",
    "apps.accounts.middleware.CadastroCompletoMiddleware",
    "apps.accounts.middleware.MfaRequiredMiddleware",
    "apps.policies.middleware.PolicyMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "waffle.middleware.WaffleMiddleware",
]

# Story 1.5b — caminhos públicos isentos de AuthRequiredMiddleware.
PUBLIC_PATHS = [
    "/",
    "/auth/entrar/",
    "/auth/codigo/",
    "/auth/mfa/",
    "/healthz",
    "/readyz",
    "/metrics",
    "/admin/login/",
    "/static/",
    "/media/",
]

# Story 2.4 — rotas isentas de CadastroCompletoMiddleware.
BYPASS_PROFILE_PATHS = [
    "/auth/",
    "/admin/",
    "/static/",
    "/media/",
    "/healthz",
    "/readyz",
    "/metrics",
    # Story 5.2 adiciona view real desta rota
    "/gestor/requisicoes/nova/",
    # Story 2.5 — setup MFA precisa ser acessível mesmo sem cadastro completo
    "/conta/seguranca/mfa/",
]

MESSAGE_STORAGE = "django.contrib.messages.storage.session.SessionStorage"

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# ADR-003: Postgres + pgvector
DATABASES = {
    "default": env.db(
        "DATABASE_URL",
        default="postgres://postgres:postgres@localhost:5432/gestao_vagas_dev",
    ),
}

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": env("REDIS_URL_CACHE", default="redis://localhost:6379/1"),
    }
}

DRAMATIQ_BROKER_URL = env("REDIS_URL_BROKER", default="redis://localhost:6379/0")

# Story 2.6 — Sessão Django com cookies seguros (ADR D2.2, NFR13)
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_SECURE = not DEBUG  # True em prod (HTTPS), False em dev local
SESSION_COOKIE_AGE = 60 * 60 * 24 * 7  # 7 dias
SESSION_SAVE_EVERY_REQUEST = True  # rolling: cada request renova o timer
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SECURE = not DEBUG

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "accounts.User"

# auth.E003 suprimido: unicidade de email garantida via UniqueConstraint case-insensitive
# (Lower('email')) em apps.accounts.models.User.Meta.constraints — ADR-009.
SILENCED_SYSTEM_CHECKS = ["auth.E003"]
