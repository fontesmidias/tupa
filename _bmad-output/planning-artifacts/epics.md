---
stepsCompleted:
  - step-01-validate-prerequisites
  - step-02-design-epics
  - step-03-create-stories-lot1  # Lote 1 de 4 salvo; Party Mode Amelia + Lotes 2-4 pendentes para próxima sessão
sessionState:
  lastSession: '2026-04-21'
  pausedAt: 'Step 3 — Lote 1 de 4 stories concluído (Epics 1-3, 24 stories). Party Mode com Amelia sobre Lote 1 pendente. Handoff em _bmad-output/planning-artifacts/HANDOFF.md'
  resumePrompt: 'Ver HANDOFF.md seção "Prompt de retomada".'
inputDocuments:
  - path: 'docs/prd/'
    type: 'prd-sharded'
    summary: '89 FRs em 13 áreas; 54 NFRs em 10 categorias; 5 jornadas; Appendix A matriz rastreabilidade; Appendix B 3 pendências DPO; Appendix C changelog.'
  - path: '_bmad-output/planning-artifacts/architecture.md'
    type: 'architecture'
    summary: '14 ADRs, 5 blocos de decisões, padrões de implementação, estrutura completa de 13 apps (vagas adicionado em 2026-04-21), validação PASS, VPS 12GB/6vCPU dimensionada.'
  - path: '_bmad-output/planning-artifacts/prd-validation-report.md'
    type: 'validation-report'
    summary: 'PRD aprovado PASS 5/5 Excellent.'
workflowType: 'epics-and-stories'
project_name: 'gestao-vagas'
user_name: 'Bruno'
communication_language: 'Portugues do brasil'
document_output_language: 'Portugues do brasil'
date: '2026-04-21'
pm: 'John (bmad-agent-pm)'
uxSpecPlan:
  status: 'deferred-intentional'
  decision: 'Bruno confirmou (2026-04-21) que quer UX spec formal, mas em momento oportuno — quando John recomendar.'
  recommendedTiming: 'Após Epic 1-3 (bootstrap + auth + submissão multimodal) estarem codados e funcionando localmente. Sally terá superfícies reais para refinar.'
  whenToInvoke: 'bmad-create-ux-design skill; Sally como facilitadora.'
---

# Epics & Stories — gestao-vagas

**PM Facilitador:** John (bmad-agent-pm)
**Solicitante:** Bruno (Coord. RH + Eng. Software — Green House)
**Data início:** 2026-04-21
**Versão:** 0.1 (em construção)

_Este documento transforma o PRD + Arquitetura em épicos e histórias executáveis pelo Claude Code. Cada história referencia FRs/NFRs/ADRs de origem — mantemos **links canônicos aos docs-fonte** em vez de duplicar conteúdo (ver decisão abaixo)._

## Decisão sobre reuso vs. duplicação

O template BMAD padrão pede re-listar todos os FRs/NFRs aqui. **Não vamos** — o PRD já tem 89 FRs + 54 NFRs rigorosamente catalogados (foi validado PASS 5/5), e a Arquitetura tem 14 ADRs com IDs rastreáveis. Duplicar cria risco de drift. Em vez disso:

- **FRs fonte:** `docs/prd/functional-requirements.md` (ou `archive/prd.md` para a versão monolítica). Referenciados por ID (FR27, FR43, etc.).
- **NFRs fonte:** `docs/prd/non-functional-requirements.md`.
- **Jornadas fonte:** `docs/prd/user-journeys.md`.
- **Scoping/Fatias fonte:** `docs/prd/project-scoping-phased-development.md`.
- **ADRs fonte:** `_bmad-output/planning-artifacts/architecture.md` (seção "Architecture Decisions Log").
- **Matriz rastreabilidade fonte:** `docs/prd/appendix-a-matriz-de-rastreabilidade-jornada-fr-nfr.md`.

Cada história cita os FRs/NFRs/ADRs que implementa. Quando Claude for codar a história, ele abre esses artefatos, não precisa de cópia aqui.

## Resumo de requisitos

- **89 Functional Requirements** (FR1–FR89) em 13 áreas de capacidade. Ver `docs/prd/functional-requirements.md`.
- **54 Non-Functional Requirements** (NFR1–NFR54) em 10 categorias. Ver `docs/prd/non-functional-requirements.md`.
- **14 Architecture Decision Records** (ADR-001 a ADR-014). Ver `_bmad-output/planning-artifacts/architecture.md`.
- **5 User Journeys narradas** (Marlene, Roberto, Bruno-RH, ingestão automática, admin técnico). Ver `docs/prd/user-journeys.md`.
- **Fatiamento do PRD:** MVP (Fatia 1) → 1.1 → 2 (Growth) → 3 (Vision). Ver `docs/prd/project-scoping-phased-development.md`.
- **Pendências DPO:** 3 itens bloqueantes de go-live. Ver `docs/prd/appendix-b-pendncias-dpo-jurdico.md`.

## Coverage Map

Matriz formal Jornada → FR → NFR já existe no **PRD Appendix A**. Será reusada. Nos épicos aqui, cada um listará explicitamente:
- Jornadas que cobre.
- FRs que implementa (range ou lista).
- NFRs que atende.
- ADRs que aplica.

## Epic List

### Epic 1 — Fundação do projeto (Bootstrap técnico)

**User Outcome:** Projeto existe, roda em `localhost:3005`, banco conectado, Redis rodando, testes passam, CI em pé. Habilita tudo que vem depois.
**FRs cobertos:** FR84 (skeleton admin de tomadores), FR88 (feature flags), FR89 (backup diário).
**NFRs:** NFR50, NFR51, NFR52, NFR53, NFR54.
**ADRs:** 001, 002, 003, 004, 005, 006, 008, 010, 012.

### Epic 2 — Acesso sem fricção (Link mágico + cadastro progressivo)

**User Outcome:** Gestor digita e-mail, recebe código, entra. Completa perfil após primeira ação de valor. RH entra da mesma forma; MFA disponível.
**FRs:** FR1-FR9.
**NFRs:** NFR1, NFR11-NFR19.
**ADRs:** 002, 008, 010.

### Epic 3 — Auditoria imutável (Hash-chain) + LGPD baseline

**User Outcome:** Toda ação é rastreável e inadulterável. Políticas versionadas com changelog Nubank-style. Titular exerce direitos LGPD.
**FRs:** FR64-FR72.
**NFRs:** NFR19, NFR26-NFR33.
**ADRs:** D1.4, D2.5.

### Epic 4 — Providers IA plugáveis (Fundação)

**User Outcome:** RH gerencia providers (OCR/Vision/Áudio/LLM) via UI, troca em runtime, vê cota. Mistral + Groq + ocr.space + Claude configuráveis.
**FRs:** FR53-FR60.
**NFRs:** NFR34-NFR36, NFR41-NFR44.
**ADRs:** 006, 013.

### Epic 5 — Submissão multimodal pelo gestor

**User Outcome:** Gestor envia áudio/PDF/texto/imagem direto → recebe confirmação → recebe resumo IA por e-mail. Jornadas J1 e J2.
**FRs:** FR10-FR18, FR61-FR63, FR73-FR78 (integração inicial help), FR79-FR80 (telemetria captura).
**NFRs:** NFR2, NFR15-NFR16, NFR45-NFR48.
**ADRs:** D4.2, D4.3, D4.4, 006, 011.

### Epic 6 — Revisão RH e publicação de vagas

**User Outcome:** RH revisa rascunho IA com player áudio sincronizado + diff + campos amarelos → aprova → vaga publicada + gestor notificado. Jornada J3.
**FRs:** FR29-FR35, FR41-FR42, FR48-FR52.
**NFRs:** NFR3, NFR28.
**ADRs:** D4.2, D4.5.

### Epic 7 — Ingestão passiva de currículos por e-mail

**User Outcome:** RH encaminha e-mail com CV → sistema detecta, extrai, deduplica, cataloga. Jornada J4.
**FRs:** FR19-FR24.
**NFRs:** NFR5, NFR9, NFR24.
**ADRs:** 013, D3.4.

### Epic 8 — Matching vaga × candidato

**User Outcome:** RH vê candidatos ranqueados com explicabilidade. Notificação quando CV novo tem match alto.
**FRs:** FR43-FR47.
**NFRs:** NFR6, NFR8.
**ADRs:** D1.5.

### Epic 9 — Detecção de duplicatas (3 camadas)

**User Outcome:** RH recebe alerta "possível duplicata" com veredito IA → mescla/relaciona/descarta. Camada 3 (LLM) atrás de flag.
**FRs:** FR36-FR40.
**NFRs:** NFR24.
**ADRs:** D1.5, 010.

### Epic 10 — Hub unificado de revisão (Inbox)

**User Outcome:** RH abre `/inbox/` e vê tudo em human-in-the-loop numa tela: rascunhos + currículos baixa confiança + alertas duplicata + e-mails em quarentena + matches.
**FRs:** agregador (reusa Epics 6, 7, 8, 9).
**NFRs:** NFR3.

### Epic 11 — Help contextual universal

**User Outcome:** Tooltip em qualquer campo/botão/status; RH edita via admin sem redeploy. Breadcrumbs + empty states.
**FRs:** FR73-FR78 (cobertura completa).
**NFRs:** NFR47.

### Epic 12 — Telemetria UX + IA-lê-logs

**User Outcome:** Sistema captura uso; job LLM semanal gera relatório; RH vê em `/admin/ux-insights`.
**FRs:** FR79-FR83.
**NFRs:** NFR37-NFR40.

### Epic 13 — Observabilidade e operação

**User Outcome:** Dashboards Grafana; alertas; log estruturado; backup automático testado.
**FRs:** operacionais.
**NFRs:** NFR20-NFR25, NFR37-NFR40, NFR51.
**ADRs:** 014.

### Epic 14 — Deploy em produção (Swarm)

**User Outcome:** Sistema no subdomínio da Green House. TLS 1.3. Zero-downtime. Primeiro tomador real em produção.
**FRs:** operacionais.
**NFRs:** NFR11, NFR20, NFR21-NFR23, NFR50.
**ADRs:** 014. Bloqueado por 3 decisões DPO do Appendix B do PRD.

## Fatiamento MVP → 1.1 → 2 → 3

| Fatia | Epics |
|---|---|
| **Fatia 1 (MVP)** | 1, 2, 3, 4, 5, 6, 7, 8, 9*, 10, 11, 12*, 13, 14 |
| **Fatia 1.1** | Epic 9 Camada 3 (LLM raciocinador) ativa via flag; Epic 12 job LLM ativa após 30d de eventos |
| **Fatia 2 (Growth)** | WhatsApp (Evolution API) · Parsing Word · Templates por tomador · Cotas PcD · Disparate impact · Providers adicionais · MFA TOTP obrigatório |
| **Fatia 3 (Vision)** | Portal candidato · Suporte IA (chatbot RAG) · Gov.br/SINE integração · eSocial S-2200 · Multi-idioma |

## FR Coverage Map (sumarizado)

| Epic | FRs implementadas |
|---|---|
| Epic 1 | FR84 (skel), FR88, FR89 |
| Epic 2 | FR1-FR9 |
| Epic 3 | FR64-FR72 |
| Epic 4 | FR53-FR60 |
| Epic 5 | FR10-FR18, FR61-FR63, FR73-FR78 (inicial), FR79-FR80 |
| Epic 6 | FR29-FR35, FR41-FR42, FR48-FR52 |
| Epic 7 | FR19-FR24 |
| Epic 8 | FR43-FR47 |
| Epic 9 | FR36-FR40 |
| Epic 10 | agregador (reusa Epics 6-9) |
| Epic 11 | FR73-FR78 (cobertura completa) |
| Epic 12 | FR79-FR83 |
| Epic 13 | operacionais (backup, obs) |
| Epic 14 | operacionais (deploy) |

