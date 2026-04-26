---
stepsCompleted:
  - step-01-init
  - step-02-context
  - step-03-starter
  - step-04-decisions
  - step-05-patterns
  - step-06-structure
  - step-07-validation
  - step-08-complete
workflowStatus: complete
completedAt: 2026-04-21
inputDocuments:
  - path: 'docs/prd/'
    type: 'prd-sharded'
    summary: 'PRD v1.0 completo, 16 shards + index.md. Staffing B2G web app, 89 FRs, 54 NFRs, 5 jornadas, stack hipótese Django+Postgres+Redis+Dramatiq+MinIO+Swarm.'
  - path: '_bmad-output/planning-artifacts/prd-validation-report.md'
    type: 'validation-report'
    summary: 'PRD aprovado PASS 5/5 Excellent em 12 checks. Zero gaps críticos.'
  - path: '_bmad-output/planning-artifacts/archive/prd.md'
    type: 'prd-monolithic-archive'
    summary: 'Backup do PRD monolítico pré-shard (fonte histórica).'
workflowType: 'architecture'
project_name: 'gestao-vagas'
user_name: 'Bruno'
communication_language: 'Portugues do brasil'
document_output_language: 'Portugues do brasil'
date: '2026-04-21'
architect: 'Winston (bmad-agent-architect)'
devEnvironmentConstraints:
  local:
    stackConfirmed: 'Django + HTMX monolítico (server-rendered, 1 porta) — ratificado pelo Bruno 2026-04-21 após esclarecimento; Next.js/SPA descartado'
    appPort: 3005
    appPortNote: 'Pode ser ajustada mais tarde. Django servirá portal do gestor + painel RH + endpoints internos nesta mesma porta.'
    postgres:
      status: 'already running on Bruno machine'
      connection: 'localhost (não rodar Postgres em Docker no local; reutilizar existente)'
      credentials: 'a configurar via .env local; ver DATABASE_URL'
    processManager: 'PM2'
    processes:
      - name: 'gv-web'
        port: 3005
        runtime: 'Django via uvicorn/gunicorn'
        role: 'portal gestor + painel RH + endpoints internos'
      - name: 'gv-worker'
        port: null
        runtime: 'Dramatiq worker'
        role: 'consumidor da fila (jobs IA, ingestão e-mail, telemetria)'
      - name: 'gv-email-ingestion'
        port: null
        runtime: 'Python daemon (IMAP IDLE) OU worker webhook-consumer'
        role: 'monitor da caixa curriculos@; só necessário se provedor de e-mail for IMAP. Webhook é consumido pelo gv-web'
    redisLocal:
      decision: 'Docker em local (container único rodando Redis 7-alpine)'
      command: 'docker run -d --name gv-redis -p 6379:6379 redis:7-alpine'
      rationale: 'Isola do host; evita instalação nativa no Windows; paridade com produção (Swarm também rodará Redis 7-alpine); zero configuração adicional.'
    minioLocal:
      decision: 'Filesystem local em dev; MinIO apenas em prod (Swarm)'
      devStorage: 'django-storages FileSystemStorage gravando em ./media/ (gitignored)'
      prodStorage: 'django-storages S3Boto3Storage apontando para MinIO no Swarm'
      rationale: 'Abstração transparente permite dev sem container extra; reduz consumo de RAM na máquina do Bruno; integridade de prod preservada por paridade da interface S3-compatible; MINIO_* e USE_MINIO em .env controlam a troca.'
  vps:
    status: 'especificações a serem fornecidas pelo Bruno mais adiante'
    known:
      - 'Docker Swarm'
      - 'Traefik (roteamento + TLS)'
      - 'Portainer (gestão)'
      - 'Subdomínio apontado para IP da VPS'
    pending: 'CPU, RAM, disco, S.O., versões, rede, segurança, backup existente'
---

# Architecture Decision Document — gestao-vagas

**Arquiteto:** Winston (bmad-agent-architect)
**Solicitante:** Bruno (Coord. RH + Eng. Software — Green House)
**Data início:** 2026-04-21
**Versão:** 0.1 (em construção)

_Este documento é construído colaborativamente, seção por seção, através do workflow bmad-create-architecture. Decisões técnicas são travadas aqui e servem de base para épicos, histórias e implementação._

## Architecture Decisions Log (ADR)

Registro cronológico de cada decisão arquitetural, com **contexto**, **decisão** e **consequências/porquê** — no estilo ADR (Architecture Decision Record). Decisões são imutáveis depois de registradas; mudanças viram uma nova ADR que superseda a anterior.

### ADR-001 — Stack de aplicação: Django 5.x + HTMX (server-rendered monolítico)

- **Data:** 2026-04-21
- **Status:** Accepted
- **Contexto:** PRD precisa entregar portal do gestor (mobile-first), painel RH (kanban + revisão), worker assíncrono, e ingestão de e-mail. Volume baixo (20 req/mês, 10 vagas ativas, 100 tomadores). Bruno é solo-dev. "Amanhã em produção" é ambição declarada. Winston recomendou Django em rodadas anteriores. Bruno levantou brevemente hipótese de SPA (Next.js + API em porta separada) mas ratificou Django monolítico em 2026-04-21 após esclarecimento.
- **Decisão:** Django 5.x como framework único, servindo tanto HTML (templates Django + Jinja quando necessário) quanto endpoints internos de dados. **HTMX** para interatividade cliente (sem SPA). Django Admin customizado (via `django-unfold` ou similar) evitando, porém não para o painel do RH — esse terá UI dedicada.
- **Consequências / Porquê:**
  - ✅ Admin, Auth, ORM, migrations, CSRF, forms, signals — tudo nativo; economiza semanas.
  - ✅ 1 processo HTTP para gerir (PM2 simples).
  - ✅ HTMX cobre 95% das necessidades de UX sem reintroduzir React build pipeline.
  - ⚠ Para telas muito interativas (ex.: player de áudio sincronizado com transcrição na revisão RH), HTMX + Alpine.js será suficiente mas menos polido que uma SPA. Trade-off aceito.
  - ⚠ Se no futuro o portal do candidato (Vision) for público-externo de alto tráfego, pode migrar essa superfície para SPA sem refatorar o backend.

### ADR-002 — Porta única em dev local: 3005

- **Data:** 2026-04-21
- **Status:** Accepted (revisável)
- **Contexto:** Bruno inicialmente sugeriu frontend:3005 + backend:3006; após confirmação, optou por stack monolítica — porta única.
- **Decisão:** Django web process escuta em `localhost:3005` em desenvolvimento. A porta é configurável por `.env` (variável `APP_PORT=3005`) caso precise mudar.
- **Consequências / Porquê:**
  - ✅ Zero CORS, zero cookie cross-origin.
  - ✅ Alinha com convenção "node-like" da máquina do Bruno (familiar com 3000+).
  - ⚠ Porta 3005 é incomum para Django (padrão é 8000); equipe futura precisará dos `.env.example` atualizados.

### ADR-003 — PostgreSQL local: reusar instância existente na máquina do Bruno

- **Data:** 2026-04-21
- **Status:** Accepted
- **Contexto:** Bruno já tem PostgreSQL rodando localmente. Adicionar outro Postgres (via Docker) duplicaria recursos.
- **Decisão:** Django em dev conecta ao Postgres existente em `localhost:5432`. Database dedicada (`gestao_vagas_dev`) e role (`gv_app`) criados. Extensão `pgvector` instalada nessa database (`CREATE EXTENSION IF NOT EXISTS vector;`). Credenciais e DSN em `.env` local (`DATABASE_URL=postgres://gv_app:***@localhost:5432/gestao_vagas_dev`).
- **Consequências / Porquê:**
  - ✅ Menos consumo de RAM/CPU na máquina de dev.
  - ✅ Bruno mantém um único conjunto de ferramentas (pgAdmin/TablePlus) apontando para sua instância existente.
  - ⚠ Precisa garantir que a versão do Postgres existente é ≥ 14 (requisito prático do pgvector e recursos modernos de JSONB). Se for < 14, atualizar.
  - ⚠ Dev não terá paridade 100% com prod (prod rodará Postgres dedicado em Swarm) — risco mínimo dado que diferenças de versão podem ser alinhadas.

### ADR-004 — Gerenciamento de processos em dev: PM2

