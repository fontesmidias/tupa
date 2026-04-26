# gestao-vagas

Sistema interno de Requisicao de Pessoal com ingestao multimodal por IA.

Stack: Django 5.x + HTMX + Tailwind + daisyUI + Alpine.js · Postgres + pgvector · Redis · Dramatiq · PM2 · Docker Swarm.

## Setup local (MVP)

1. **Pre-requisitos:** Python 3.12+, [uv](https://docs.astral.sh/uv/), Docker Desktop, Node.js (para PM2).
2. **Subir infra Docker:**
   ```
   docker run -d --name gv-postgres -p 5433:5432 \
     -e POSTGRES_USER=admin -e POSTGRES_PASSWORD=adminpassword \
     -e POSTGRES_DB=gestao_vagas_dev --restart unless-stopped \
     pgvector/pgvector:pg15

   docker run -d --name gv-redis -p 6379:6379 \
     --restart unless-stopped redis:7-alpine
   ```
3. **Instalar deps + migrar:**
   ```
   uv sync
   cp .env.example .env   # edite conforme seu ambiente
   uv run python manage.py check_db
   uv run python manage.py check_redis
   uv run python manage.py migrate
   uv run python manage.py init_flags
   ```
4. **Rodar (via PM2):**
   ```
   pm2 start ecosystem.config.js
   pm2 logs gv-web
   ```
   Acesse http://localhost:3005/.

   Alternativamente (dev rapido, so web): `uv run python manage.py runserver 3005`.

## Testes

```
uv run pytest --cov=apps --cov-report=term-missing
uv run ruff check apps config tests
uv run ruff format --check apps config tests
uv run mypy apps
```

## Backup local

Script em [deploy/backup/backup.sh](deploy/backup/backup.sh) faz `pg_dump` comprimido em `_backups/`.

```
bash deploy/backup/backup.sh
```

Variaveis de ambiente: `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`, `BACKUP_ROOT` (opcional). Defaults batem com `.env` local.

> Implementacao plena (retencao GFS + mirror MinIO offsite + teste mensal de restore) chega na Story 13.4a/b.

## Feature flags (django-waffle)

- `enable_duplicate_llm_layer` — Camada 3 de duplicatas (Fatia 1.1)
- `enable_ux_llm_report` — Job LLM semanal (Fatia 1.1)
- `require_mfa_for_rh` — MFA obrigatorio para rh_admin (Fatia 2)

Gerenciar via `/admin/waffle/flag/` ou comando `uv run python manage.py init_flags` (idempotente).

## Estrutura de apps (ADR-012 — 5 camadas)

1. `core`
2. `accounts`
3. `requisitions`, `ai_providers`, `curriculos`, `email_ingestion`, `policies`
4. `vagas`, `matching`
5. `audit`, `notifications`, `telemetry`, `help`

Enforcement automatico via `tests/integration/test_architecture.py`.

## Documentacao

- PRD: [docs/prd/](docs/prd/)
- Arquitetura & ADRs: [_bmad-output/planning-artifacts/architecture.md](_bmad-output/planning-artifacts/architecture.md)
- Epics & Stories: [_bmad-output/planning-artifacts/epics.md](_bmad-output/planning-artifacts/epics.md)