Todos os 89 FRs estão cobertos em pelo menos um Epic.

## Histórias (a ser construído no Step 3)

_Next: decompor cada épico em user stories com acceptance criteria._

## Stories — Lote 1 (Epics 1-3) — Aprovado em 2026-04-21 (Party Mode pendente nova sessão)

### Epic 1 — Fundação do projeto (Bootstrap técnico)

**Goal:** Projeto roda em localhost:3005, banco conectado, Redis rodando, testes passam, CI em pé.

#### Story 1.1 — Bootstrap do projeto Django ✅ DONE (2026-04-21)

As a solo developer (Bruno, via Claude Code), I want um projeto Django 5.x inicializado com uv, 13 apps criados, So that tenho alicerce para implementar features.

Acceptance Criteria:
- Given repositório Git limpo When executo o comando de bootstrap da Arquitetura Then existem pyproject.toml, uv.lock, manage.py, config/settings/{base,dev,prod,test}.py, config/{urls.py,asgi.py,wsgi.py}
- And existem 13 apps em apps/{core,accounts,requisitions,vagas,ai_providers,matching,curriculos,email_ingestion,audit,notifications,telemetry,help,policies}
- And `vagas` pertence à camada de composição do ADR-012 (acima de requisitions, abaixo de matching)
- And `uv run python manage.py check` passa
- And `uv run python manage.py runserver 3005` serve "Hello, gestao-vagas"
- And .env.example existe com variáveis documentadas
- And .gitignore exclui .env, media/, __pycache__/, *.pyc, .venv/

FRs: n/a · NFRs: NFR52 · ADRs: 001, 002, 003, 008.

#### Story 1.2 — Configuração Postgres local + pgvector ✅ DONE (2026-04-21, via Docker container `gv-postgres` porta 5433 — ADR-003 ajustado)

As a Bruno, I want Django conectado ao Postgres local com `gestao_vagas_dev` + extensão pgvector, So that rodo migrations.

AC:
- Given Postgres 14+ em localhost:5432 When executo `manage.py migrate` Then migrations rodam sem erro
- And extensão `vector` instalada
- And DATABASE_URL lido via django-environ
- And `manage.py check_db` valida conectividade + pgvector

FRs: n/a · NFRs: NFR22 · ADRs: 003.

#### Story 1.3 — Redis local via Docker + conexão Django ✅ DONE (2026-04-21)

As a Bruno, I want Redis via Docker + Django usando como cache + broker Dramatiq, So that jobs async e cache rodam localmente.

AC:
- Given Docker rodando When `docker run -d --name gv-redis -p 6379:6379 --restart unless-stopped redis:7-alpine` Then `docker ps` mostra gv-redis up
- And `manage.py check_redis` retorna "Redis OK"
- And Django CACHES default usa django-redis apontando para redis://localhost:6379/1
- And Dramatiq broker em config/dramatiq.py usa redis://localhost:6379/0

FRs: n/a · NFRs: NFR25 · ADRs: 005.

#### Story 1.4 — Configuração PM2 (ecosystem.config.js) ✅ DONE (2026-04-21)

As a Bruno, I want PM2 gerenciando gv-web + gv-worker + gv-email-ingestion, So that subo/derrubo com 1 comando.

AC:
- Given PM2 instalado When `pm2 start ecosystem.config.js` Then 3 processos sobem (uvicorn na 3005, dramatiq, daemon IMAP)
- And `pm2 status` mostra online
- And `pm2 logs gv-web` mostra output
- And `pm2 delete ecosystem.config.js` para tudo
- And reload automático via --reload em dev

FRs: n/a · NFRs: NFR50 · ADRs: 004, 011, 013.

#### Story 1.5a — apps/core/ fundamentos (models + types + exceptions) ✅ DONE (2026-04-21, cobertura 100%)

As a Claude Code, I want apps/core/ com primitivos de domínio prontos, So that cada novo app reusa base sem reinventar.

AC:
- Given Story 1.1 When Story 1.5a completa Then apps/core/base_models.py define TimestampedModel, UUIDModel, SoftDeleteModel
- And apps/core/base_services.py define ServiceResult[T] + DomainError
- And apps/core/types.py define type aliases (UserId, TomadorId, etc.)
- And apps/core/exceptions.py define DomainValidationError, ProviderUnavailable, ExtractionFailed, DuplicateDetected, ConsentRequired
- And testes cobrem ≥85% destes módulos

FRs: n/a · NFRs: NFR37, NFR52 · ADRs: 008, 012.

#### Story 1.5b — apps/core/ runtime (middleware + jobs + logging + testing) ✅ DONE (2026-04-21, cobertura 92% total / ≥94% arquivos novos)

As a Claude Code, I want apps/core/ com runtime plumbing pronto, So that middleware, jobs idempotentes, logging e testing mixins existam antes dos demais apps.

AC:
- Given Story 1.5a When Story 1.5b completa Then apps/core/middleware.py tem TraceIdMiddleware, DomainExceptionMiddleware, AuthRequiredMiddleware (skeleton)
- And apps/core/tasks.py + idempotent_actor.py implementam @idempotent_actor com tabela job_execution_log
- And apps/core/logging.py configura structlog (JSON em prod, console em dev)
- And apps/core/testing.py tem BaseTestCase, AuthenticatedClientMixin
- And testes cobrem ≥80%

FRs: n/a · NFRs: NFR37, NFR52 · ADRs: 008, 010, 012.

#### Story 1.6 — tests/conftest.py raiz + fixtures globais ✅ DONE (2026-04-21, 53 testes, cobertura 93%)

As a Claude Code, I want fixtures pytest globais, So that cada story reusa sem reinventar.

AC:
- Given Story 1.5 When `pytest --collect-only` Then fixtures disponíveis: db, user, rh_admin, gestor_b, authenticated_client, mock_ai_provider, freeze_time, redis_mock
- And usam factory_boy (UserFactory em apps/core/tests/factories.py temporariamente)
- And pytest.ini tem DJANGO_SETTINGS_MODULE=config.settings.test

FRs: n/a · NFRs: NFR52.

#### Story 1.7 — CI/CD básico (GitHub Actions pr-checks.yml) ✅ DONE (2026-04-21, workflow validado localmente; falta push para GitHub + proteção de branch)

As a Bruno, I want GitHub Actions rodando ruff + mypy + pytest a cada PR, So that ninguém merge código quebrado.

AC:
- Given repo GitHub When abro PR Then workflow pr-checks.yml dispara
- And roda: uv sync, ruff check, ruff format --check, mypy apps/, pytest --cov=apps --cov-fail-under=70
- And bloqueia merge em falha
- And usa caching de .venv e .mypy_cache

FRs: n/a · NFRs: NFR51, NFR52 · ADRs: 008, Step 4 D5.1.

#### Story 1.8 — Teste arquitetural (ADR-012 enforcement) ✅ DONE (2026-04-21, 16 testes)

As a Bruno, I want teste automatizado que valida grafo de dependências (ADR-012), So that previno circular imports.

AC:
- Given Stories 1.1-1.7 When `pytest tests/integration/test_architecture.py` Then teste percorre apps/**/*.py com ast e coleta imports
- And verifica grafo de 5 camadas para cada app
- And falha se apps/requisitions importar de apps/matching
- And falha se apps/audit for importado por qualquer app
- And passa com estrutura inicial

FRs: n/a · NFRs: NFR52 · ADRs: 012.

#### Story 1.9 — manage.py seed_dev (fixtures iniciais)

As a Bruno, I want comando que popula base com dados mínimos, So that não crio tudo manualmente.

AC:
- Given Stories 1.1-1.6 + 2.1 When `manage.py seed_dev` Then cria: 1 superuser admin, 1 RH operator, 3 gestores (A/B/C), 3 tomadores, ai_provider_config com Mistral+Groq, 5 help_snippet, policy_version v1
- And idempotente
- And falha em prod (settings.DEBUG == False and ALLOW_SEED != 'true')
- And usa factory_boy factories

FRs: FR84 · ADRs: Fixtures & Seed.

#### Story 1.10 — Feature flags (django-waffle) + backup script ✅ DONE (2026-04-21)

As a Bruno, I want django-waffle + script de backup Postgres+MinIO, So that tenho controle de rollout e recovery.

AC:
- Given Stories 1.1-1.9 When Story 1.10 completa Then django-waffle adicionado + migrations rodadas
- And 3 flags via seed_dev: enable_duplicate_llm_layer, enable_ux_llm_report, require_mfa_for_rh
- And deploy/backup/backup.sh contém pg_dump + mc mirror (placeholder para MinIO)
- And README documenta backup local

FRs: FR88, FR89 · NFRs: NFR21 · ADRs: 014, Step 4 D5.7.

---

### Epic 2 — Acesso sem fricção

**Goal:** Gestor e RH entram com link mágico. Cadastro progressivo valor-primeiro.

#### Story 2.1 — User model customizado (AbstractBaseUser + UUID) ✅ DONE (2026-04-21, 90 testes, cobertura 91.27%, models 100%)

As a Bruno, I want User com UUID PK, email identificador, tipo_gestor, tomador_id, circulo_id, anonimizado_em, So that atendo LGPD e visibilidade.

AC:
- Given projeto inicializado When Story 2.1 completa Then apps.accounts.models.User herda de AbstractBaseUser + PermissionsMixin
- And PK é UUIDField(default=uuid.uuid4)
- And campos: email (unique, case-insensitive), tipo_gestor (TextChoices A/B/C nullable), tomador FK null, circulo FK null, anonimizado_em DateTime null
- And is_cadastro_completo é property (nome + tipo_gestor + tomador)
- And UserFactory em apps/accounts/tests/factories.py + rh_admin_user_factory
- And migrations rodam limpas
- And settings.AUTH_USER_MODEL = 'accounts.User'
- And ≥85% cobertura

FRs: FR4, FR6, FR8 · NFRs: NFR13, NFR14 · ADRs: D2.1.

#### Story 2.2 — Link mágico: solicitar código ✅ DONE (2026-04-21, 105 testes, cobertura 92.41%, novos arquivos ≥95%)

As a gestor, I want digitar email e receber código de 6 dígitos, So that entro sem senha.

AC:
- Given não autenticado em /auth/entrar/ When digita email válido e submete Then MagicLink(email, code_hash, ip, ua, expires_at=now+15min, used_at=null) criado
- And email de 6 dígitos enviado (SMTP; backend console em dev)
- And redirect para /auth/codigo/?email=<email>
- And email inválido: erro sem revelar existência
- And rate-limit: 5/IP+email/10min retorna 429
- And evento auth.magic_link_requested logado

FRs: FR1 · NFRs: NFR1, NFR12, NFR18 · ADRs: D2.6.

#### Story 2.3 — Link mágico: consumir código ✅ DONE (2026-04-21, 124 testes, cobertura 93.17%, service 94%)

As a gestor, I want digitar código e entrar, So that acesso sem senha.

AC:
- Given MagicLink válido When digito código correto Then used_at=now(), sessão criada, login
- And contexto divergente (IP de consumo em classe /24 diferente do IP de solicitação OU hash da UA string difere) → NÃO invalida automaticamente; exige reconfirmação via segundo código enviado ao mesmo email
- And evento `auth.magic_link_context_mismatch` logado com {ip_sol, ip_con, ua_hash_sol, ua_hash_con}
- And expirado → erro "código expirado"
- And errado → erro genérico "inválido"
- And 5 tentativas erradas em 10min → bloqueia por 15min
- And cadastro incompleto → redirect para fluxo Story 2.4
- And completo → home do role