- **Data:** 2026-04-21
- **Status:** Accepted
- **Contexto:** Bruno já usa PM2 e quer todos os processos do projeto sob essa ferramenta.
- **Decisão:** `ecosystem.config.js` do PM2 na raiz do projeto, com 2–3 apps:
  - `gv-web`: Django via `uvicorn config.asgi:application --port 3005 --reload` (ASGI para futura compatibilidade com websockets/SSE; HTMX pode usar SSE).
  - `gv-worker`: `dramatiq app.queue` consumindo Redis.
  - `gv-email-ingestion`: só se o provedor de e-mail for IMAP IDLE (daemon Python). Se for webhook (Google Pub/Sub, M365 Graph), o webhook entra no `gv-web` — não há 3º processo.
- **Consequências / Porquê:**
  - ✅ `pm2 start ecosystem.config.js` sobe tudo de uma vez; `pm2 logs` centraliza.
  - ✅ Restart automático em falha; hot-reload de código via `--reload` (dev).
  - ✅ Paridade conceitual com prod (em prod os processos viram serviços Swarm, mas o modelo de "múltiplos processos com responsabilidades distintas" é o mesmo).
  - ⚠ PM2 rodando Python é incomum mas funciona bem (PM2 é agnóstico de linguagem para processos long-running).

### ADR-005 — Redis local: Docker dedicado (container único)

- **Data:** 2026-04-21
- **Status:** Accepted
- **Contexto:** Precisamos de Redis em dev (broker Dramatiq + cache de sessão + rate-limit). Bruno optou por Docker em vez de instalação nativa.
- **Decisão:** Redis 7-alpine via Docker em container standalone. Comando: `docker run -d --name gv-redis -p 6379:6379 --restart unless-stopped redis:7-alpine`. Conexão em `.env`: `REDIS_URL=redis://localhost:6379/0` (broker), `REDIS_URL_CACHE=redis://localhost:6379/1` (cache Django).
- **Consequências / Porquê:**
  - ✅ Zero instalação no host Windows; isolamento completo.
  - ✅ Paridade total com Swarm (prod vai rodar `redis:7-alpine` também).
  - ✅ `docker start gv-redis` / `docker stop gv-redis` controla ciclo de vida sem PM2.
  - ⚠ Bruno precisa ter Docker Desktop rodando para desenvolver. Se desligar, `gv-worker` começa a falhar — erro claro e recuperável.

### ADR-006 — Object storage: filesystem em dev, MinIO em prod (abstração via django-storages)

- **Data:** 2026-04-21
- **Status:** Accepted
- **Contexto:** Uploads multimodais (áudio, PDF, imagens, currículos) precisam ser armazenados. MinIO é S3-compatible e será usado em prod no Swarm. Rodar MinIO em dev aumenta consumo de RAM sem ganho significativo.
- **Decisão:** Em **dev**, usar `FileSystemStorage` do Django, gravando em `./media/` (gitignored). Em **prod**, usar `django-storages` com backend `storages.backends.s3.S3Storage` apontando para MinIO. Backend é selecionado por variável de ambiente (`USE_MINIO=true` ativa MinIO).
  - Estrutura de buckets em prod: `gv-uploads` (originais do gestor), `gv-curriculos` (currículos ingeridos), `gv-ux-reports` (relatórios LLM semanais). Política de lifecycle define retenção por bucket conforme NFR30 e decisão DPO pendente.
- **Consequências / Porquê:**
  - ✅ Dev leve — arquivos viram arquivos no disco, inspecionáveis diretamente.
  - ✅ Abstração transparente no código — `FileField.save()` funciona igual em ambos os ambientes.
  - ✅ Prod mantém integridade, versionamento e retention via lifecycle policies do MinIO.
  - ⚠ Testes em dev não capturam edge cases específicos de S3/MinIO (ex.: permissões, multipart upload, pre-signed URLs). Mitigação: ao tocar fluxos de storage, rodar MinIO em Docker pontualmente para teste antes de deploy.
  - ⚠ Pre-signed URLs (para compartilhar arquivo com link temporário) só funcionam com MinIO — se a feature for necessária em dev, ativar MinIO localmente.

### ADR-007 — VPS de produção: especificações pendentes

- **Data:** 2026-04-21
- **Status:** Proposed (pendente de dados)
- **Contexto:** Bruno informará CPU/RAM/disco/S.O./versões/rede da VPS mais tarde. O que já é sabido: tem Docker + Swarm + Traefik + Portainer instalados; subdomínio apontado para IP público.
- **Decisão:** Reservar seção "Deployment — VPS Production" a ser preenchida quando as especs chegarem. Até lá, arquitetura de prod usa os valores declarados no PRD (Docker Swarm, Traefik, Postgres 16 dedicado, Redis 7, MinIO, Loki+Grafana+Prometheus). Será confirmado se a VPS suporta esse stack completo ou se algum serviço precisa ir para provedor externo (ex.: Grafana Cloud free, Redis Cloud free, Backblaze B2 para backup offsite).
- **Consequências / Porquê:**
  - ✅ Documento permanece vivo — espaço reservado para especs reais em vez de suposições.
  - ⚠ Dimensionamento (workers × vCPU) depende de quanto a VPS oferece; decisão fica em aberto.

## Project Context Analysis

### Requirements Overview

**Functional Requirements:**
89 FRs em 13 áreas (Acesso/Identidade; Submissão; Ingestão de CVs; Extração IA/Revisão; Duplicatas; Vagas/Matching; Painel RH; Providers Plugáveis; Notificações; Auditoria/Compliance/Políticas; Help Contextual; Telemetria; Configuração/Admin). Mapeamento FR↔Jornada formalizado no Appendix A do PRD. ~61 FRs traceáveis diretamente a jornadas narradas; ~28 FRs transversais (compliance, help, telemetria, config) que o próprio PRD marca como "épicos independentes".

**Non-Functional Requirements:**
54 NFRs em 10 categorias. Os que mais moldam a arquitetura:
- NFR2: pipeline multimodal ≤ 3 min p95 / ≤ 8 min p99 — exige fila assíncrona robusta.
- NFR7-8: 10× volume sem degradação; 50k currículos sem perder latência de match — pgvector indexing plan.
- NFR11-19: segurança (TLS 1.3, link mágico TTL, cookies HttpOnly, criptografia em repouso para campos sensíveis, rate-limiting, hash-chain SHA-256).
- NFR20-25: uptime 99%, backup diário, RPO 24h, RTO 4h, restore testado trimestralmente, idempotência de jobs.
- NFR26-33: LGPD hardcore — ROPA, consentimento granular, revisão humana obrigatória, anonimização, export LAI mascarado.
- NFR34-36: custo ≤ R$0,15/vaga p95; alerta 80% cota; troca de provider em runtime.
- NFR37-40: observabilidade estruturada (JSON + trace_id).
- NFR45-49: responsividade desde 360px, WCAG 2.1 AA (meta com tolerância), PT-BR.
- NFR50-54: deploy zero-downtime, cobertura ≥70% nas camadas críticas, feature flags.

**Scale & Complexity:**
- Primary domain: full-stack web monolítico (Django + HTMX) + workers assíncronos (Dramatiq) + e-mail ingestion.
- Complexity de arquitetura: Média (CRUD + fila + LLM + storage, volume baixo, sem multi-tenant físico).
- Complexity de domínio: Alta (LGPD/LAI/B2G, AI ethics, multi-provider, compliance densa).
- Estimated architectural components (MVP): 1 Django web, 1 Dramatiq worker, 1 e-mail ingestion worker (condicional), Postgres+pgvector, Redis, object storage (filesystem dev / MinIO prod), SMTP, providers de IA plugáveis (OCR/Vision/Áudio/LLM).

### Technical Constraints & Dependencies

**Declaradas e travadas:**
- Django 5.x + HTMX + Tailwind (ADR-001)
- Porta 3005 em dev (ADR-002)
- PostgreSQL local reutilizado (ADR-003)
- PM2 orquestrando processos em dev (ADR-004)
- Redis 7-alpine em Docker em dev (ADR-005)
- Filesystem em dev + MinIO em prod (ADR-006)
- VPS em Docker Swarm + Traefik + Portainer (ADR-007 pendente de specs)

**Pendentes (impactam implementação mas não bloqueiam arquitetura):**
- Provedor de e-mail da Green House (define ingestão via webhook vs IMAP IDLE).
- Especificações completas da VPS (dimensionamento de workers).
- 3 pendências DPO do Appendix B do PRD (base legal match IA, retenção CVs, LAI masking).
- API keys de providers iniciais (Mistral, Groq, Claude, OpenAI, ocr.space).

