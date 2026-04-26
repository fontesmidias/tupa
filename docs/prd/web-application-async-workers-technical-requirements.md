# Web Application + Async Workers — Technical Requirements

## Project-Type Overview

Sistema web server-rendered predominantemente (Django templates + HTMX para interações dinâmicas, sem SPA full) com 3 superfícies:

1. Portal do Gestor (público autenticado por link mágico) — mobile-first, focado em submissão de requisição.
2. Painel do RH (admin) — UI dedicada em Django templates (ou Django Admin customizado com django-unfold para visual moderno), com kanban de requisições, revisão de rascunhos IA, configuração de providers.
3. Serviço de ingestão de e-mail (worker/daemon separado) — monitora caixa `curriculos@greenhousedf.com.br` por IMAP IDLE ou webhook; emite jobs para fila.

Tudo orquestrado como serviços Docker em Docker Swarm com Traefik expondo apenas o portal via subdomínio da Green House.

## Technical Architecture Considerations

Stack consolidada (hipótese travada para Arquitetura validar):

| Camada | Tecnologia | Justificativa |
|---|---|---|
| Web framework | Django 5.x + HTMX | Admin pronto, auth/ORM/migrations/CSRF nativos; HTMX elimina SPA evitando 80% da complexidade frontend |
| UI helpers | Tailwind CSS + django-tailwind | Mobile-first, consistência visual |
| Auth | Django auth customizado + link mágico próprio | TTL ≤15min, single-use, bound IP/UA; tabela `magic_link` |
| DB | PostgreSQL 16 + pgvector | Transacional, JSONB, embeddings, maduro |
| Cache / broker | Redis 7 | Sessão, Dramatiq broker, pub/sub interno |
| Fila de jobs | Dramatiq | Retries, código limpo, middleware claro |
| Object storage | MinIO (S3-compatible) | Binários originais |
| Observabilidade | Loki + Grafana + Prometheus | Boring tech self-hosted |
| Secrets | django-cryptography / django-fernet-fields + chave mestra em env | Campos sensíveis em repouso |
| Deploy | Docker Swarm + Traefik + Portainer | Sem K8s, sem overkill |
| Dev local | Docker Compose | Paridade com produção |
| CI/CD | GitHub Actions + registry | Build + test + deploy para Swarm |
| Feature flags | django-waffle ou flag em tabela | Rollout controlado do pipeline IA |

## Functional Architecture — Componentes principais

```
┌─────────────┐        ┌───────────────┐        ┌─────────────────┐
│  Portal     │        │  Painel RH    │        │ Email Ingestion │
│  (gestor)   │        │  (admin)      │        │  Worker         │
│  Django +   │        │  Django +     │        │  (IMAP IDLE /   │
│  HTMX       │        │  HTMX         │        │   webhook)      │
└──────┬──────┘        └───────┬───────┘        └────────┬────────┘
       │                       │                         │
       └───────────────────────┴─────────────────────────┘
                               │
                   ┌───────────┴────────────┐
                   │                        │
              ┌────┴─────┐            ┌─────┴─────┐
              │ Postgres │            │  Redis    │
              │ +pgvector│            │ (broker + │
              │          │            │  cache)   │
              └────┬─────┘            └─────┬─────┘
                   │                        │
                   └────────┬───────────────┘
                            │
                   ┌────────┴─────────┐
                   │ Dramatiq Workers │
                   │ (N processos)    │
                   └────────┬─────────┘
                            │
       ┌────────────────────┼──────────────────────────┐
       │                    │                          │
  ┌────┴─────┐         ┌────┴─────┐             ┌──────┴──────┐
  │ AI       │         │ MinIO    │             │ SMTP /      │
  │ Providers│         │ (bins)   │             │ Evolution   │
  │ (OCR/Vis │         │          │             │ Growth      │
  │ Audio/   │         └──────────┘             └─────────────┘
  │ LLM)     │
  └──────────┘
```

## Authentication & Authorization Model

Autenticação:
- Link mágico default (gestores e RH).
- MFA (TOTP) opcional para contas administrativas.
- Sessão Django com cookie HttpOnly, Secure, SameSite=Lax; rotação em mudança de privilégio.

Autorização (pool único com visibilidade por círculo):
- Perfis: `rh_admin`, `rh_operator`, `gestor`, `system`.
- Atributo derivado `tipo_gestor` (A/B/C) define trilha de auditoria (B ativa LAI).
- Tabela `circulo(tomador_id, departamento, coordenacao)` agrupa gestores.
- Queryset mixin no Django filtra automaticamente por círculo para `gestor`.