FRs: FR2, FR3 · NFRs: NFR12 · ADRs: D2.2.

#### Story 2.4 — Cadastro progressivo valor-primeiro ✅ DONE (2026-04-21, 147 testes, cobertura 94.06%, novos 100%)

As a gestor, I want completar perfil após submeter primeira ação de valor, com pré-preenchimento IA do domínio do email, So that não encaro form antes de valor.

AC:
- Given autenticado com is_cadastro_completo==False When tenta rota protegida Then middleware redireciona /auth/completar-perfil/
- And tela pré-preenche tipo_gestor por domínio (.gov.br→B, greenhousedf.com.br→A, outros→C)
- And pré-preenche tomador via Tomador.match_by_email_domain(email)
- And gestor confirma/edita máx 3 campos, salva
- And após salvar, is_cadastro_completo==True, redirect rota original
- And se pulou, fica logado mas bloqueado de rotas protegidas (exceto Nova requisição)

FRs: FR4, FR5, FR6 · NFRs: NFR48 · ADRs: D2.1.

#### Story 2.5 — MFA TOTP opt-in para rh_admin ✅ DONE (2026-04-21, 195 testes, cobertura 94.64%, novos ≥92%)

As a Bruno (rh_admin), I want ativar MFA TOTP, So that reforço segurança.

AC:
- Given rh_admin autenticado When acessa /conta/seguranca/mfa/ e clica Ativar Then secret TOTP gerado + QR exibido
- And usuário escaneia + digita código → se correto, mfa_enabled=True, secret criptografado
- And próximo login de rh_admin com mfa_enabled pede código TOTP após link mágico
- And flag require_mfa_for_rh pode forçar todos
- And pode desativar com confirmação via TOTP

FRs: FR7 · NFRs: NFR17 · ADRs: D2.4.

#### Story 2.6 — Sessão Django com cookies seguros + logout ✅ DONE (2026-04-21, 200 testes, cobertura 94.75%)

As a usuário, I want sessão expire e logout explícito, So that conta segura em dispositivos compartilhados.

AC:
- Given autenticado When verifica cookies Then HttpOnly=True, Secure=True em prod, SameSite=Lax
- And SESSION_COOKIE_AGE = 7 dias rolling
- And logout POST /auth/sair/ → sessão destruída, redirect /auth/entrar/
- And mudança de privilégio rotaciona session_key

FRs: FR9 · NFRs: NFR13 · ADRs: D2.2.

#### Story 2.7 — QuerySet mixin + decorators de role ✅ DONE (2026-04-21, 220 testes, cobertura 94.93%, novos 100%)

As a Claude Code, I want @require_role + RequisicaoManager.for_user auto-filtrando por círculo, So that autorização é transversal e declarativa.

AC:
- Given Stories 2.1-2.6 When view @require_role('rh_admin') acessada por gestor Then 403
- And @require_role_any('rh_admin','rh_operator') aceita ambos
- And RequisicaoManager.for_user(gestor) retorna requisições onde circulo_id match ou criado_por==gestor
- And for_user(rh_admin) retorna todas
- And testes cobrem 3 cenários (ok, proibido, filtro cross-círculo)

FRs: FR8 · NFRs: NFR13 · ADRs: D2.3.

---

### Epic 3 — Auditoria imutável + LGPD baseline

**Goal:** Toda ação rastreável. Políticas versionadas. Titular exerce direitos LGPD.

#### Story 3.1 — Modelo AuditLog com hash-chain ✅ DONE (2026-04-21, 245 testes, cobertura 95.12%, novos 100%)

As a Bruno, I want audit_log que registra escrita com hash SHA-256 encadeado, So that provo integridade para TCU/ANPD/DPO.

AC:
- Given Stories 1.5 + 2.1 When Story 3.1 completa Then apps.audit.models.AuditLog tem: id UUID, actor_user_id UUID nullable, ip, user_agent, action, entity_type, entity_id, before JSONB, after JSONB, timestamp, hash_prev CHAR(64), hash_curr CHAR(64)
- And db_table='audit_log'
- And hash_curr = sha256(hash_prev || canonical_json(payload))
- And AuditLog.seal(actor, entity, before, after, action) atomiza criação + hash
- And migration cria índice (entity_type, entity_id, timestamp) + único hash_curr
- And append-only: teste valida ausência de update/delete no manager

FRs: FR64 · NFRs: NFR19 · ADRs: D1.4.

#### Story 3.2 — Signal post_save genérico + log_audit ✅ DONE (2026-04-21, 262 testes, cobertura 95.37%, novos ≥90%)

As a Claude Code, I want signal universal + função log_audit(actor,entity,before,after,action), So that qualquer app dispara audit sem boilerplate.

AC:
- Given Story 3.1 + Story 2.7 (AuthRequiredMiddleware fornecendo request.user) When modelo com AuditableMixin salva Then post_save captura diff e chama log_audit
- And log_audit chama AuditLog.seal em transação atômica
- And AuditableMixin.Meta.auditable_fields permite excluir campos sensíveis
- And testes cobrem criação, update, delete
- And actor vem de request.user via middleware ou passado explicitamente
- And em contexto async (Dramatiq worker, management command), `actor=None` é permitido e AuditLog marca `actor_user_id=NULL` + `action` prefixado com `system:` — teste cobre cenário de job sem request

FRs: FR64 · NFRs: NFR19 · ADRs: D1.4. **Depende de:** Story 2.7.

#### Story 3.3 — Comando manage.py verify_audit_chain

As a Bruno, I want comando que valida integridade da cadeia inteira, So that provo ausência de adulteração.

AC:
- Given Stories 3.1+3.2 + registros When `manage.py verify_audit_chain` Then comando lê registros em ordem de timestamp
- And valida registro[i].hash_prev == registro[i-1].hash_curr e hash_curr recomputa
- And sucesso: "✅ Cadeia íntegra: N registros"
- And falha: mostra registro que quebrou + exit != 0
- And suporta --since <date>

FRs: FR65 · NFRs: NFR19 · ADRs: D1.4.

#### Story 3.4 — PolicyVersion + PolicyAcceptance ✅ DONE (2026-04-21, 275 testes, migração seed idempotente 0002_seed_v1)

As a Bruno, I want versionar Termos + Política e registrar aceites imutáveis, So that atendo LGPD.

AC:
- Given Epic 2 completo When Story 3.4 completa Then apps.policies.models.PolicyVersion: id UUID, kind (terms/privacy), version (semver), effective_at, full_text_md, summary_of_changes_md
- And PolicyAcceptance: user, policy_version, accepted_at, ip, user_agent, summary_shown_version
- And PolicyAcceptance append-only
- And seed_dev cria v1 de ambas
- And admin Django permite criar nova PolicyVersion

FRs: FR67, FR69 · NFRs: NFR27 · ADRs: D1.4.

#### Story 3.5 — PolicyMiddleware: modal estilo Nubank ✅ DONE (2026-04-21, 284 testes)

As a usuário, I want ver modal com resumo em tópicos das mudanças, So that entendo sem ler documento completo.

AC:
- Given Story 3.4 + nova v2 When usuário com último aceite v1 acessa rota protegida Then PolicyMiddleware intercepta e renderiza modal com summary_of_changes_md (v2)
- And modal CTA "Ver documento completo" → /politicas/privacidade/v2/
- And "Aceitar" → PolicyAcceptance criado → request prossegue
- And "Não aceito" → logout + mensagem
- And pula /auth/, /webhooks/, /healthz, /politicas/

FRs: FR67, FR68, FR69 · NFRs: NFR27 · ADRs: Step 4 D3.3.

#### Story 3.6a — Direitos do titular: ver / corrigir / exportar (LGPD Arts. 17-19) ✅ DONE (2026-04-21, 295 testes, DRAMATIQ_EAGER em tests, audit_bridge para não violar ADR-012)

As a titular, I want acesso/correção/portabilidade dos meus dados, So that exerço direitos de transparência LGPD.

AC:
- Given autenticado When acessa /conta/meus-dados/ Then vê os botões: Ver / Corrigir / Exportar (placeholders para Anonimizar/Revogar com link para 3.6b)
- And Ver: JSON/tabela com dados pessoais + audit relacionado (via apps.audit)
- And Corrigir: form para campos editáveis (nome, email secundário) dispara AuditLog via Story 3.2
- And Exportar: ZIP com JSON + binários anexados (CVs, áudios) gerado async via `@idempotent_actor`
- And SLA: resposta automática ≤15 dias; métricas logadas

FRs: FR70, FR71 · NFRs: NFR31, NFR32 · ADRs: D2.5.

#### Story 3.6b — Direitos do titular: anonimizar / revogar (LGPD Arts. 18, 20)

As a titular, I want anonimizar conta ou revogar opt-ins, So that exerço direito ao esquecimento preservando auditoria legal.

AC:
- Given Story 3.6a + Story 2.5 (MFA TOTP) When titular clica Anonimizar Then exige reautenticação via link mágico + código MFA (se mfa_enabled) OU segundo link mágico de confirmação
- And `services.anonymize_user(user)` executa em transação: substitui PII (nome, email, CPF) por hash determinístico, set `anonimizado_em=now()`, mantém `id` para integridade referencial
- And hash-chain de audit_log é **preservado**: registros anteriores do usuário permanecem com `actor_user_id` apontando para conta anonimizada; teste valida que `verify_audit_chain` continua PASS após anonimização
- And Revogar: desativa flags de opt-in (marketing, analytics) sem deletar conta — registra AuditLog `consent.revoked`
- And SLA: ≤15 dias; ações críticas disparam email ao DPO
- And operação é idempotente (segunda chamada em usuário já anonimizado retorna no-op com log)

FRs: FR70, FR72 · NFRs: NFR31, NFR32 · ADRs: D2.5.

#### Story 3.7 — Criptografia em repouso (EncryptedField)

As a Bruno, I want campos sensíveis criptografados, So that backups vazados não revelam dados sensíveis.

AC:
- Given Epic 2 + 3.1-3.3 When Story 3.7 completa Then django-cryptography-django5 instalado + FIELD_ENCRYPTION_KEY em .env.example
- And apps.core.fields.EncryptedCharField e EncryptedTextField re-exportados
- And migration de teste: User.cpf_encrypted com EncryptedCharField funciona via ORM
- And DB mostra cipher text; ORM retorna plaintext
- And AiProviderConfig.api_key (futuro Epic 4) já nasce EncryptedCharField

FRs: FR72 · NFRs: NFR14 · ADRs: D2.5.

---

**Lote 1 total: 26 stories** (ajuste pós-revisão Amelia 2026-04-21: Story 1.5 → 1.5a+1.5b, Story 3.6 → 3.6a+3.6b; AC de 2.3 desambiguado; dependência 3.2→2.7 declarada).

---

### Epic 4 — Providers IA plugáveis (Fundação)

#### Story 4.1 — AiProviderConfig model + api_key criptografada

As a Bruno, I want registro único de providers com credenciais criptografadas em repouso, So that troco/adiciono provider sem deploy.

AC:
- Given Story 3.7 When Story 4.1 completa Then apps.ai_providers.models.AiProviderConfig tem: id UUID, name, kind (ocr/vision/audio/llm), driver_class (dotted path), api_key EncryptedCharField, config JSONB, priority int, is_active bool, quota_monthly int nullable, quota_used int, health_status (healthy/degraded/down), last_check_at
- And admin Django permite criar/editar
- And seed_dev cria 4 registros (Mistral OCR, ocr.space, Groq Whisper, Claude)
- And ≥85% cobertura