**Dependências externas confirmadas:**
- LLM: Claude (Anthropic), Mistral, Groq — plugáveis.
- Transcrição áudio: Groq Whisper (default free-tier), OpenAI Whisper.
- OCR/Vision: Mistral Vision (default), ocr.space (fallback).
- pgvector (extensão Postgres), Redis 7, MinIO (S3-compatible), SMTP.
- Evolution API (Growth, não MVP).

### Cross-Cutting Concerns Identified

Concerns que atravessam múltiplos componentes e exigem tratamento arquitetural explícito desde o dia 1:

1. **Auditoria hash-encadeada**: middleware + Django signals capturam toda escrita → grava em `audit_log` com hash SHA-256 encadeado. Comando de integridade.
2. **Autorização por "círculo"**: QuerySet mixin + custom manager no ORM filtra automaticamente por perfil (rh_admin, rh_operator, gestor) e por círculo do gestor (tomador/departamento/coordenação).
3. **Providers de IA plugáveis**: `AiProvider` Protocol + registry em memória + `ai_provider_config` table encriptada + health-check + fallback automático + notificação por e-mail.
4. **Observabilidade**: logger estruturado JSON + `trace_id` propagado request→job→provider; métricas Prometheus; logs Loki; dashboards Grafana.
5. **Feature flags**: django-waffle ou tabela flag simples — governam Camada 3 de duplicatas, job LLM de telemetria, ingestão por e-mail, etc.
6. **LGPD enforcement**: campos sensíveis com `EncryptedField`; `policy_version` com modal de aceite; endpoints de direitos do titular; anonimização em vez de exclusão.
7. **Idempotência de jobs**: chaves derivadas de hash de conteúdo; dedup por Message-Id em e-mail ingestion; workers Dramatiq com retry + DLQ.
8. **Help contextual**: tabela `help_snippet` editável; template tag injetando tooltips; middleware de telemetria.
9. **Telemetria UX**: tabela particionada por semana; job semanal LLM produz relatório em markdown; dashboard /admin/ux-insights.
10. **Rate-limiting e anti-abuse**: link mágico rate-limited por IP e e-mail; MFA opcional para RH; detection de IP atípico.

## Starter Template Evaluation

### Primary Technology Domain

**Full-stack web monolítico** — Django 5.x + HTMX + Tailwind. Já travado em ADR-001.

### Starter Options Considered

**Opção 1 — cookiecutter-django (pydanny/django-cookiecutter):**
- Maduro (~12k ⭐), manutenção excelente.
- Inclui Django 5.x, Postgres, Redis, Celery, Docker, GitHub Actions CI, django-allauth, django-environ, ruff, mypy, pytest, pre-commit.
- **Desvantagens para nosso caso:** vem com Celery (decidimos Dramatiq), django-allauth (vamos usar link mágico custom), social login, etc. — muita coisa pra remover.

**Opção 2 — falco-cli (Tobi DEGNON):**
- Jovem (~600 ⭐, crescendo), feito especificamente para Django + HTMX + Tailwind.
- Mais enxuto. Não inclui Dramatiq nem pgvector.
- **Vantagens:** fit natural para nosso stack. **Desvantagens:** menos battle-tested em produção pesada.

**Opção 3 — Bootstrap manual (recomendada):**
- `django-admin startproject` + estrutura custom baseada em convenções Winston.
- Total controle; zero baggage não desejado.
- Custo: ~1 dia para configurar settings, CI, lint, pre-commit, testes.

### Selected Starter: Bootstrap Manual (Opção 3)

**Rationale for Selection:**

1. **Decisões muito específicas:** Dramatiq (não Celery); link mágico custom (não allauth); pgvector; providers plugáveis; audit hash-chain; ingestão e-mail swappable. Qualquer cookiecutter traz features que vamos remover — a "economia" vira noise.
2. **Solo-dev:** Bruno precisa entender 100% do código desde o dia 1. Cookiecutter costuma gerar arquivos que ninguém lê até dar problema.
3. **Estrutura de apps é convenção clara** (ver ADR-008 a ser criada) — `config/` + `apps/` bem delimitados, sem mágica.
4. **Falco-cli é 2º lugar:** se mudássemos de ideia, ele é a escolha. Mas pgvector + Dramatiq + providers custam 1h adicional sobre o bootstrap — não compensa a economia de scaffolding.

### Initialization Command (vira 1ª User Story do MVP)

```bash
# Na raiz do repo (já existe)
mkdir -p apps config deploy tests

# Bootstrap com uv (ferramenta moderna de packaging Python)
uv init gestao-vagas --python 3.12

# Dependências principais
uv add django~=5.1 \
       "psycopg[binary]~=3.2" \
       pgvector~=0.3 \
       "dramatiq[redis]~=1.17" \
       redis~=5.0 \
       django-environ~=0.11 \
       django-htmx~=1.19 \
       django-cryptography-django5~=2.2 \
       django-storages[s3]~=1.14 \
       django-tailwind~=3.8 \
       django-waffle~=4.2 \
       uvicorn~=0.30 \
       gunicorn~=23.0 \
       whitenoise~=6.7 \
       structlog~=24.4 \
       sentry-sdk~=2.15 \
       anthropic~=0.40 \
       openai~=1.50 \
       groq~=0.11 \
       mistralai~=1.2

# Dependências de dev
uv add --group dev pytest-django~=4.9 pytest-cov~=5.0 ruff~=0.7 mypy~=1.12 pre-commit~=4.0 ipython~=8.28

# Criar projeto Django + apps
uv run django-admin startproject config .

for app in core accounts requisitions ai_providers matching audit notifications telemetry help curriculos; do
  mkdir -p apps/$app
  uv run python manage.py startapp $app apps/$app
done
```

**Architectural Decisions Provided by Manual Bootstrap:**

**Language & Runtime:** Python 3.12, Django 5.1+ ASGI (via uvicorn em dev/gunicorn em prod).

**Styling Solution:** Tailwind CSS via `django-tailwind` (Node.js executado só para build do CSS; não há bundler JS de frontend).

**Build Tooling:** `uv` como package manager (~10× mais rápido que pip); Ruff como linter/formatter; Mypy para tipagem estática opcional.

**Testing Framework:** pytest-django + pytest-cov. Cobertura alvo ≥70% nas camadas críticas (NFR52).

**Code Organization:** convenção `apps/<domínio>` (dez apps iniciais delimitados por bounded context); `config/` para settings/urls/asgi; `deploy/` para Dockerfile + compose + Swarm stack; `tests/` para testes de integração/smoke cross-app.

**Development Experience:** `ecosystem.config.js` (PM2) com 2-3 apps (gv-web, gv-worker, [gv-email-ingestion condicional]); `.env` local com dotenv via django-environ; pre-commit hooks rodando ruff + mypy + pytest em cada commit.

**Note:** A execução deste comando (com ajustes de versões mais atuais ao momento da execução) será a **primeira User Story** do MVP — "Setup: bootstrap do projeto gestao-vagas". Toda estrutura subsequente parte daí.

## Core Architectural Decisions

Decisões técnicas específicas que complementam as ADRs anteriores. Cada item tem decisão + porquê. Ordem segue categorias BMAD: Data / Auth & Security / API & Communication / Frontend / Infrastructure & Deployment.

### Decision Priority Analysis

**Critical Decisions (Block Implementation):** D1.1 migrations, D1.4 hash-chain, D1.5 pgvector HNSW, D2.1 User model, D2.3 QuerySet mixin, D2.5 criptografia em repouso, D3.4 idempotência de jobs, D5.9 migrations em deploy.

**Important Decisions (Shape Architecture):** todas as D4 (frontend), D5.1-5.7 (infra+deploy), D2.2/2.6/2.7 (auth details).

**Deferred Decisions (Post-MVP):** OpenTelemetry (fica para Fase 2 se distribuição ficar crítica); WebSockets full (SSE cobre MVP); multi-região.

### Data Architecture