## API Surface (mínima)

Sistema server-rendered — sem API pública no MVP:
- `/webhooks/email-inbound` — webhook do provedor de e-mail quando chega mensagem na caixa monitorada. Alternativa IMAP IDLE é worker daemon sem endpoint.
- `/webhooks/whatsapp` (Growth) — callbacks Evolution API.
- `/api/internal/*` — endpoints autenticados por sessão para chamadas HTMX.

DRF entra apenas se houver API externa em Growth/Vision.

## Data Model — Entidades principais (MVP)

- `usuario` (extends Django User) — + tipo_gestor, tomador_id, telefone, circulo_id
- `tomador` — cliente Green House (órgão público, privado, conta Green House)
- `requisicao` — content_hash, fingerprint_estruturado, embedding, parent_id, duplicata_status, sla_contratual, prazo_estimado, tipo_gestor_criador
- `input_artefato` — inputs originais (audio/pdf/word/imagem/texto); tipo, path MinIO, hash, mime-real, size
- `rascunho_extracao` — saída IA (JSON, score de confiança por campo, provider usado, tokens, tempo)
- `vaga` — após aprovação, requisição vira vaga ativa
- `candidato` — cpf_hash, email, telefone, nome, dedup-key múltipla
- `curriculo` — binário + extração; candidato_id, origem (upload-rh, email-monitorado)
- `match_vaga_candidato` — score, explicabilidade, decisão RH
- `ai_provider_config` — providers plugáveis (kind, name, is_active, is_fallback, encrypted_api_key, quota_resets_on)
- `ai_usage` — contador local (provider, date, count, tokens_in, tokens_out, bytes)
- `audit_log` — append-only hash-encadeado (action, entity, before, after, user, ip, ua, hash_prev, hash_atual)
- `policy_version` / `policy_acceptance` — changelog de políticas
- `help_snippet` — tooltips editáveis pelo RH
- `ux_event` — telemetria (particionado por semana)
- `ux_report` — relatórios semanais LLM
- `magic_link` — tokens de auth

## Implementation Considerations

Filas e workers:
- 3 filas lógicas por prioridade: `urgent`, `default`, `background`.
- Dead letter queue para jobs com falhas recorrentes — notificação ao RH.

Idempotência:
- Jobs de ingestão idempotentes (hash como chave). Reprocessar é seguro.
- Webhooks de e-mail deduplicados por Message-Id.

Observabilidade mínima:
- Logs estruturados (JSON) com trace_id correlacionando request → job → providers.
- Métricas: latência por etapa, falha por provider, tokens consumidos, tamanho da fila.
- Alertas: fila >20 jobs por >5min, erro de provider >3× em 10min, uptime <99% diário.

Testes:
- Unit tests para cada provider driver (mocks).
- Integration tests para pipeline completo (upload → extração → rascunho).
- Smoke tests em CI com fixtures.

Deployment:
- `docker-compose.stack.yml` único com services: web, worker, email-ingestion, db, redis, minio, traefik, loki, grafana.
- Migrations em job pre-deploy.
- Rolling update (zero-downtime) via Swarm.
- Backup cronjob no host: pg_dump + mc mirror do MinIO para storage externo (Wasabi/Backblaze).

## Estimativa de esforço (Fatia 1 — MVP, solo)

| Bloco | Esforço |
|---|---|
| Setup infra (Swarm stack, Traefik, Postgres, Redis, MinIO, CI/CD) | 2–3 dias |
| Auth link mágico + cadastro progressivo + perfis | 3–4 dias |
| Portal do gestor (mobile-first, submissão multimodal, HTMX) | 4–6 dias |
| Pipeline IA (providers plugáveis, extração, fila, retry, dashboard cotas) | 6–8 dias |
| Painel RH (kanban, revisão, diff visual, reaproveitamento de template) | 5–7 dias |
| Ingestão de e-mail (webhook/IMAP, dedup, anti-loop, matching) | 4–5 dias |
| Detecção de duplicatas (3 camadas) | 3–4 dias |
| Log append-only + policy changelog + direitos do titular LGPD | 3 dias |
| Telemetria UX + job LLM + dashboard de insights | 3–5 dias |
| Help contextual + breadcrumbs + empty states | 2–3 dias |
| Notificações e-mail SMTP + fallback alerts | 2 dias |
| Compliance checklist go-live (ROPA, runbook, restore teste) | 2–3 dias |
| **Total estimado** | **~40–55 dias úteis (solo)** |

Estimativa honesta indica Fatia 1 real em ~2 meses solo. A negociação de escopo fina entra no Step 8 (Scoping).