FRs: FR53, FR54 · NFRs: NFR14, NFR41 · ADRs: 006.

#### Story 4.2 — Interfaces de provider (OCR/Vision/Audio/LLM)

As a Claude Code, I want Protocol classes tipadas para cada kind, So that drivers são intercambiáveis e mypy valida.

AC:
- Given Story 1.5a When Story 4.2 completa Then apps/ai_providers/providers/base.py define Protocol: OCRProvider.extract_text(file) → ExtractResult, AudioProvider.transcribe(file, lang) → TranscriptResult, VisionProvider.describe(image) → VisionResult, LLMProvider.complete(prompt, schema) → LLMResult
- And cada Result é Pydantic model com text, confidence, raw, meta
- And apps/ai_providers/registry.py fornece get_provider(kind) que seleciona ativo de maior priority com health!=down
- And mypy strict passa

FRs: FR55 · NFRs: NFR37, NFR41 · ADRs: 006, 008.

#### Story 4.3a — Driver MistralOCR

As a Bruno, I want driver MistralOCR implementando OCRProvider, So that MVP tem OCR primário funcional.

AC:
- Given Stories 4.1+4.2 When Story 4.3a completa Then apps/ai_providers/providers/mistral_ocr.py implementa OCRProvider
- And respeita timeout configurável (default 30s) + retry tenacity 3x exponencial
- And erros mapeiam para ProviderUnavailable / ExtractionFailed
- And VCR.py cassettes versionados cobrem: happy path PDF, happy path imagem, 429, 500, timeout
- And ≥85% cobertura

FRs: FR56 · NFRs: NFR34, NFR42, NFR43 · ADRs: 006.

#### Story 4.3b — Driver OcrSpace (fallback)

As a Bruno, I want driver OcrSpace como fallback do MistralOCR, So that queda do primário não quebra ingestão.

AC:
- Given Story 4.3a When Story 4.3b completa Then apps/ai_providers/providers/ocr_space.py implementa OCRProvider
- And priority menor que Mistral em seed_dev
- And mesmo padrão timeout/retry/erros/VCR/cobertura da 4.3a

FRs: FR56 · NFRs: NFR34, NFR42, NFR43 · ADRs: 006.

#### Story 4.3c — Driver GroqWhisper (transcrição áudio)

As a Bruno, I want driver GroqWhisper implementando AudioProvider, So that submissão por áudio funciona.

AC:
- Given Stories 4.1+4.2 When Story 4.3c completa Then apps/ai_providers/providers/groq_whisper.py implementa AudioProvider
- And suporta mp3/m4a/wav/ogg/webm
- And transcribe(file, lang='pt') retorna TranscriptResult com text + segments[{start,end,text}] para sync com wavesurfer
- And timeout/retry/erros/VCR com fixtures de áudio curto (5s + 1min) + ≥85% cobertura

FRs: FR25, FR57 · NFRs: NFR34, NFR42, NFR43 · ADRs: 006.

#### Story 4.3d — Driver ClaudeLLM

As a Bruno, I want driver ClaudeLLM implementando LLMProvider, So that extração estruturada funciona.

AC:
- Given Stories 4.1+4.2 When Story 4.3d completa Then apps/ai_providers/providers/claude_llm.py implementa LLMProvider
- And complete(prompt, schema) usa Anthropic SDK com tool-use / JSON mode para garantir schema Pydantic válido
- And usa prompt caching (cache_control em system prompts longos)
- And timeout/retry/erros/VCR/≥85% cobertura
- And teste cobre schema válido e retry em schema inválido (1 retry antes de levantar ExtractionFailed)

FRs: FR56, FR57 · NFRs: NFR34, NFR42, NFR43 · ADRs: 006.

#### Story 4.4 — Dashboard /rh/providers/ (UI HTMX)

As a RH admin, I want listar/ativar/desativar providers e ver saúde + quota, So that opero IA sem precisar do Django admin.

AC:
- Given rh_admin autenticado When GET /rh/providers/ Then vê tabela HTMX: name, kind, priority, status (badge colorida), quota_used/monthly, última checagem
- And botões Ativar/Desativar disparam POST idempotente com CSRF
- And reorder via drag-and-drop Alpine.js persiste priority
- And toda mudança dispara AuditLog via Story 3.2
- And requer @require_role('rh_admin')

FRs: FR58 · NFRs: NFR28 · ADRs: 006, ADR-009.

#### Story 4.5 — Health check + fallback automático em cascata

As a Bruno, I want job periódico que pinga cada provider e sistema que faz fallback para próximo em priority, So that degradação não quebra ingestão.

AC:
- Given Stories 4.1-4.3 When cron `health_check_providers` roda (a cada 5min) Then chama método .ping() de cada driver ativo e atualiza health_status + last_check_at
- And registry.get_provider(kind) pula provider com status=down; se todos down, raises AllProvidersDown
- And chamada runtime que falha com ProviderUnavailable marca provider como degraded e tenta próximo em priority
- And teste integração simula queda do Mistral → ocr.space atende
- And evento `ai.provider.fallback` emitido para telemetria (Epic 12)

FRs: FR59 · NFRs: NFR35, NFR42, NFR43, NFR44 · ADRs: 006, 011.

#### Story 4.6 — Notificação email RH em fallback/quota

As a RH admin, I want receber email quando provider cai ou quota >80%, So that ajo antes do usuário sentir.

AC:
- Given Story 4.5 When health_status transiciona para down OU quota_used/quota_monthly ≥ 0.8 Then job envia email HTML para rh_admins ativos
- And template render provider.name + motivo + link dashboard
- And deduplicação: mesmo evento não gera 2 emails em 1h (Redis key TTL)
- And AuditLog `ai.provider.alert_sent` registrado
- And teste usa django mail outbox

FRs: FR60 · NFRs: NFR36 · ADRs: D1.4.

#### Story 4.7 — Destinatários de notificações (fallback/incidentes)

As a RH admin, I want gerenciar lista de destinatários de alertas operacionais, So that quem recebe "provider down" / "quota" / "IMAP disconnect" / "backup fail" / "deploy" é configurável sem deploy.

AC:
- Given Story 3.7 When Story 4.7 completa Then apps.notifications.models.NotificationRecipient tem: id UUID, email, nome, canais JSONB (`{fallback_provider, quota_alert, imap_disconnect, backup_fail, deploy}` booleanos), is_active bool
- And UI /rh/notificacoes/destinatarios/ lista/cria/edita/desativa via HTMX (requer @require_role('rh_admin'))
- And seed_dev popula 1 registro (Bruno, rh@greenhousedf.com.br) com todos canais ON
- And services.send_operational_alert(channel, subject, body) consulta recipients ativos com canais[channel]=True e envia
- And Stories 4.6 + 7.2b + 13.3b + 13.4a + 14.3b consomem esse service
- And AuditLog em mudanças
- And ≥85% cobertura

FRs: FR86 · NFRs: NFR28 · ADRs: D1.4.

---

### Epic 5 — Submissão multimodal pelo gestor

#### Story 5.1 — Modelo Requisicao + máquina de estados

As a Claude Code, I want Requisicao com FSM explícita, So that transições são validadas e auditadas.

AC:
- Given Epic 2 When Story 5.1 completa Then apps.requisitions.models.Requisicao tem: id UUID, criado_por FK User, tomador FK, circulo FK, status TextChoices (rascunho/enviado/processando/revisao/aprovado/rejeitado/esclarecimento), titulo, descricao, payload_ia JSONB, score_confianca decimal, created_at, updated_at
- And django-fsm ou custom FSM em services: transições válidas são (rascunho→enviado), (enviado→processando), (processando→revisao), (revisao→aprovado|rejeitado|esclarecimento), (esclarecimento→enviado)
- And transição inválida levanta DomainValidationError
- And AuditableMixin ligado
- And factory + ≥85% cobertura

FRs: FR10, FR11 · NFRs: NFR45 · ADRs: D4.2.

#### Story 5.2 — Portal gestor: form Nova Requisição (HTMX)

As a gestor, I want página simples com título + descrição + campo multimodal, So that submeto em ≤2min sem fricção.

AC:
- Given autenticado com is_cadastro_completo When GET /gestor/nova-requisicao/ Then vê form HTMX com campos: titulo (text), descricao (textarea), anexos (drop zone), botão Enviar
- And mobile-first Tailwind + daisyUI
- And POST cria Requisicao em status=rascunho, redirect /gestor/requisicoes/<id>/enviada/
- And validação client-side via Alpine.js + server-side
- And cadastro incompleto redireciona Story 2.4 (bypass previsto)

FRs: FR12, FR13 · NFRs: NFR2, NFR45, NFR48 · ADRs: D4.3, ADR-009.

#### Story 5.3 — Upload TUS resumível (áudio/PDF/imagem/texto)

As a gestor, I want upload que retoma após quedas de rede, So that áudio de 10min não é perdido.

AC:
- Given Story 5.2 When gestor anexa arquivo ≤100MB Then upload usa protocolo TUS (tus-py-server) em /tus/
- And chunks de 5MB, retomada automática se aba fecha e reabre
- And tipos aceitos: mp3/m4a/wav/ogg/webm, pdf, jpg/png/webp, txt
- And tipo inválido rejeitado com mensagem amigável
- And arquivo salvo em storage (Filesystem dev / MinIO prod) com UUID path
- And RequisicaoAnexo model liga Requisicao ↔ storage path + mime + size

FRs: FR14, FR15 · NFRs: NFR2, NFR16 · ADRs: 006.

#### Story 5.4a — Pipeline etapa 1: transcribe + OCR → texto bruto

As a Claude Code, I want primeira etapa do pipeline que extrai texto de qualquer anexo, So that LLM recebe input uniforme.

AC:
- Given Stories 4.3a-c + 5.3 When Requisicao transita enviado→processando Then `@idempotent_actor` extract_raw_text(req_id) roda
- And áudio/vídeo → AudioProvider.transcribe() → armazena TranscriptResult completo (text + segments) em RequisicaoAnexo.transcript_json
- And pdf/imagem → OCRProvider.extract_text() → armazena texto em RequisicaoAnexo.extracted_text
- And falha de provider cai no fallback da Story 4.5; se todos down → status=revisao com flag `needs_manual_review=True`
- And teste cobre áudio OK, PDF OK, imagem OK, provider down

FRs: FR16, FR25, FR26, FR61 · NFRs: NFR15 · ADRs: D4.2, 006, 011.

#### Story 5.4b — Pipeline etapa 2: LLM extract + schema Pydantic + transição revisao

As a Claude Code, I want segunda etapa que converte texto bruto em payload_ia estruturado + transiciona FSM, So that RH recebe rascunho editável.

AC:
- Given Story 5.4a + Story 4.3d When extract_raw_text completa Then actor estruturar_requisicao(req_id) roda em cadeia
- And concatena textos brutos + descrição original e passa a LLMProvider.complete(prompt, schema=RequisicaoExtractedSchema)
- And RequisicaoExtractedSchema (Pydantic) valida: cargo, senioridade, requisitos[], responsabilidades[], localidade, tipo_contrato, faixa_salarial, beneficios[]
- And schema inválido após 1 retry → status=revisao com motivo + anexo bruto preservado (não perde dado)
- And sucesso: payload_ia populado, transição processando→revisao, AuditLog emitido
- And teste cobre schema válido, schema inválido 1x depois válido, schema inválido 2x → revisao com motivo

FRs: FR17, FR27, FR62 · NFRs: NFR15, NFR46 · ADRs: D4.2, D4.4, 006, 011.

#### Story 5.5 — Rascunho com score de confiança por campo

As a Claude Code, I want cada campo de payload_ia ter score 0-1, So that RH vê o que precisa atenção.