- **D1.1 — Migrations:** Django migrations nativas. Toda migration documentada; schema ≠ data migrations. Histórico imutável em prod. **Porquê:** battle-tested, zero ferramenta extra.
- **D1.2 — Cache:** Redis como cache Django via `django-redis` (DB 1). TTL default 5 min (leituras pesadas), 15 min (sessões de link mágico).
- **D1.3 — Validação:** Django Forms para views; Pydantic v2 para schemas de extração IA. **Porquê:** Pydantic é o padrão Python moderno com suporte nativo a LLM tool-use / JSON schema.
- **D1.4 — Audit log hash-chain:** tabela `audit_log` com `hash_prev VARCHAR(64)` + `hash_curr VARCHAR(64)`. `hash_curr = sha256(hash_prev || json_payload)`. Signal `post_save` em modelos auditáveis. Comando `manage.py verify_audit_chain`. **Porquê:** implementação clara, verificável, sem trigger SQL obscuro.
- **D1.5 — Embeddings (pgvector):** coluna `embedding vector(768)` em `requisicao`. Índice HNSW com `vector_cosine_ops`. **Porquê:** HNSW = melhor recall × velocidade para < 1M registros; 768 casa com Mistral embed. Se trocar provedor de embedding, migration de dimensão.

### Authentication & Security

- **D2.1 — Modelo User:** `AbstractBaseUser` customizado em `apps.accounts.models.User`. PK UUID (não AutoField — evita enumeração). Atributos custom: `email` (unique, identificador), `tipo_gestor` (enum A/B/C), `tomador_id`, `circulo_id`, `anonimizado_em`. **Porquê:** controle total sobre fields e validações; requisitos LGPD exigem anonimização-por-default.
- **D2.2 — Session vs Token:** sessões Django com cookie `HttpOnly + Secure + SameSite=Lax`. Zero JWT no MVP (não há API pública). **Porquê:** sessões são mais simples e seguras para uso interno.
- **D2.3 — Autorização:** custom QuerySet mixin + manager (`RequisicaoManager.for_user(user)`) filtra por círculo automaticamente. Decorators `@require_role('rh_admin')` em views. Sem `django-guardian`. **Porquê:** modelo de círculo é simples o suficiente; guardian seria overhead.
- **D2.4 — MFA:** `django-otp` com TOTP. Opt-in por conta; obrigatório para `rh_admin` em prod via feature flag.
- **D2.5 — Criptografia em repouso:** `EncryptedCharField`/`EncryptedTextField` em `apps.core.fields` (Fernet nativo, marcador `enc::`) aplicados a: `User.cpf`, `User.mfa_secret`, e (futuro Epic 4) `AiProviderConfig.api_key`. Chave em `.env` (`FIELD_ENCRYPTION_KEY`). **Rotação de chave:** `@lru_cache` em `_get_fernet()` implica **rotação exige restart do processo** (PM2 `reload` serve). Até suporte multi-chave ser implementado, documentar rotação como operação manual coordenada com janela de manutenção. `manage.py check --deploy` bloqueia boot em prod sem a chave (`accounts.E002`).
- **D2.6 — Rate-limiting:** `django-ratelimit` em views de auth (5 solicitações de link mágico por IP+email em 10 min — NFR18).
- **D2.7 — CSP e headers:** `django-csp` + middleware aplica HSTS, X-Content-Type-Options, X-Frame-Options, Referrer-Policy. Dev usa CSP report-only; prod é restritiva.

### API & Communication Patterns

- **D3.1 — URLs internas:** `apps/<app>/urls.py` incluídas em `config/urls.py`. Namespacing por app (`requisitions:detail`). Endpoints HTMX retornam partials HTML, não JSON.
- **D3.2 — Webhooks externos:** `/webhooks/email-inbound` autenticado por segredo compartilhado em header + idempotência por `Message-Id`. `/webhooks/whatsapp` em Growth.
- **D3.3 — Error handling:** views retornam `HttpResponseBadRequest`/`Http404`/`HttpResponseServerError` com templates `errors/<code>.html`. Views HTMX adicionam `HX-Trigger` header com toast JSON para alertas cliente.
- **D3.4 — Idempotência de jobs:** chave = `sha256(json.dumps(payload, sort_keys=True))`. Tabela `job_execution_log(key, result, executed_at)` previne re-execução.
- **D3.5 — Filas Dramatiq:** 3 filas lógicas (`urgent`, `default`, `background`); DLQ configurada; notificação ao RH em DLQ full.

### Frontend Architecture

- **D4.1 — Interatividade:** HTMX para requests parciais + Alpine.js para estado local (menus, modais, toggles). Zero React/Vue.
- **D4.2 — Player de áudio sincronizado:** `wavesurfer.js` (vanilla) na tela de revisão RH; carregado sob demanda.
- **D4.3 — Upload multimodal:** `tus-js-client` + servidor TUS (`django-tus` ou equivalente) para uploads > 5MB resumíveis. Upload simples para < 5MB.
- **D4.4 — Notificações in-app:** SSE (Server-Sent Events) via Django ASGI + HTMX SSE extension. Sem WebSocket no MVP.
- **D4.5 — Design system:** Tailwind CSS + `daisyUI`. **Porquê:** daisyUI reduz CSS boilerplate e garante consistência visual.
- **D4.6 — Ícones:** `heroicons` via template tags Django.

### Infrastructure & Deployment

- **D5.1 — CI/CD:** GitHub Actions — `pr-checks.yml` (lint+test+cov) e `deploy-prod.yml` (tag/merge main → build → push registry → deploy Swarm via SSH + `docker stack deploy`).
- **D5.2 — Container registry:** GitHub Container Registry (ghcr.io) — gratuito para repos privados.
- **D5.3 — Secrets:** `docker secret` em prod (Swarm native). `.env` gitignored em dev. Futuro upgrade: SOPS + age se equipe crescer.
- **D5.4 — Observabilidade:** Loki (logs) + Prometheus (métricas) + Grafana (dashboards), todos no Swarm. Dashboards pre-configurados: latência pipeline, falhas por provider, uso de cota, tamanho fila, uptime.
- **D5.5 — Tracing:** `structlog` com `trace_id` via contextvars. Sem OpenTelemetry no MVP.
- **D5.6 — Sentry:** `sentry-sdk` instalado; DSN vazio em dev; obrigatório em prod.
- **D5.7 — Backup:** cronjob host (fora do Swarm): `pg_dump` + `mc mirror` → Backblaze B2 ou Wasabi. Rotação 30d diários + 6m semanais. Restore testado trimestralmente.
- **D5.8 — Health checks:** `/healthz` (público, 200 + hash commit); `/readyz` (checa DB + Redis + MinIO + providers). Traefik usa `/healthz` para liveness.
- **D5.9 — Migrations em deploy:** job pre-deploy roda `manage.py migrate --check`, aborta se inconsistente. Migrations destrutivas bloqueadas por default — requerem flag explícita.
- **D5.10 — Zero-downtime deploy:** Swarm rolling update — `max-parallel: 1`, `monitor: 60s`, `failure-action: rollback`.

### Decision Impact Analysis

**Implementation Sequence (ordem sugerida de histórias):**

1. **Setup/Bootstrap** — comando da seção Starter (ADR/starter).
2. **Infra local** — PM2 ecosystem, Redis Docker, Postgres DB/role/extension.
3. **User model + Auth link mágico** — D2.1, D2.2, D2.5, D2.6.
4. **Audit log hash-chain** — D1.4 (antes de qualquer model auditável).
5. **QuerySet mixin + permissions** — D2.3.
6. **Pipeline IA + providers plugáveis** — D1.5, D3.4, ADR-001.
7. **Submissão multimodal + revisão RH** — D4.2, D4.3, D4.4.
8. **Matching + duplicatas** — D1.5.
9. **Observabilidade + health + deploy** — D5.4-5.10.

**Cross-Component Dependencies:**

- D1.4 (audit hash-chain) bloqueia toda escrita — precisa existir antes de features de escrita.
- D2.1 (User customizado) bloqueia migrations subsequentes — precisa ser a 1ª migration após `auth` / `contenttypes`.
- D5.7 (backup) depende de D5.3 (secrets) para credenciais de B2/Wasabi.
- D4.4 (SSE) depende de ASGI (uvicorn/gunicorn+uvicorn-workers) — já decidido em ADR-004.
- D1.5 (pgvector HNSW) precisa de migration que cria a extensão antes do índice — ordem importa.

## Implementation Patterns & Consistency Rules

### Pattern Categories Defined