AC:
- Given Story 5.4b When LLM retorna extração Then schema força `{valor: T, confianca: float 0-1}` por campo via self-eval estruturado no próprio prompt (JSON mode / tool-use) — SEM dependência de logprobs do provider
- And score_confianca geral = média ponderada dos campos obrigatórios
- And serializer marca `needs_review=True` em cada campo com `confianca < 0.8`
- And UI da Story 6.3 lê esse flag para destacar amarelo
- And teste valida schema com fixture real e 2 sintéticos (1 alta confiança, 1 baixa)

FRs: FR18, FR28, FR63 · NFRs: NFR46 · ADRs: D4.4.

#### Story 5.6 — Email "estamos processando" ao gestor

As a gestor, I want email imediato de confirmação com previsão, So that sei que funcionou.

AC:
- Given Story 5.1 When Requisicao transita rascunho→enviado Then email enviado a criado_por.email
- And template inclui: titulo, link "Acompanhar", previsão "até 10 min"
- And envio via Dramatiq actor idempotente
- And teste com django mail outbox valida subject + body contém titulo

FRs: FR73, FR74 · NFRs: NFR45 · ADRs: D1.4.

#### Story 5.7 — Email "está em revisão" ao gestor

As a gestor, I want email quando IA termina e RH vai revisar, So that sei prazo.

AC:
- Given Story 5.4 When transita processando→revisao Then email enviado com link /gestor/requisicoes/<id>/
- And inclui resumo de 3 linhas do rascunho
- And SLA médio de revisão RH (configurável, default 48h)
- And teste valida template

FRs: FR75, FR76 · NFRs: NFR45 · ADRs: D1.4.

#### Story 5.8 — Telemetria de captura (eventos)

As a Bruno, I want eventos estruturados em cada etapa do pipeline, So that Epic 12 tem dados prontos.

AC:
- Given Stories 5.1-5.7 When fluxo roda Then emite eventos: `requisicao.created`, `requisicao.submitted`, `ai.process.started`, `ai.process.completed`, `ai.process.failed`, `requisicao.review_ready`
- And cada evento tem: req_id, user_id (anonimizável), duration_ms, provider_used, success bool, timestamp
- And eventos gravados em tabela telemetry_event (apps/telemetry) com TTL 90d
- And teste valida 6 eventos em fluxo happy path

FRs: FR79, FR80 · NFRs: NFR33 · ADRs: D1.4.

---

### Epic 6 — Revisão RH e publicação de vagas

#### Story 6.1 — Kanban /rh/requisicoes/ (HTMX + colunas por status)

As a RH operator, I want kanban com colunas Revisão/Esclarecimento/Aprovado/Rejeitado, So that vejo fila de trabalho.

AC:
- Given @require_role_any('rh_admin','rh_operator') When GET /rh/requisicoes/ Then vê 4 colunas HTMX com cards (titulo, gestor, score_confianca badge, tempo em status)
- And card clicável abre /rh/requisicoes/<id>/revisar/
- And filtro por círculo, tomador, gestor, range de data
- And paginação infinite scroll HTMX
- And ordenação: mais antigo primeiro (FIFO) por default

FRs: FR29, FR30 · NFRs: NFR3, NFR28 · ADRs: D4.5.

#### Story 6.2a — Player wavesurfer + transcript sincronizado (áudio)

As a RH, I want ouvir áudio com transcript destacado em tempo real, So that revisão de submissões por áudio é rápida.

AC:
- Given Stories 5.3+5.4a When abre /rh/requisicoes/<id>/revisar/ com anexo áudio Then wavesurfer.js renderiza waveform com timestamps
- And transcript (segments[] da Story 4.3c) mostra trechos destacados conforme playback
- And clicar palavra do transcript salta o áudio para timestamp correspondente
- And controles: play/pause, velocidade (0.75/1/1.25/1.5x), skip +/-10s
- And teste E2E com anexo áudio fixture valida highlight sync

FRs: FR31 · NFRs: NFR3 · ADRs: D4.5.

#### Story 6.2b — Viewer inline PDF / imagem

As a RH, I want anexos PDF/imagem renderizados inline na tela de revisão, So that não alterno janelas.

AC:
- Given Story 5.3 When abre /rh/requisicoes/<id>/revisar/ com anexo PDF/imagem Then viewer renderiza inline (PDF via pdf.js, imagem via <img>)
- And PDF tem controles de zoom/página
- And imagem tem zoom/pan
- And texto extraído da Story 5.4a mostrado em painel lateral (toggle)
- And múltiplos anexos renderizados em tabs

FRs: FR32 · NFRs: NFR3 · ADRs: D4.5.

#### Story 6.3 — Diff visual: rascunho IA vs texto bruto + highlight de baixa confiança

As a RH, I want ver quais campos foram extraídos vs inferidos e destacar baixa confiança, So that reviso o que importa.

AC:
- Given Story 5.5 When abre tela de revisão Then cada campo de payload_ia é input editável
- And fundo amarelo em campos needs_review=True
- And tooltip mostra confianca + trecho-fonte do texto bruto
- And edição dispara AuditLog com before/after

FRs: FR33, FR34 · NFRs: NFR28 · ADRs: D4.5.

#### Story 6.4 — Ações: Aprovar / Rejeitar / Solicitar Esclarecimento

As a RH, I want 3 ações terminais na revisão, So that fecho o ciclo.

AC:
- Given tela de revisão When clica Aprovar Then transita revisao→aprovado, dispara Story 6.5
- And Rejeitar: abre modal com motivo obrigatório (textarea), transita→rejeitado, dispara email gestor
- And Solicitar Esclarecimento: abre modal com perguntas, transita→esclarecimento, dispara email gestor com link para completar
- And cada ação requer @require_role_any('rh_admin','rh_operator')
- And AuditLog em todas

FRs: FR35, FR41, FR42 · NFRs: NFR28 · ADRs: D4.2.

#### Story 6.5 — Transição aprovado → criação de Vaga ativa

As a Bruno, I want aprovação transformar Requisicao em Vaga publicada, So that matching (Epic 8) tem o que ranquear.

AC:
- Given Story 6.4 quando aprovado Then services.promote_to_vaga(req) cria apps.vagas.models.Vaga copiando campos de payload_ia
- And Vaga tem: id UUID, requisicao FK unique, titulo, descricao_md, requisitos JSONB, status (ativa/pausada/fechada), publicada_em, embedding vector (preparado para Epic 8)
- And transição é transacional: Vaga created + Requisicao.status=aprovado + AuditLog em 1 transaction
- And evento `vaga.published` emitido para Epic 8 indexar embedding
- And teste valida rollback em falha

FRs: FR48, FR49, FR50 · NFRs: NFR6 · ADRs: D1.5, D4.2.

#### Story 6.6 — Notificação gestor em aprovação / rejeição / esclarecimento

As a gestor, I want saber o desfecho sem precisar abrir o sistema, So that acompanho por email.

AC:
- Given Story 6.4 When ação terminal Then email enviado a criado_por.email com template por ação
- And Aprovado: "Sua vaga foi publicada" + link /gestor/vagas/<id>/
- And Rejeitado: motivo do RH + link para nova submissão
- And Esclarecimento: perguntas do RH + link para completar
- And idempotente (Dramatiq retry não duplica)
- And AuditLog registra `email.sent` por ação

FRs: FR51, FR52, FR77, FR78 · NFRs: NFR45 · ADRs: D1.4.

---

**Lote 1 + Lote 2 total: 51 stories** (Lote 1: 26, Lote 2: 25). Ajustes pós-revisão Amelia 2026-04-21 no Lote 2: Story 4.3 → 4.3a/b/c/d; Story 5.4 → 5.4a/b; Story 6.2 → 6.2a/b; AC 5.5 desambiguado (self-eval JSON mode, sem logprobs); app `vagas` adicionado retroativamente à Story 1.1 (13 apps total).

---

### Epic 7 — Ingestão passiva de currículos por e-mail

#### Story 7.1 — AiEmailAccount model + credenciais IMAP criptografadas

As a Bruno, I want registro de contas IMAP com senha criptografada, So that configuro caixas sem commitar credencial.

AC:
- Given Story 3.7 When Story 7.1 completa Then apps.email_ingestion.models.AiEmailAccount tem: id UUID, email, imap_host, imap_port, username, password EncryptedCharField, use_ssl bool, last_uid bigint, is_active bool, last_idle_at, health (healthy/disconnected/auth_failed)
- And admin Django permite cadastrar
- And seed_dev cria registro placeholder para `curriculos@greenhousedf.com.br` (senha vazia até credenciais chegarem)
- And AuditLog em mudanças
- And ≥85% cobertura

FRs: FR19 · NFRs: NFR14, NFR24 · ADRs: 013, D3.4.

#### Story 7.2a — Daemon gv-email-ingestion: bootstrap IMAP IDLE

As a Bruno, I want processo PM2 separado que escuta IMAP IDLE e enfileira novos emails, So that captura é em tempo real.

AC:
- Given Story 7.1 + ADR-004 When `pm2 start ecosystem.config.js` Then processo `gv-email-ingestion` roda apps/email_ingestion/daemon.py
- And conecta via imapclient por conta ativa, entra em IDLE
- And ao receber EXISTS, fetch UIDs > last_uid e enfileira `@idempotent_actor` process_email(account_id, uid)
- And atualiza last_uid após enfileirar com sucesso
- And teste usa IMAP mock (aioimaplib) cobrindo happy path: idle → novo email → enfileira

FRs: FR20 · NFRs: NFR5, NFR24 · ADRs: 013, ADR-004.

#### Story 7.2b — Daemon: reconnect + health tracking + alerta

As a Bruno, I want reconexão automática + health visível + alerta em disconnect prolongado, So that falha silenciosa não ocorre.

AC:
- Given Story 7.2a When conexão cai Then daemon tenta reconexão com backoff exponencial (1s, 2s, 4s... cap 60s)
- And health=healthy atualizado em AiEmailAccount.last_idle_at a cada heartbeat 30s
- And após 5min de falha contínua → health=disconnected + emite evento `email.imap.disconnected` (Story 12.1)
- And disparo de email rh_admins (dedup 1h, reusa padrão Story 4.6)
- And auth_failed é estado terminal (não retry; exige intervenção)
- And teste cobre disconnect transitório, disconnect prolongado, auth_failed

FRs: FR20 · NFRs: NFR5, NFR24 · ADRs: 013.

#### Story 7.3 — Parse MIME: corpo + attachments + dedup por Message-ID

As a Claude Code, I want serviço que recebe raw bytes e devolve EmailParsed, So that lógica de negócio não lida com MIME.

AC:
- Given Story 7.2 When process_email roda Then services.parse_email(raw) usa email.parser e retorna EmailParsed Pydantic: message_id, from_, to_, subject, date, body_text, body_html, attachments[{filename, mime, bytes_path}]
- And attachments ≤20MB salvos em storage (dev/MinIO); >20MB rejeitado com quarentena
- And IncomingEmail model criado com message_id unique (dedup natural do IMAP)
- And Message-ID já existente → no-op idempotente
- And teste com fixtures .eml (multipart, só texto, só anexo, anexo corrompido)

FRs: FR21 · NFRs: NFR15 · ADRs: 013.

#### Story 7.4 — Classificador de email (currículo vs outros)

As a Claude Code, I want classificar cada email antes de extrair CV, So that não processo spam/confirmações como candidato.

AC:
- Given Story 7.3 When EmailParsed recebido Then services.classify_email() aplica: (1) regra — tem anexo PDF/doc com keywords "curriculo|cv|resume" no nome OU assunto contém "candidat|vaga" → is_cv=True; (2) se dúbio, LLMProvider.complete com schema `{is_cv: bool, motivo: str, confianca: 0-1}`
- And is_cv=False → IncomingEmail.status='ignored', AuditLog
- And is_cv=True com confianca<0.7 → status='quarantine' (Story 7.6)
- And is_cv=True com confianca≥0.7 → dispara Story 7.5
- And teste cobre 3 cenários + fallback quando LLM down

FRs: FR22 · NFRs: NFR15, NFR24 · ADRs: 006, 013.

#### Story 7.5a — Extração CV: OCR + LLM → payload estruturado

As a Claude Code, I want etapa que pega anexo e devolve CurriculoExtracted validado, So that persistência é isolada da extração.

AC:
- Given Stories 7.4 + 4.3a + 4.3d When email classificado como CV Then actor extract_cv_payload(incoming_email_id) roda
- And OCRProvider.extract_text(attachment) → texto bruto
- And LLMProvider.complete(prompt, schema=CurriculoExtractedSchema) extrai: nome, email, telefone, cargo_atual, senioridade, skills[], experiencias[], formacao[], localidade, linkedin_url (self-eval `{valor, confianca}` por campo conforme padrão Story 5.5)
- And retorna ExtractionResult{raw_text, payload, score_geral} persistido em tabela temp para etapa 7.5b
- And teste cobre happy path, schema inválido após 1 retry, provider down (fallback Story 4.5)

FRs: FR23, FR26, FR27, FR28 · NFRs: NFR15 · ADRs: 006, 013.

#### Story 7.5b — Persistência: Candidato + CurriculoVersao + branching quarentena

As a Claude Code, I want etapa que materializa extração em registros e decide rota (catalogado vs quarentena), So that Epic 8 tem dados e RH resolve ambíguos.

AC:
- Given Story 7.5a When ExtractionResult disponível Then services.persist_cv(result) cria ou recupera Candidato:
  - chave primária de match: email normalizado (lower+trim); fallback: hash(nome_canonicalizado + telefone_normalizado) se sem email
- And cria CurriculoVersao{candidato_fk, raw_text, payload, score_geral, source='email', incoming_email_fk, created_at}
- And candidato pré-existente gera nova versão (append-only, nunca sobrescreve)
- And branching final: score_geral<0.7 → CurriculoVersao.status='quarantine' (Story 7.6); ≥0.7 → 'catalogado' (dispara embed Story 8.3)
- And operação atômica; falha parcial rollback
- And teste cobre novo candidato, candidato existente (nova versão), quarentena, catalogado

FRs: FR23 · NFRs: NFR9, NFR15 · ADRs: 013.

#### Story 7.6 — Quarentena: UI RH para resolver emails/CVs com baixa confiança

As a RH, I want lista de emails/CVs em quarentena com ações Aprovar/Rejeitar/Reprocessar, So that não perco candidato viável.

AC:
- Given Stories 7.4+7.5 When GET /rh/email-quarantine/ Then vê lista paginada com preview, motivo, data, anexos
- And ações: Aprovar (força processamento), Rejeitar (status=ignored + motivo), Reprocessar (rerun classify+extract)
- And requer @require_role_any('rh_admin','rh_operator')
- And AuditLog em cada ação
- And feed é HTMX auto-refresh a cada 30s

FRs: FR24 · NFRs: NFR28 · ADRs: D4.5.

#### Story 7.7 — Whitelist de remetentes autorizados da caixa de CVs

As a RH admin, I want gerenciar lista de remetentes autorizados, So that apenas emails desses endereços/domínios são processados (defesa contra spam/abuso).

AC:
- Given Story 7.1 When Story 7.7 completa Then apps.email_ingestion.models.AuthorizedSender tem: id UUID, pattern (email completo OU wildcard tipo `*@parceira.com.br`), descricao, is_active, added_by FK, added_at
- And UI /rh/email-senders/ lista/cria/edita/desativa via HTMX (requer @require_role('rh_admin'))
- And services.classify_email (Story 7.4) consulta whitelist ANTES de LLM: remetente não-match → status='ignored_unauthorized' sem custo IA
- And whitelist vazia = modo permissivo (MVP); flag `strict_sender_whitelist` liga modo restrito
- And AuditLog em mudanças
- And seed_dev vazio (Bruno popula pós-deploy)
- And ≥85% cobertura

FRs: FR85 · NFRs: NFR24, NFR28 · ADRs: 013, D1.4.

---

### Epic 8 — Matching vaga × candidato

#### Story 8.1 — pgvector: extensão + index + migração de embeddings

As a Bruno, I want pgvector extension + colunas embedding vector(1536) em Vaga e CurriculoVersao, So that busca semântica escala.

AC:
- Given Story 6.5 + Story 7.5 When Story 8.1 completa Then migration `CREATE EXTENSION IF NOT EXISTS vector` roda
- And Vaga.embedding vector(1536) nullable + IVFFlat index (lists=100)
- And CurriculoVersao.embedding vector(1536) nullable + IVFFlat index
- And teste valida EXPLAIN ANALYZE usa index em query knn

FRs: FR43 · NFRs: NFR6, NFR8 · ADRs: D1.5, ADR-003.

#### Story 8.2 — Embed Vaga em publicação (listener vaga.published)

As a Claude Code, I want job que gera embedding quando Vaga é publicada, So that matching tem Vaga indexável imediatamente.

AC:
- Given Story 8.1 + evento `vaga.published` (Story 6.5) When evento emitido Then actor embed_vaga(vaga_id) roda
- And usa LLMProvider.embed(texto concatenado: titulo + descricao_md + requisitos) → vector(1536)
- And salva em Vaga.embedding, marca embedded_at
- And idempotente: reprocessar no-op se embedding existe (a menos que texto mudou via hash)
- And teste valida embedding gerado + retry em falha provider

FRs: FR44 · NFRs: NFR6 · ADRs: D1.5.

#### Story 8.3 — Embed CurriculoVersao em criação

As a Claude Code, I want embedding gerado quando CurriculoVersao é criada, So that CV novo é matchable imediatamente.

AC:
- Given Stories 8.1+7.5 When CurriculoVersao salva com status='catalogado' Then actor embed_curriculo(curriculo_versao_id) roda
- And usa embed(payload extraído concatenado: cargo + skills + experiencias[].cargo+descricao)
- And salva em embedding, marca embedded_at
- And idempotente por hash
- And teste valida geração + retry

FRs: FR44 · NFRs: NFR6 · ADRs: D1.5.

#### Story 8.4a — Matching service: filtros hard + knn + score híbrido + explicabilidade

As a Claude Code, I want services.match_candidates(vaga_id, k=50) puro (sem cache) retornando ranking explicável, So that algoritmo é testável isolado de infra.

AC:
- Given Stories 8.2+8.3 When chamado Then: (1) aplica filtros hard (localidade compatível, tipo_contrato compatível) restringindo Candidatos; (2) knn em CurriculoVersao.embedding <-> Vaga.embedding; (3) score final = 0.7 * (1 - cosine_distance) + 0.3 * rule_score (skills match + senioridade match)
- And retorna MatchResult[{candidato_id, score, explicacao{vector_sim, skills_matched[], gaps[], senioridade_match}}] ordenado por score desc
- And teste unitário com fixtures (2 vagas, 5 candidatos) valida ordem + explicação + filtros hard

FRs: FR45, FR46 · NFRs: NFR6, NFR8 · ADRs: D1.5.

#### Story 8.4b — Cache Redis de matching + invalidação por signal

As a Claude Code, I want cache Redis para match_candidates + invalidação dirigida, So that latência de /rh/vagas/<id>/candidatos/ fica <200ms sem retornar resultado velho.

AC:
- Given Story 8.4a When match_candidates(vaga_id) é chamado Then wrapper `match_candidates_cached` consulta cache key `match:{vaga_id}:v{version}` TTL 1h
- And invalidação via signal pós-`embed_curriculo` (Story 8.3) que itera Vagas ativas cujos filtros hard (mesma localidade E tipo_contrato compatível) batem com a nova CurriculoVersao e executa `cache.delete(f'match:{vaga_id}:v{version}')` em cada
- And `version` incrementa quando filtros da Vaga mudam (edit via UI admin)
- And teste cobre: cache hit, cache miss, invalidação após novo CV compatível, não-invalidação quando CV incompatível

FRs: FR45 · NFRs: NFR6, NFR8 · ADRs: D1.5, ADR-005.

#### Story 8.5 — UI ranking com explicabilidade

As a RH, I want /rh/vagas/<id>/candidatos/ com ranking + motivo visual, So that decido com contexto.

AC:
- Given Story 8.4 When GET rota Then lista top 50 com card: nome, score badge, skills matched (verde), gaps (vermelho), senioridade match, link para CurriculoVersao
- And filtro por score mínimo, localidade, faixa salarial
- And paginação HTMX
- And ação "Descartar para esta vaga" persiste preferência
- And requer role RH

FRs: FR47 · NFRs: NFR28 · ADRs: D4.5.

#### Story 8.6 — Notificação RH: "novo CV com match alto em vaga ativa"

As a RH, I want email quando CV novo tem score≥0.85 em alguma vaga ativa, So that ajo rápido.

AC:
- Given Stories 8.3+8.4 When embed_curriculo completa Then actor check_matches_for_new_cv(cv_id) roda
- And para cada Vaga ativa, calcula score; se ≥0.85, emite notificação
- And dedup: mesmo (cv, vaga) não notifica 2x em 30d
- And email agrupa múltiplas vagas em lista
- And AuditLog `match.high_score_alert`

FRs: FR45 · NFRs: NFR6 · ADRs: D1.5, D1.4.

---

### Epic 9 — Detecção de duplicatas (3 camadas)

#### Story 9.1 — Camada 1: hash exato (arquivo + email normalizado)

As a Claude Code, I want detecção O(1) por hash SHA-256 do arquivo e email normalizado, So that capturo duplicata trivial antes de embed.

AC:
- Given Story 7.3 (binário persistido em path estável) + Story 7.5b (CurriculoVersao catalogada) When CurriculoVersao criada Then services.detect_duplicate_l1(cv) checa: (a) hash SHA-256 computado sobre o binário original em storage (mesma fonte da Story 7.3, reprodutível) bate com CurriculoVersao existente; (b) email normalizado (lower + trim) bate com Candidato existente
- And match → cria DuplicateCandidate{cv_new_id, cv_match_id OR candidato_match_id, layer=1, score=1.0, status=pending}
- And teste cobre mesmo arquivo, email igual com caixa diferente, nenhum match

FRs: FR36 · NFRs: NFR24 · ADRs: D1.5.

#### Story 9.2 — Camada 2: fuzzy (trigram nome + email + telefone)

As a Claude Code, I want detecção fuzzy usando pg_trgm, So that variações (acentos, abreviação) são pegas.

AC:
- Given Story 9.1 quando L1 não acha Then services.detect_duplicate_l2(cv) usa pg_trgm similarity em nome (>0.7) combinado com match parcial email (domínio igual) OU telefone normalizado igual
- And score L2 = média ponderada das similaridades
- And match ≥0.75 → DuplicateCandidate layer=2
- And extension pg_trgm habilitada via migration + index GIN
- And teste cobre nomes com acentos, abreviação de sobrenome, email diferente mas telefone igual

FRs: FR37 · NFRs: NFR24 · ADRs: D1.5, 010.

#### Story 9.3 — Camada 3: LLM raciocinador (atrás de flag)

As a Bruno, I want camada 3 opcional que usa LLM para casos ambíguos (score L2 entre 0.55-0.75), So that capturo duplicatas que rules perdem.