Cerca de 15 áreas onde AI agents podem divergir: naming, estrutura de apps, assinatura de providers plugáveis, formatos de erro, commits, convenções HTMX. Esta seção fecha todas.

### Naming Patterns

**Database (Django ORM padrão):**
- Tabelas geradas pelo Django (`<app>_<modelo>`); `Meta.db_table` só quando necessário (ex.: `audit_log`).
- Colunas `snake_case`. FK: `<nome_singular>_id` (padrão Django).
- Índices com nome explícito (`idx_<tabela>_<colunas>`).
- Constraints com nome explícito (`uq_<tabela>_<colunas>`).
- Enums via `models.TextChoices`, constantes `UPPER_SNAKE`.

**Code:**
- Python: PEP 8 + Ruff. `snake_case` funções/variáveis; `PascalCase` classes; `UPPER_SNAKE` constantes.
- Django apps em `apps/<dominio>` (snake_case).
- Managers: `<Modelo>Manager(models.Manager)`; QuerySets: `<Modelo>QuerySet(models.QuerySet)`.
- Dramatiq actors: verbo no imperativo (`process_upload`, `extract_requirements`, `check_duplicates`).
- Templates: `<app>/<acao>.html`; partials HTMX em `<app>/_partials/<nome>.html`.

**URLs:**
- Path: kebab-case em PT-BR (`/requisicoes/<uuid>/em-revisao/`).
- Name: `<app>:<acao>` (`requisitions:detail`).
- Param kinds sempre `<uuid:pk>` (nunca IDs incrementais expostos).

**HTMX:**
- `hx-target` semântico, nunca IDs genéricos.
- `hx-swap` default `innerHTML`; explicitar quando diferente.
- Indicator: `hx-indicator=".spinner"` padronizado.

### Structure Patterns

**Project Organization:**
```
gestao-vagas/
├── apps/{core,accounts,requisitions,ai_providers,matching,curriculos,email_ingestion,audit,notifications,telemetry,help,policies}/
├── config/{settings/,urls.py,asgi.py,wsgi.py,dramatiq.py}
├── deploy/{Dockerfile,docker-compose.dev.yml,docker-compose.stack.yml}
├── tests/{integration/,smoke/}
├── static/, media/ (gitignored), templates/
├── docs/ (PRD sharded)
├── _bmad-output/ (arquitetura + validation)
├── .env.example, .gitignore
├── ecosystem.config.js  (PM2)
├── manage.py, pyproject.toml, uv.lock, README.md
```

**Por app:**
```
apps/<app>/
├── admin.py, apps.py, urls.py, views.py, models.py, managers.py, forms.py
├── services.py        # lógica de domínio (NÃO na view nem no model)
├── signals.py         # post_save hooks (audit, notif)
├── jobs.py            # Dramatiq actors
├── schemas.py         # Pydantic v2 (I/O LLM, validação estruturada)
├── migrations/
├── templates/<app>/, static/<app>/
└── tests/{test_models.py,test_views.py,test_services.py,test_jobs.py}
```

**Regra forte:** lógica de domínio vai em `services.py`; views orquestram HTTP; models guardam dados. Facilita testes e reuso por jobs.

### Format Patterns

**Respostas HTMX:**
- Partials HTML (`_partials/<nome>.html`).
- Headers: `HX-Trigger: {"gv:toast": {...}}` dispara eventos cliente.
- Erros: `HttpResponseBadRequest` + partial de erro + toast.

**Webhooks:**
- Sucesso: `200 OK`, body `{"ok": true, "request_id": "<uuid>"}`.
- Validação: `400` com `{"error": "<msg>", "code": "<code>"}`.
- Auth fail: `401`.
- Idempotência hit: `200 OK` com `{"ok": true, "duplicate": true}`.

**Payload de jobs:**
- JSON-serializável; UUIDs como string; datetime como ISO 8601 UTC.
- `meta.idempotency_key` sempre presente.

**Exceptions internas:**
- Custom em `apps/core/exceptions.py`: `ProviderUnavailable`, `ExtractionFailed`, `DuplicateDetected`, `ConsentRequired`, `DomainValidationError`.
- `logger.exception(event, extra={...})` — structlog formata JSON.

**Datetime:**
- DB timezone-aware (`USE_TZ = True`), UTC.
- UI via `|localtime|date:"..."` em `America/Sao_Paulo`.

### Communication Patterns

**Signals custom (`apps/core/signals.py`):**
- `requisition_approved`, `duplicate_detected`, `provider_fallback_triggered`, `policy_updated`, `consent_revoked`.
- Nome: `<noun>_<past_verb>`.
- Payload: dataclass em `apps/core/events.py` (imutável, tipado).
- Handlers em cada app relevante; nunca em `apps.py` (evita side effects de import).

**Logging:**
- `structlog` com JSON em prod, console-pretty em dev.
- Campos obrigatórios: `timestamp`, `level`, `event`, `trace_id`, `user_id` (hash quando aplicável).
- Níveis: DEBUG (dev), INFO (marcos), WARNING (recuperável), ERROR (ação humana), CRITICAL (pager).
- Contexto via `structlog.contextvars.bind_contextvars(trace_id=..., user_id=...)`.

### Process Patterns

**Error handling em views:**
- Domain exceptions interceptadas por `DomainExceptionMiddleware` (`apps/core/middleware.py`).
- Generic exceptions → template `500.html` com request ID visível.
- 404 custom com CTA "voltar ao painel".

**Loading states:**
- HTMX indicator com DaisyUI spinner (`loading loading-spinner loading-md`).
- Uploads assíncronos → status via SSE em banner top-of-page.

**Retry (jobs):**
- Dramatiq default: `@retry(max_retries=3, min_backoff=1000, max_backoff=30000)`.
- Provider IA: retry com backoff + fallback após 3 falhas seguidas.
- Audit log writes: retry infinito com alerta após 10.

**Authentication flow:**
- `AuthRequiredMiddleware` exceto rotas públicas (`/auth/`, `/webhooks/`, `/healthz`).
- `request.user.is_cadastro_completo` controla redirect para completar perfil.

**Validation timing:**
- Forms síncronos no submit.
- Pipeline IA assíncrono; resultados validados por Pydantic antes de persistir.

### Enforcement Guidelines

**All AI Agents MUST:**

1. Rastrear cada commit a FR/Story. Formato: `<tipo>(<area>): <msg>\n\nRefs: FR27, NFR2`. Tipos: `feat|fix|refactor|test|docs|chore|ops`.
2. Escrever testes antes de marcar história done. Cobertura ≥70% nas camadas críticas.
3. Nunca colocar lógica de domínio em views ou models — vai para `services.py`.
4. Nunca strings mágicas — usar `TextChoices`.
5. Nunca bypassar audit log.
6. Nunca hardcodar API key — `django-environ` + `FIELD_ENCRYPTION_KEY`.
7. Nunca `print()` — sempre `structlog.get_logger(__name__)`.
8. Rodar ruff + mypy + pytest pre-PR; pre-commit ativo.

**Pattern Enforcement:**
- Ruff zero violations no CI.
- Mypy strict em `services.py`, `schemas.py`, `jobs.py`; tolerância maior em templates/admin.
- GitHub Actions bloqueia merge em falha.
- Review humano (ou Amelia) checa padrões não-lintáveis.

### Pattern Examples

**Good — view HTMX com service:**
```python
# apps/requisitions/views.py
@require_role_any('gestor', 'rh_admin', 'rh_operator')
def detail(request, pk):
    req = get_object_or_404(Requisicao.objects.for_user(request.user), pk=pk)
    return render(request, 'requisitions/detail.html', {'req': req})

@require_role_any('rh_admin', 'rh_operator')
def review_approve(request, pk):
    req = get_object_or_404(Requisicao.objects.for_user(request.user), pk=pk)
    try:
        services.approve_requisition(req, user=request.user)
    except DomainValidationError as e:
        return render(request, 'requisitions/_partials/error_banner.html', {'error': str(e)}, status=400)
    response = render(request, 'requisitions/_partials/status_badge.html', {'req': req})
    response['HX-Trigger'] = json.dumps({'gv:toast': {'type': 'success', 'message': 'Requisição aprovada.'}})
    return response
```

**Good — service encapsulando o porquê:**
```python
# apps/requisitions/services.py
def approve_requisition(req: Requisicao, *, user: User) -> None:
    if req.status != RequisitionStatus.PENDING_REVIEW:
        raise DomainValidationError('Requisição não está em revisão.')
    if req.low_confidence_fields_count > 0 and not req.all_fields_reviewed:
        raise DomainValidationError('Há campos de baixa confiança ainda não revisados.')
    req.status = RequisitionStatus.APPROVED
    req.approved_by = user
    req.approved_at = timezone.now()
    req.save()
    signals.requisition_approved.send(sender=Requisicao, req=req, actor=user)
```

**Anti-pattern — lógica na view:**
```python
# ❌ Nunca
def review_approve(request, pk):
    req = Requisicao.objects.get(pk=pk)
    req.status = 'approved'  # string mágica!
    req.approved_by = request.user
    req.approved_at = timezone.now()
    req.save()
    # transição de status sem validação de domínio nem sinal
```

### ADR-008 — Typing estático: django-stubs + mypy configurado (pós-feedback Amelia)

- **Data:** 2026-04-21
- **Status:** Accepted
- **Contexto:** Step 5 definiu "mypy strict em services.py, schemas.py, jobs.py". Amelia (Dev) apontou que sem `django-stubs` a integração com ORM gera `# type: ignore` em todo lugar (QuerySet, `.objects.filter()`, `select_related`).
- **Decisão:**
  - Adicionar ao `uv add --group dev`: `django-stubs[compatible-mypy]~=5.1`, `mypy~=1.12`.
  - Arquivo `mypy.ini` na raiz:
    ```ini
    [mypy]
    plugins = mypy_django_plugin.main
    python_version = 3.12
    strict = False
    warn_unused_ignores = True
    warn_redundant_casts = True

    [mypy.plugins.django-stubs]
    django_settings_module = "config.settings.dev"

    [mypy-apps.*.services]
    strict = True

    [mypy-apps.*.schemas]
    strict = True

    [mypy-apps.*.jobs]
    strict = True
    ```
  - Strict só nas 3 camadas críticas (services/schemas/jobs); resto do projeto tem checagem leve.
- **Consequências / Porquê:**
  - ✅ ORM tipado corretamente; QuerySets, Managers, Meta todos cobertos pelo plugin.
  - ✅ Onde tipagem realmente importa (domínio, validação Pydantic, jobs) temos strict.
  - ⚠ Templates, admin.py, migrations ficam tolerantes — não vale o esforço.
  - ⚠ Todo PR que tocar services/schemas/jobs exige `uv run mypy apps/<app>/` verde.

### ADR-009 — Convenção de `name=` em URLs: snake_case (path fica kebab-case em PT-BR)

- **Data:** 2026-04-21
- **Status:** Accepted
- **Contexto:** Step 5 especificou path `/requisicoes/<uuid>/em-revisao/` (kebab-case PT-BR). Amelia apontou que o atributo `name=` precisa de convenção própria para `{% url %}` e `reverse()` ficarem consistentes.
- **Decisão:**
  - **Path (URL visível ao usuário):** kebab-case em PT-BR → `/requisicoes/<uuid:pk>/em-revisao/`.
  - **Name (identificador interno):** snake_case em inglês com namespace do app → `requisitions:em_revisao` NÃO; **`requisitions:mark_in_review`** (verbo canônico inglês).
  - Regra: path fala com o usuário (PT-BR amigável); name fala com o desenvolvedor (inglês consistente). Templates: `{% url 'requisitions:mark_in_review' pk=req.pk %}` sempre. Tests: `reverse('requisitions:mark_in_review', kwargs={'pk': req.pk})`.
- **Consequências / Porquê:**
  - ✅ Usuário vê URL legível em PT-BR; dev lê código em inglês (padrão do ecossistema).
  - ✅ Zero ambiguidade sobre qual chave usar em `{% url %}`.
  - ⚠ Exige disciplina de mapeamento path↔name em cada `urls.py`.

### ADR-010 — Decorator `@idempotent_actor` para Dramatiq

- **Data:** 2026-04-21
- **Status:** Accepted
- **Contexto:** Step 4 D3.4 definiu "chave idempotente = sha256(json.dumps(payload, sort_keys=True)) em `meta.idempotency_key`". Amelia apontou que `meta` não é campo nativo do Dramatiq Message — precisa de wrapper para evitar boilerplate.
- **Decisão:** Criar `apps/core/tasks.py` com decorator `@idempotent_actor` que:
  - Registra actor Dramatiq (`@dramatiq.actor(...)` internamente).
  - Computa chave idempotente do payload antes de enfileirar.
  - Consulta tabela `job_execution_log(key, result_json, status, executed_at)` no início do job; se `status='ok'`, retorna `result_json` sem reprocessar.
  - Ao final, grava resultado na tabela.
  - Middleware Dramatiq (`apps/core/dramatiq_middleware.py`) injeta `trace_id` + `user_id_hash` nos logs structlog via contextvars.
  - Uso: `@idempotent_actor(queue_name='default', max_retries=3)` em vez de `@dramatiq.actor(...)`.
- **Consequências / Porquê:**
  - ✅ Devs não esquecem idempotência — é o default do helper.
  - ✅ Boilerplate colapsa de ~15 linhas para 1 decorator.
  - ⚠ Implementar e testar bem antes de virar dependência de outros jobs (testar na story 2 ou 3).

### ADR-011 — Dramatiq queue única (MVP); segmentação em Fatia 2

- **Data:** 2026-04-21
- **Status:** Accepted (**supersedes D3.5** de Step 4)
- **Contexto:** Step 4 D3.5 previa 3 filas lógicas (`urgent`, `default`, `background`) + DLQ. Amelia apontou que com ~10 usuários RH e volume 20 req/mês, isso é overhead prematuro.
- **Decisão:** MVP tem **1 fila `default`**. DLQ do Dramatiq é built-in (não precisa configuração adicional). Segmentação em `urgent`/`background` + workers dedicados por fila entra em **Fatia 2** quando volume justificar (threshold sugerido: fila > 50 mensagens p95 por > 5 min).
- **Consequências / Porquê:**
  - ✅ `ecosystem.config.js` do PM2 tem 1 worker `gv-worker` rodando `dramatiq app.dramatiq`.
  - ✅ Menos config em Swarm (1 service worker em vez de 3).
  - ⚠ Se algo realmente crítico (ex.: notificação pós-aprovação) ficar preso atrás de job lento (ex.: extração IA de 3 min), usuário percebe latência. Mitigação no MVP: jobs rápidos e lentos só compartilham fila se volume for baixo — o volume baixo (20/mês) garante que isso não vira problema.

### Fixtures & Seed Data (pós-feedback Amelia)

Esta seção complementa "Project Organization" e define como popular dados de desenvolvimento.

**Factory-boy obrigatório por app:**
- Cada `apps/<app>/tests/factories.py` define `<Modelo>Factory(DjangoModelFactory)`.
- Convenção: atributos determinísticos (faker pt_BR); `post_generation` para relações; `Params` para variações (`with_admin_role`, `with_uploads`, etc.).
- Usadas em todos os testes e também pelo `seed_dev`.

**Comando `manage.py seed_dev`:**
- Implementado em `apps/core/management/commands/seed_dev.py`.
- Idempotente (pode rodar 2×; não duplica).
- Popula:
  - 1 superuser admin (`admin@local.test` senha `admin`).
  - 1 RH operator (`rh@local.test`).
  - 3 gestores (1 de cada tipo A/B/C), cada um com seu círculo.
  - 3 tomadores (órgão público + empresa privada + conta Green House).
  - 5 requisições (status variados: pending_review, approved, rejected).
  - 10 candidatos com currículos de exemplo.
  - `ai_provider_config` com Mistral e Groq cadastrados (keys de placeholder via env).
  - `help_snippet` com 5 tooltips iniciais.
  - `policy_version` v1 dos Termos de Uso + Política de Privacidade.
- Para reset completo: `manage.py flush && manage.py seed_dev`.
- **NÃO roda em prod** (guarda `settings.DEBUG or os.environ.get('ALLOW_SEED') == 'true'`).

**Convenção de test fixtures:**
- Fixtures estáticas em `apps/<app>/tests/fixtures/` (JSON/YAML) só quando factory não resolve (ex.: binários de exemplo — áudio OGG de 30s, PDF de Termo de Referência real anonimizado).
- `conftest.py` raiz e por app; fixtures pytest nomeadas `<modelo>_fx` ou `<caso>_fx`.

**Updates aos ADRs anteriores:**