AC:
- Given Story 9.2 + flag `enable_duplicate_llm_layer` ativa + score L2 entre 0.55-0.75 When detect_duplicate_l3 roda Then envia os 2 CVs ao LLMProvider com schema `{is_duplicate: bool, motivo: str, confianca: 0-1}`
- And confianca≥0.75 + is_duplicate → DuplicateCandidate layer=3
- And flag desligada → skip silencioso
- And cache Redis TTL 24h por par (cv_a, cv_b) ordenado
- And teste com fixture simulando LLM

FRs: FR38 · NFRs: NFR24 · ADRs: 010, Fatia 1.1.

#### Story 9.4 — UI alerta duplicata: Mesclar / Relacionar / Descartar

As a RH, I want lista de alertas com ações terminais, So that resolvo e fecho.

AC:
- Given Stories 9.1-9.3 When GET /rh/duplicatas/ Then lista DuplicateCandidate com status=pending: mostra side-by-side 2 candidatos, diff visual, camada detectora, score, motivo
- And Mesclar: services.merge_candidates(primary, secondary) — consolida CurriculoVersoes sob primary, marca secondary.merged_into=primary, preserva histórico
- And Relacionar: cria vínculo não destrutivo (tabela CandidatoRelacao) sem mesclar
- And Descartar: status=false_positive + motivo
- And cada ação gera AuditLog + é reversível (Story 9.5)

FRs: FR39 · NFRs: NFR28 · ADRs: D1.5, D1.4, D4.5.

#### Story 9.5 — Reversibilidade de merge + AuditLog íntegro

As a RH, I want desfazer merge se identificamos engano, So that não perco dados irrecuperáveis.

AC:
- Given Story 9.4 When RH acessa /rh/duplicatas/<id>/desfazer/ (até 30d após merge) Then services.unmerge_candidates(merge_id) restaura secondary com CurriculoVersoes originais
- And AuditLog de merge tem before/after suficiente para unmerge
- And verify_audit_chain continua PASS
- And >30d bloqueia com mensagem "retenção expirada"
- And teste cobre merge→unmerge idempotente

FRs: FR40 · NFRs: NFR19, NFR24 · ADRs: D1.4, D1.5.

---

### Epic 10 — Hub unificado de revisão (Inbox)

#### Story 10.1 — Agregador /inbox/ (Requisições revisão + CV quarentena + duplicatas + matches alertas)

As a RH, I want uma tela que agrega tudo human-in-the-loop, So that começo meu dia sabendo o que fazer.

AC:
- Given Stories 6.1 + 7.6 + 9.4 + 8.6 When GET /inbox/ Then vê 4 seções colapsáveis: (1) Requisições em revisão (Story 6.1 reusando queryset), (2) Emails/CVs em quarentena (Story 7.6), (3) Alertas de duplicata pendentes (Story 9.4), (4) Matches alta-confiança novos (Story 8.6)
- And contador por seção no topo
- And cada card linka para tela específica de ação
- And ordem: mais antigo primeiro por seção
- And requer role RH
- And render server-side HTMX, cache Redis 30s

FRs: agregador · NFRs: NFR3, NFR28 · ADRs: D4.5.

#### Story 10.2 — Filtros globais + atribuição a operador

As a RH admin, I want atribuir item do inbox a operador específico + filtros globais, So that divido trabalho com time.

AC:
- Given Story 10.1 When RH admin clica "Atribuir" num item Then modal lista rh_operators ativos e persiste InboxAssignment{item_type, item_id, assignee_id, assigned_at, assigned_by_id}
- And filtros globais: meus itens / sem atribuição / tomador X / período
- And operador só vê seus itens por default (toggle "ver todos")
- And AuditLog em cada atribuição

FRs: agregador · NFRs: NFR28 · ADRs: D4.5.

#### Story 10.3 — Ações em lote (resolver múltiplos alertas)

As a RH, I want selecionar múltiplos itens e aplicar ação em massa (ex: descartar 10 duplicatas), So that limpo inbox rápido quando bate certeza.

AC:
- Given Story 10.1 When seleciona ≥2 cards de mesmo tipo Then barra flutuante aparece com ações disponíveis por tipo
- And confirmação modal exige texto "confirmar" digitado
- And execução em Dramatiq com progresso HTMX
- And AuditLog por item
- And limite 50 itens por operação

FRs: agregador · NFRs: NFR28 · ADRs: D1.4, D4.5.

---

**Lote 1 + 2 + 3 total: 71 stories** (Lote 1: 26, Lote 2: 25, Lote 3: 20).

---

### Epic 11 — Help contextual universal

#### Story 11.1 — HelpSnippet model + admin editável

As a Bruno, I want model simples para snippets de ajuda, So that RH edita tooltips sem redeploy.

AC:
- Given Epic 3 When Story 11.1 completa Then apps.help.models.HelpSnippet tem: id UUID, key slug unique, title, body_md (markdown), scope (tooltip/empty_state/breadcrumb), updated_at, updated_by FK
- And django-admin permite edit com preview markdown
- And seed_dev popula ≥15 snippets iniciais cobrindo formulários críticos (novo requisição, revisão, providers dashboard, inbox)
- And AuditLog via Story 3.2
- And ≥85% cobertura

FRs: FR73 · NFRs: NFR47 · ADRs: D1.4.

#### Story 11.2 — Tooltip engine (Alpine.js + HTMX)

As a usuário, I want hover em ícone "?" mostrar ajuda contextual, So that descubro sem sair da tela.

AC:
- Given Story 11.1 When elemento tem `data-help-key="slug"` Then Alpine.js dispara GET /api/help/<key>/ em hover/focus
- And endpoint retorna HTML renderizado de body_md com markdown-it server-side
- And cache Redis TTL 5min por key (invalidado em save do admin)
- And fallback gracioso: key inexistente → tooltip "Ajuda em construção"
- And acessibilidade: aria-describedby + navegável por teclado
- And teste E2E valida hover + conteúdo

FRs: FR74, FR75 · NFRs: NFR47 · ADRs: D4.5.

#### Story 11.3 — Breadcrumbs globais + empty states padronizados

As a usuário, I want breadcrumbs sempre presentes e empty states informativos, So that não me perco e sei o próximo passo.

AC:
- Given Story 11.1 When template estende base.html Then renderiza breadcrumb via template tag `{% breadcrumb %}` lendo URLconf namespace + titulos
- And component `{% empty_state key="..." %}` renderiza HelpSnippet scope=empty_state com ilustração + CTA
- And listas sem dados usam empty state em vez de tabela vazia
- And breadcrumb último item não-clicável
- And teste de template cobre 3 cenários

FRs: FR76, FR77 · NFRs: NFR47 · ADRs: ADR-009.

#### Story 11.4 — UI admin /admin/help/ com preview + versionamento

As a RH admin, I want UI própria (fora do Django admin) para editar snippets com preview lado-a-lado, So that edito com contexto.

AC:
- Given Story 11.1 When GET /admin/help/ Then lista paginada + filtro por scope/key
- And editor split: markdown ↔ preview HTMX em tempo real
- And histórico: cada save cria HelpSnippetVersion (append-only) com updated_by + timestamp
- And rollback: restaurar versão anterior
- And requer @require_role('rh_admin')

FRs: FR78 · NFRs: NFR28, NFR47 · ADRs: D4.5, D1.4.

#### Story 11.5 — SystemThreshold: confiança IA / similaridade duplicata / alerta quota

As a RH admin, I want configurar thresholds críticos do sistema sem deploy, So that calibro comportamento IA/duplicatas/alertas conforme operação real.

AC:
- Given Epic 3 When Story 11.5 completa Then apps.core.models.SystemThreshold (singleton) tem campos: min_confianca_requisicao (default 0.8), min_confianca_cv (default 0.7), dup_l2_min_score (default 0.75), dup_l3_score_range (default [0.55, 0.75]), quota_alert_ratio (default 0.8), match_alert_score (default 0.85)
- And UI /admin/thresholds/ editável via HTMX (requer @require_role('rh_admin'))
- And helpers `thresholds.get('key')` substituem literals hard-coded nas Stories 5.5, 7.4, 7.5b, 8.6, 9.2, 9.3, 4.6
- And cache Redis invalidado em save
- And AuditLog com before/after em cada mudança
- And seed_dev popula com defaults

FRs: FR87 · NFRs: NFR28, NFR47 · ADRs: D1.4.

---

### Epic 12 — Telemetria UX + IA-lê-logs

#### Story 12.1 — TelemetryEvent model + retenção 90d

As a Bruno, I want tabela única com TTL automático, So that eventos UX + sistema coexistem sem explodir storage.

AC:
- Given Story 5.8 When Story 12.1 completa Then apps.telemetry.models.TelemetryEvent tem: id UUID, event_name, user_id nullable, session_id, properties JSONB, occurred_at, inserted_at
- And index em (event_name, occurred_at) + (user_id, occurred_at)
- And comando `manage.py prune_telemetry` deleta >90d; cron diário via PM2
- And ingestor centralizado: `services.emit_event(name, props, user=None)` reusado por Story 5.8
- And anonimização: user_id=NULL após anonimizar_user (Story 3.6b)
- And ≥85% cobertura

FRs: FR79 · NFRs: NFR33, NFR37 · ADRs: D1.4.

#### Story 12.2 — Captura UX client-side (clicks, tempos, erros)

As a Claude Code, I want biblioteca mínima JS que emite eventos UX, So that medição é uniforme.

AC:
- Given Story 12.1 When template carrega Then `static/js/telemetry.js` expõe `window.track(name, props)` e auto-captura: page_view (com duração até unload), click em `[data-track]`, form_submit, js_error (window.onerror)
- And eventos buferizados no cliente e enviados em batch via navigator.sendBeacon para /api/telemetry/ingest/
- And endpoint valida schema e chama emit_event
- And rate-limit 100 eventos/min por session_id (dropa excesso com log)
- And teste cobre batch, beacon em unload, rate-limit

FRs: FR80 · NFRs: NFR38 · ADRs: D4.5.

#### Story 12.3 — Dashboard /admin/ux-insights (HTMX + charts)

As a Bruno, I want dashboard agregado com top events, funnels e erros, So that entendo uso sem abrir Grafana.

AC:
- Given Stories 12.1+12.2 When GET /admin/ux-insights/ Then vê cards: eventos por dia (7d), top 10 nomes, top erros JS, funil "novo → submetido → revisado → aprovado"
- And queries agregadas com cache Redis 5min
- And filtro por período, role, tomador
- And gráficos com Chart.js ou HTMX server-rendered SVG
- And requer @require_role('rh_admin')

FRs: FR81 · NFRs: NFR28, NFR37 · ADRs: D4.5.

#### Story 12.4 — Job LLM semanal: UX report em linguagem natural (Fatia 1.1, flag)

As a Bruno, I want LLM ler eventos da semana e gerar relatório narrativo, So that encontro insights sem pivotar manualmente.

AC:
- Given Story 12.3 + flag `enable_ux_llm_report` ON + ≥30d de dados When cron semanal (domingo 03h) roda Then actor generate_ux_report() agrega últimos 7d em estrutura determinística (top-N por event_name + contadores agregados + amostra estratificada de erros), serializa JSON e valida ≤30k tokens via tiktoken antes de enviar; se exceder, reduz amostra de erros iterativamente até caber OU aborta com log `ux_report.skipped_oversized`
- And envia ao LLMProvider com prompt "encontre 3 atritos + 3 oportunidades + 1 bug suspeito" e schema Pydantic
- And report salvo em apps.telemetry.models.UxReport (week_of, summary_md, findings JSONB)
- And email para rh_admins com sumário + link /admin/ux-insights/reports/<id>/
- And flag OFF → skip silencioso
- And teste cobre fixture + schema inválido + flag OFF