- ADR correspondente ao starter (comando de bootstrap): adicionar ao `uv add --group dev` as deps `factory-boy~=3.3 faker~=30` e `django-stubs[compatible-mypy]~=5.1`.
- ADR-004 (PM2) confirmado: `gv-worker` roda `dramatiq app.dramatiq` sem flag `--queues` (fila única default).

### Atualização ao Step 5 — Implementation Patterns (Delta)

Incorporando correções acima:

1. **Convenção de URL name**: snake_case em inglês com verbo canônico (`mark_in_review`, `approve`, `reject`, `list`, `detail`, `create`).
2. **`@idempotent_actor`** é o default para jobs; usar `@dramatiq.actor` puro só em casos excepcionais (com comentário justificando).
3. **Queue única `default`** até segmentação justificar.
4. **mypy config** em `mypy.ini` com strict nas 3 camadas críticas via glob `mypy-apps.*.{services,schemas,jobs}`.
5. **Factories obrigatórias** por app antes de marcar story como done (contribui para ≥70% cobertura).

### ADR-012 — Grafo de dependências entre apps + regra de imports cross-app

- **Data:** 2026-04-21
- **Status:** Accepted (pós-feedback Amelia em Party Mode Round Step 6)
- **Contexto:** Com 12 apps no domínio, imports cross-app sem disciplina causam dependências circulares por volta da 6ª-10ª story. `matching/services.py` importa `requisitions` + `curriculos` + `ai_providers`; `notifications` importa `requisitions` + `matching`; `audit/signals.py` escuta todos.
- **Decisão:** Grafo de camadas fixas com direção obrigatória. App em camada superior pode importar de camada inferior; NUNCA ao contrário. Cross-app só via `services.py` (nunca `models.py → models.py`); tipos compartilhados em `apps/core/{types.py,schemas.py,events.py}`.
  ```
  Camada 0 (base):       core
  Camada 1:              accounts
  Camada 2 (domínio):    requisitions, curriculos, ai_providers, policies, help
  Camada 3 (composição): matching, email_ingestion, notifications
  Camada 4 (folhas):     audit, telemetry   (só ouvem signals; ninguém importa delas)
  ```
  Regras:
  - Camada N pode importar de camadas 0..N-1.
  - Camada 2 entre si pode se referenciar via **signals** (event-driven) ou via **service calls read-only**; nunca write cross-app sem signal.
  - Camada 4 registra handlers; não é importada por ninguém.
  - Enforce: `ruff` com regra `import-cycles` + teste `tests/integration/test_architecture.py` que percorre imports com `ast` e falha em violação.
- **Consequências / Porquê:**
  - ✅ Zero ciclos; refactor previsível.
  - ✅ `audit` e `telemetry` nunca aparecem em `requirements` de outros apps.
  - ⚠ Se futuramente `matching` precisar emitir evento para `notifications`, usa signal — nunca import direto.

### Adições ao `apps/core/` (pós-feedback Amelia)

Preencher `apps/core/` com primitivos que toda story importará:

```
apps/core/
├── __init__.py
├── apps.py
├── base_models.py        # TimestampedModel, UUIDModel, SoftDeleteModel
├── base_services.py      # ServiceResult[T] (dataclass), DomainError (base Exception)
├── types.py              # TypeAliases: UserId = NewType('UserId', UUID), TomadorId, etc.
├── schemas.py            # Pydantic base: TimestampedSchema, AuditableSchema
├── events.py             # dataclasses de payloads de signals
├── signals.py            # declaração de signals custom (implementação nos handlers)
├── exceptions.py         # DomainValidationError, ProviderUnavailable, etc. (já no step 5)
├── middleware.py         # TraceIdMiddleware, DomainExceptionMiddleware, AuthRequiredMiddleware
├── mixins.py             # SoftDeleteMixin, AuditableMixin
├── tasks.py              # ADR-010: @idempotent_actor
├── idempotent_actor.py   # implementação do decorator (separado para clareza)
├── dramatiq_middleware.py # trace_id via contextvars
├── logging.py            # structlog config
├── testing.py            # pytest mixins: BaseTestCase, APITestCase, AuthenticatedClientMixin
├── templatetags/
│   ├── gv_ui.py, gv_help.py
├── templates/core/
│   ├── ui/               # átomos compartilhados (pós-feedback Sally)
│   │   ├── status_badge.html
│   │   ├── confidence_chip.html
│   │   ├── empty_state.html
│   │   ├── skeleton.html
│   │   ├── toast.html
│   │   ├── spinner.html
│   │   ├── modal.html
│   │   └── breadcrumb.html
│   └── review_inbox.html # hub de fila unificada de revisão (pós-feedback Sally)
├── management/commands/
│   ├── seed_dev.py
│   ├── verify_audit_chain.py
│   └── lint_architecture.py  # executa o teste de imports + report
└── tests/
    ├── conftest.py       # fixtures globais (db, user, authenticated_client, mock_ai_provider, freeze_time)
    ├── factories.py      # UserFactory, TomadorFactory, RequisicaoFactory (relocam? ou por app?)
    └── test_*.py
```

**Decisão sobre factories:** cada app mantém suas próprias em `apps/<app>/tests/factories.py`; `apps/core/tests/factories.py` apenas para factories de base (UserFactory é aqui, reusada por todos).

### `tests/conftest.py` raiz — fixtures globais

```
tests/
├── conftest.py           # fixtures reutilizáveis por todos os tests
├── integration/
│   └── test_architecture.py  # valida ADR-012: sem ciclos, regras de import respeitadas
├── smoke/
│   └── test_happy_paths.py
```

Fixtures mínimas em `tests/conftest.py`:
- `db` (transactional_db do pytest-django)
- `user` (cria via UserFactory)
- `rh_admin` (user com role rh_admin)
- `gestor_b` (user tipo_gestor=B servidor)
- `authenticated_client` (Client com login)
- `mock_ai_provider` (registra MockProvider no registry durante o teste)
- `freeze_time` (freezegun decorator)
- `redis_mock` (fakeredis para jobs Dramatiq inline)

### Sally — `templates/ui/` (átomos globais)

Conforme ADR-012 + adição ao `apps/core/`, os átomos visuais ficam em `apps/core/templates/core/ui/` e são consumidos por todos os apps via `{% include "core/ui/status_badge.html" with status=req.status %}`. Isso previne duplicação visual (3 badges em 3 apps) e garante coerência.

**Lista inicial de átomos (pode crescer):**
- `status_badge.html` (recebe `status`, cor derivada por filtro custom)
- `confidence_chip.html` (recebe `score` 0-1)
- `empty_state.html` (recebe `title`, `message`, `cta_url`, `cta_label`)
- `skeleton.html` (placeholder de loading)
- `toast.html` (recebe `type`, `message`)
- `spinner.html`
- `modal.html` (base para modais HTMX)
- `breadcrumb.html` (recebe `crumbs` — lista)

### Sally — `review_inbox.html` (hub unificado de revisão)

Tela única que consolida todos os itens em "human-in-the-loop":
- Rascunhos IA pending_review (de `requisitions`)
- Currículos com campos de baixa confiança (de `curriculos`)
- Alertas de duplicata pendentes (de `requisitions`)
- E-mails em quarentena (de `email_ingestion`)
- Matches com score alto sem decisão (de `matching`)

Rota: `/inbox/` (name: `core:review_inbox`). View em `apps/core/views.py` consulta querysets de apps de camada 2-3 via `services.get_review_queue(user)` — respeita círculo do usuário. Ordenação por SLA próximo do vencimento.

### ADR-013 — Ingestão de e-mail: IMAP IDLE genérico (não webhook específico)

- **Data:** 2026-04-21
- **Status:** Accepted
- **Contexto:** Pendência crítica do Step 7 — escolher entre webhook específico de provedor (Google Pub/Sub, Microsoft Graph) ou IMAP IDLE genérico para a caixa monitorada `curriculos@greenhousedf.com.br`. Bruno confirmou SMTP/IMAP genérico.
- **Decisão:** Daemon Python com IMAP IDLE (`imapclient` ou `aioimaplib`) em processo dedicado sob PM2 (`gv-email-ingestion`). Envio de notificações continua via SMTP (já previsto em `apps/notifications`).
- **Consequências / Porquê:**
  - ✅ Funciona com qualquer provedor padrão (Google, M365, servidor corporativo próprio, Zoho, etc.) sem depender de integração específica.
  - ✅ Zero custo adicional; zero configuração de provedor.
  - ⚠ IMAP IDLE pode derrubar conexão silenciosamente — daemon precisa reconectar com backoff exponencial + health check periódico.
  - ⚠ Requer credenciais IMAP em `.env` (`IMAP_HOST`, `IMAP_PORT=993`, `IMAP_USER`, `IMAP_PASSWORD`, `IMAP_FOLDER=INBOX`). Senha criptografada (django-cryptography).
  - ⚠ Processo `gv-email-ingestion` fica no ecosystem.config.js do PM2 desde o MVP (não é mais "condicional" como indicado em ADR-004).

## Architecture Validation Results

### Coherence Validation ✅

- 13 ADRs compatíveis entre si; stack coesa Python 3.12 + Django 5.x + Postgres 16 + Redis 7 + Dramatiq + MinIO.
- Patterns (Step 5) sustentam decisions (Step 4); structure (Step 6) implementa patterns.
- Grafo de camadas (ADR-012) enforce via `tests/integration/test_architecture.py`.

### Requirements Coverage Validation ✅

- **89/89 FRs** arquiteturalmente suportados — mapeamento FR→app→arquivo em "Requirements to Structure Mapping" (Step 6).
- **54/54 NFRs** arquiteturalmente endereçados — tabela de cobertura por categoria em Step 7 validation.
- 5 jornadas do PRD com caminho técnico mapeado.

### Implementation Readiness Validation ✅

- Decisões completas: 13 ADRs + 5 blocos D (Data/Auth/API/Frontend/Infra) documentados.
- Estrutura completa: 12 apps + config + deploy + tests com árvore de arquivos explícita.
- Padrões completos: naming, structure, format, communication, process — com enforcement via ruff + mypy + test arquitetural.

### Gap Analysis Results

**Critical Gaps:** 0

**Important Gaps (não bloqueiam dev):**
1. Especificações da VPS pendentes (ADR-007) — Bruno passa quando tiver.
2. 3 decisões DPO do PRD Appendix B — bloqueiam go-live, não dev.
3. ~~Provedor de e-mail~~ ✅ RESOLVIDO em ADR-013 (IMAP IDLE genérico).

**Nice-to-Have Gaps:** Diagramas Mermaid, playbooks de incident, runbook operacional — evoluem com experiência.

### Architecture Completeness Checklist

**✅ Requirements Analysis** — contexto analisado, escala avaliada, constraints identificados, cross-cutting mapeados.

**✅ Architectural Decisions** — 13 ADRs + 5 blocos; stack especificada; integração definida; performance e custo endereçados.

**✅ Implementation Patterns** — naming, structure, format, communication, process.

**✅ Project Structure** — árvore completa, boundaries por ADR-012, integration points mapeados, FR→arquivo explícito.

**✅ Ajustes pós-feedback** — Round Amelia (ADRs 8-11 + Fixtures/Seed) + Round Sally+Amelia (ADR-12 + apps/core populado + templates/ui + conftest raiz + review_inbox) + Round pós-preocupação-Bruno (confirmação Django + ADR-013 IMAP).

### Architecture Readiness Assessment

**Overall Status:** ✅ READY FOR IMPLEMENTATION

**Confidence Level:** High — 13 ADRs fundamentadas, 3 rounds de Party Mode incorporados, gaps críticos = 0.

**Key Strengths:**
- Rastreabilidade FR→arquivo→service explícita.
- Enforcement via linters + teste arquitetural (ADR-012 testável).
- Feature flags desde o dia 1.
- Compliance LGPD nativo (não bolt-on).
- 9+ pontos cegos corrigidos antes de codar (via Amelia + Sally).

**Areas for Future Enhancement:**
- Completar ADR-007 quando specs da VPS chegarem.
- Converter diagramas ASCII → Mermaid.
- MinIO local só quando features que dependem de presigned URLs entrarem em dev.

### Implementation Handoff

**AI Agent Guidelines:**
- Seguir as 13 ADRs sem reinterpretar.
- Respeitar grafo de camadas (ADR-012).
- Toda lógica de domínio em `services.py`; views thin; jobs via `@idempotent_actor`.
- Nunca bypassar audit log; nunca hardcode API key; nunca `print()`.
- Cada commit referencia FR/NFR/Story ID.

**First Implementation Priority (Story 1):** bootstrap do projeto — comando em Starter Template section.

**Roadmap de 15 stories sugerido** (ver Step 7 section acima).

### ADR-014 — VPS de produção: dimensionamento (supersedes ADR-007 pendente)

- **Data:** 2026-04-21
- **Status:** Accepted
- **Contexto:** ADR-007 estava pendente das specs da VPS. Bruno informou: **12 GB RAM + 6 vCPU**. Docker Swarm + Traefik + Portainer já instalados; subdomínio apontando.
- **Decisão:** Dimensionamento do stack Docker Swarm para caber em 12GB/6vCPU com folga operacional. Reserva de ~20% RAM para sistema operacional, Traefik, Portainer e picos.
  ```
  Recursos totais: 12 GB RAM · 6 vCPU (~12000 CPU units em Swarm)
  Reserva sistema: ~2.5 GB RAM · ~1 vCPU
  Disponível app:  ~9.5 GB RAM · ~5 vCPU

  Stack gestao-vagas (limits sugeridos):
  ┌─────────────────┬───────┬──────────┬──────┬─────────┐
  │ Service         │ RAM   │ CPU      │ Reps │ Total   │
  ├─────────────────┼───────┼──────────┼──────┼─────────┤
  │ gv-web          │ 768MB │ 0.5      │  2   │ 1.5GB/1 │
  │ gv-worker       │ 1.5GB │ 1.0      │  2   │ 3GB / 2 │
  │ gv-email-ingest │ 256MB │ 0.25     │  1   │ 256MB   │
  │ postgres        │ 2GB   │ 1.0      │  1   │ 2GB / 1 │
  │ redis           │ 512MB │ 0.25     │  1   │ 512MB   │
  │ minio           │ 512MB │ 0.25     │  1   │ 512MB   │
  │ loki            │ 512MB │ 0.25     │  1   │ 512MB   │
  │ grafana         │ 256MB │ 0.1      │  1   │ 256MB   │
  │ prometheus      │ 512MB │ 0.25     │  1   │ 512MB   │
  ├─────────────────┼───────┼──────────┼──────┼─────────┤
  │ TOTAL           │       │          │      │ ~9GB/6  │
  └─────────────────┴───────┴──────────┴──────┴─────────┘

  Margem: ~500MB RAM + ~0.5 vCPU livres para picos.
  ```
- **Consequências / Porquê:**
  - ✅ Folga adequada para volume baseline (20 req/mês) com headroom para 10× (NFR7).
  - ✅ 2 réplicas `gv-web` + 2 de `gv-worker` garantem zero-downtime rolling update.
  - ✅ Postgres com 2GB é confortável para base de 50k CVs (NFR8) + embeddings pgvector.
  - ⚠ **Não cabe Elasticsearch/OpenSearch** se houver vontade futura de busca full-text avançada; Postgres full-text (`tsvector`) resolve o que precisamos no MVP.
  - ⚠ **Uploads grandes** (PDF scanneado > 15MB) podem pressionar RAM dos workers durante extração — se virar problema, aumentar `gv-worker` RAM para 2GB (ainda cabe).
  - ⚠ **Backup diário** (pg_dump + mc mirror para Backblaze B2/Wasabi) roda no host (fora Swarm); consumo de RAM/CPU pontual e aceitável.
  - ⚠ Se VPS for host único sem alta disponibilidade, **downtime em reboot é inevitável** — mitigação: manutenção programada fora de horário comercial + backup recente antes.

**Parâmetros de deploy no `docker-compose.stack.yml`:**
- `deploy.resources.limits` e `deploy.resources.reservations` conforme tabela acima.
- `deploy.restart_policy.condition: on-failure` em todos os serviços.
- `deploy.update_config.parallelism: 1` + `failure_action: rollback` (zero-downtime).
- `deploy.placement.constraints: [node.role == manager]` para Postgres (evita migração acidental em cluster multi-node futuro).

**Monitoramento de recursos:** Grafana dashboard pré-configurado exibe RAM/CPU/disco por container + alertas quando um serviço ultrapassar 80% de limit por > 5 min. Evita surpresas.