FRs: FR82, FR83 · NFRs: NFR39, NFR40 · ADRs: 006, 010, Fatia 1.1.

---

### Epic 13 — Observabilidade e operação

#### Story 13.1 — structlog JSON + request_id + correlation em jobs

As a Claude Code, I want log estruturado com request_id propagado até actors Dramatiq, So that rastreio fluxo ponta-a-ponta.

AC:
- Given Story 1.5b When Story 13.1 completa Then TraceIdMiddleware injeta request_id em structlog context
- And `@idempotent_actor` aceita param `trace_id` e configura logger
- And cada log tem: timestamp, level, request_id/trace_id, module, event, extras
- And prod output JSON; dev output console colorido
- And teste valida propagação request→job

FRs: n/a · NFRs: NFR37 · ADRs: ADR-008, 010.

#### Story 13.2 — Endpoints /healthz + /readyz + /metrics (Prometheus)

As a Bruno, I want endpoints para Traefik/Portainer/Grafana consultarem, So that deploy e monitoração têm hooks.

AC:
- Given Story 13.1 When GET /healthz Then responde 200 com `{status: ok}` se processo vivo (liveness)
- And /readyz checa: DB connect, Redis ping, 1 provider IA healthy (readiness); 503 se falha
- And /metrics expõe Prometheus format via django-prometheus: http_requests, db_queries, dramatiq_jobs, ai_provider_latency
- And endpoints não exigem auth mas rate-limited
- And teste cobre 200 e 503

FRs: n/a · NFRs: NFR20, NFR22, NFR51 · ADRs: 014.

#### Story 13.3a — Grafana dashboards provisionados

As a Bruno, I want 4 dashboards prontos provisionados automaticamente, So that vejo prod sem configurar painel à mão.

AC:
- Given Story 13.2 When `deploy/grafana/dashboards/` contém JSONs Then provisioning auto-carrega: (1) Overview (req/s, p95, 5xx rate); (2) Jobs Dramatiq (fila, duração, falhas); (3) IA Providers (latência, quota, fallback events); (4) IMAP (connected, processed/h, quarentena)
- And datasource Prometheus provisionado via `deploy/grafana/datasources/`
- And versionado no repo; mudanças passam em PR
- And teste manual documentado em `deploy/grafana/README.md`

FRs: n/a · NFRs: NFR20, NFR37 · ADRs: 014.

#### Story 13.3b — Regras de alerta críticas + canal email

As a Bruno, I want alertas disparados por email quando métricas excedem limite, So that respondo antes do usuário reclamar.

AC:
- Given Story 13.3a When `deploy/grafana/alerting/` contém regras Then definidas 5 regras: 5xx>1%/5min, p95>2s/5min, fila Dramatiq>100 jobs/5min, provider IA down>10min, IMAP disconnected>5min
- And contact point email para rh_admins ativos (Slack Fatia 2)
- And notification policy com group_by por alertname + repeat_interval 1h
- And silencing manual documentado em runbook
- And teste manual (disparo sintético) documentado

FRs: n/a · NFRs: NFR21, NFR23 · ADRs: 014.

#### Story 13.4a — Backup automático Postgres + MinIO offsite

As a Bruno, I want backup diário automatizado com retenção GFS, So that tenho snapshots recuperáveis.

AC:
- Given Story 1.10 (script placeholder) When Story 13.4a completa Then `deploy/backup/backup.sh` faz pg_dump comprimido + `mc mirror` MinIO para bucket offsite (rclone crypt OU S3 outra região)
- And cron diário 02h via PM2
- And retenção GFS: 7 diários, 4 semanais, 12 mensais (rotação automática)
- And métricas emitidas: tamanho do dump, duração, sucesso/falha
- And falha dispara alerta Grafana (Story 13.3b) via exporter textfile
- And teste manual valida dump restaurável em ambiente ephemeral

FRs: n/a · NFRs: NFR21, NFR23 · ADRs: 014.

#### Story 13.4b — Teste mensal de restore + runbook DR

As a Bruno, I want restore testado automaticamente todo mês + runbook documentado, So that recovery funciona no desastre real.

AC:
- Given Story 13.4a When cron mensal (dia 1, 03h) roda Then `deploy/backup/restore_test.sh` restaura último backup em staging ephemeral, roda smoke da Story 14.4 e teardown
- And falha → alerta email rh_admin com log
- And `deploy/backup/RUNBOOK_DR.md` documenta: restore full (RTO alvo), restore point-in-time (se aplicável), contatos, checklist pós-incidente
- And resultado de cada execução logado em apps/telemetry (evento `backup.restore_test`)

FRs: n/a · NFRs: NFR21, NFR23, NFR25 · ADRs: 014.

---

### Epic 14 — Deploy em produção (Docker Swarm)

> ⚠️ **Bloqueado por 3 decisões DPO** (PRD Appendix B) antes do go-live, não antes do dev.

#### Story 14.1 — Dockerfile multi-stage + docker-compose dev

As a Bruno, I want imagem slim reprodutível + compose local para paridade, So that dev e prod usam mesma base.

AC:
- Given Epic 1 When Story 14.1 completa Then Dockerfile multi-stage: builder (uv sync --no-dev) + runtime (python:3.12-slim, non-root)
- And imagem final ≤200MB, roda whitenoise para estáticos
- And `deploy/compose/docker-compose.dev.yml` sobe: web, worker, email_ingestion, redis, postgres+pgvector, minio
- And healthchecks em cada service
- And Makefile com targets `make dev`, `make test`, `make build`
- And teste: `docker compose up` + smoke `/healthz` retorna 200

FRs: n/a · NFRs: NFR11, NFR50 · ADRs: 014.

#### Story 14.2 — Docker Swarm stack + Traefik labels + TLS Let's Encrypt

As a Bruno, I want stack prod pronta para swarm + Traefik gerencia TLS, So that deploy é 1 comando.

AC:
- Given Story 14.1 When `deploy/swarm/stack.yml` existe Then define services web (replicas=2), worker (replicas=1), email_ingestion (replicas=1, constraint single-node), redis, postgres externo
- And labels Traefik: router `Host(\`vagas.greenhousedf.com.br\`)`, certresolver letsencrypt, middleware ratelimit + compress + security-headers
- And `docker stack deploy -c stack.yml gv` funciona em nó Swarm já configurado
- And secrets via docker secret (api_keys, imap_password, field_encryption_key, db_url)
- And runbook em `deploy/swarm/README.md`

FRs: n/a · NFRs: NFR11, NFR20, NFR22 · ADRs: 014.

#### Story 14.3a — CI build + push ghcr.io + approval

As a Bruno, I want merge em main gerar imagem versionada e pausar em approval, So that controlo o que vai pra prod.

AC:
- Given Story 1.7 + 14.1 When merge em main Then `.github/workflows/deploy.yml` job `build` executa: docker build multi-stage, tag com git sha + `latest`, push para ghcr.io
- And job `approval` depende de build e exige GitHub environment=production (approval manual)
- And imagem escaneada (docker scout ou trivy) em PR; falha bloqueia merge
- And tag `latest` só atualizada após approval

FRs: n/a · NFRs: NFR51 · ADRs: 014.

#### Story 14.3b — Deploy Swarm + migrations one-shot + rollback automático

As a Bruno, I want deploy efetivo com migrations pre-deploy e rollback em falha, So that não derrubo prod por migration quebrada.

AC:
- Given Story 14.3a (approval OK) + Story 14.2 When job `deploy` dispara Then: (1) ssh no manager Swarm; (2) `docker service create --restart-condition=none` executa `manage.py migrate --check` e, se OK, `manage.py migrate`; (3) `docker service update --image <tag>` para web, worker, email_ingestion; (4) aguarda Story 14.4 smoke
- And falha no smoke → `docker service rollback` automático em cada service + alerta email
- And deploy notifica rh_admin por email (sucesso/falha) via action step
- And logs do deploy persistidos em GitHub Actions artifact

FRs: n/a · NFRs: NFR11, NFR51 · ADRs: 014.

#### Story 14.4 — Smoke test pós-deploy + verificação e2e sintética

As a Bruno, I want suite leve que roda após cada deploy, So that pego regressão antes do usuário.

AC:
- Given Story 14.3b + Story 3.3 (verify_audit_chain) + Epic 2 (link mágico) + Story 12.1 (emit_event) When deploy conclui Then `deploy/smoke/run.sh` executa: (1) GET /healthz 200; (2) GET /readyz 200; (3) login link mágico fluxo via API (conta sintética); (4) criar Requisicao rascunho; (5) `verify_audit_chain` PASS; (6) verificar /metrics exposto
- And falha em qualquer passo dispara rollback da Story 14.3b
- And resultado logado em telemetria via `emit_event('deploy.smoke', {...})` da Story 12.1
- And roda em ≤60s

FRs: n/a · NFRs: NFR20, NFR51 · ADRs: 014.

#### Story 14.5 — Go-live checklist (bloqueado por DPO, mas artefato pronto)

As a Bruno, I want checklist assinável antes de apontar DNS, So that não esqueço item crítico sob pressão.

AC:
- Given Stories 14.1-14.4 + 13.x quando Story 14.5 completa Then `deploy/GO_LIVE_CHECKLIST.md` contém: DNS apontado, TLS válido, secrets em produção ≠ dev, 3 decisões DPO registradas (PRD Appendix B), backup testado (Story 13.4), rollback testado (Story 14.3), smoke verde (Story 14.4), alertas Grafana armados (Story 13.3), primeiro tomador real briefado, contato on-call documentado
- And cada item tem checkbox + responsável + evidência
- And documentado em `deploy/README.md`
- And **status "blocked_by_dpo" até decisões B.1/B.2/B.3 registradas**

FRs: n/a · NFRs: NFR11, NFR20-23 · ADRs: 014. **Bloqueado por:** PRD Appendix B (3 decisões DPO).

---

**TOTAL FINAL: 98 stories** em 14 Epics (Lote 1: 26, Lote 2: 25, Lote 3: 23, Lote 4: 21, + 3 novas stories de gap FR: 4.7, 7.7, 11.5).

**Step 3 (Create Stories) CONCLUÍDO.**
**Step 4 (Final Validation) CONCLUÍDO** — ver `epics-validation-report.md`. Veredito: **PASS**.

Changelog completo:
- Lote 1 (pós-Amelia): 1.5→1.5a/b; 3.6→3.6a/b; AC 2.3 desambiguado; dep 3.2→2.7
- Lote 2 (pós-Amelia): 4.3→4.3a/b/c/d; 5.4→5.4a/b; 6.2→6.2a/b; AC 5.5 desambiguado (JSON mode); app `vagas` retroativo em 1.1
- Lote 3 (pós-Amelia): 7.2→7.2a/b; 7.5→7.5a/b; 8.4→8.4a/b; AC 8.4b invalidação dirigida; dep 9.1→7.3
- Lote 4 (pós-Amelia): 13.3→13.3a/b; 13.4→13.4a/b; 14.3→14.3a/b; AC 12.4 (tiktoken); Given 14.4 completo
- Gaps FR fechados: Story 4.7 (FR86 destinatários notif), Story 7.7 (FR85 whitelist remetentes), Story 11.5 (FR87 thresholds)
- Anotações FR: FR25 em 4.3c, FR27 em 4.3d, FR25+FR26 em 5.4a, FR27 em 5.4b, FR28 em 5.5, FR26+FR27 em 7.5a

**Próximo:** iniciar implementação com **Story 1.1 — Bootstrap** OU UX Spec com Sally (deferido por decisão arquitetural até Epics 1-3 codados).
