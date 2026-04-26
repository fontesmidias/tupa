# 🔀 HANDOFF — Continuação em nova janela de contexto

**Data:** 2026-04-26 (atualização 4 — pós-smoke v3, repo criado, mudança de rota)
**Motivo:** janela longa; abrir nova sessão para continuar com contexto limpo.

> **MUDANÇA DE ROTA 2026-04-26:** Bruno explicitou que estamos travados polindo prompt em corpus sintético sem rodar com PDFs reais. **Gate H1 formal abandonado.** Foco agora: usar `/lab/ia/` com PDFs reais que Bruno tem na caixa, destravar Lotes 3-4 (Epics 5-14), começar pelo Epic 5 (Vagas) como consumidor natural do AiExtractionLog. Não esperar mais a Rodada 2 do Cowork.
>
> **Repo:** github.com/fontesmidias/tupa (BSL 1.1, codinome Tupã). Commit inicial em branch `bootstrap` aguardando merge para `main`.

---

## 🧭 Prompt de retomada (copie e cole na nova sessão)

```
Retomando projeto gestao-vagas. Leia PRIMEIRO:

_bmad-output/planning-artifacts/HANDOFF.md

Depois execute imediatamente a "Opção A — smoke test em lote nos 6 PDFs sintéticos"
descrita na seção "AÇÃO IMEDIATA NA NOVA JANELA". Reporta uma tabela
comparativa de confidence/latência/custo/parsed_ok por PDF e me chama uma
revisão humana (eu) sobre os campos `requisitos` e qualquer divergência
relevante vs `_rp_data.json`.
```

---

## ⚡ AÇÃO IMEDIATA NA NOVA JANELA — OPÇÃO A

**Objetivo:** rodar smoke test em lote nos 6 PDFs sintéticos do corpus rodada 1, comparar contra ground truth, identificar divergências, e **trazer Bruno (humano) à revisão** sobre cada divergência — aprendendo com cada feedback dele para refinar o prompt v2.

**Pré-condições já satisfeitas (não refaça):**
- `.env` com `OPENAI_API_KEY` válida + `AI_LAB_ENABLED=True` + `OPENAI_MODEL_ID=gpt-4o-mini`
- Migrations 0006/0007/0008 (accounts) + 0001 (ai_providers + audit) já aplicadas no Postgres dev
- Redis + Postgres rodando
- Suíte: 350/350 verde
- Smoke test 1-PDF já rodado com sucesso (latência 12.5s, $0.00015/RP)

**Execute:**

1. **Estender `scripts/smoke_test_h1.py` para modo batch** que:
   - Lê os 6 PDFs em `_bmad-output/h1-corpus/anonimizado/`
   - Carrega `_bmad-output/h1-corpus/_rp_data.json` como ground truth
   - Para cada PDF: chama `extract_rp_from_pdf` e compara campo-a-campo (`titulo`, `tomador`, `motivo`, `requisitos`, `descricao_vaga`) com o ground truth
   - Classifica cada campo automaticamente: `match` (string-equality normalizada) / `parcial` (similaridade ≥ 0.6 via `difflib.SequenceMatcher`) / `divergente`
   - Gera tabela em `_bmad-output/h1-corpus/SMOKE_REPORT.md` com colunas: `arquivo | latência | tokens in/out | custo | confidence_LLM | match% | divergências`
   - Salva `_bmad-output/h1-corpus/smoke_results.json` (resultado bruto por RP)

2. **Após rodar**, **PARE** e apresente ao Bruno:
   - A tabela do `SMOKE_REPORT.md`
   - Uma lista numerada de cada **divergência** ou **valor parcial** (ex: "RP #03 — campo `requisitos`: ground truth tem 4 itens, LLM extraiu 0. Possível causa: prompt não instrui a extrair lista. Como você classifica: erro do prompt, erro do PDF sintético, ou comportamento aceitável?")
   - Ao final, peça: **"Bruno, classifica cada divergência como: (a) erro de prompt — ajustamos para v2, (b) limitação do sintético — ignorar até rodada 2 com originais, (c) erro do LLM — registrar como falha real."**

3. **Aprenda com o feedback dele.** Cada classificação dele entra como linha em `_bmad-output/h1-corpus/HUMAN_FEEDBACK.md` para informar o prompt v2 (`apps/ai_providers/prompts/rp_extract_v2.py` quando criado) e a próxima rodada de avaliação. Não tente decidir sozinho o que é "aceitável" — a hipótese H1 é de produto, e quem julga produto é o Bruno.

4. **Custo estimado total da Opção A:** ~$0.001 (6 chamadas × ~$0.00015). Latência total: ~75s sequencial, ~15s se rodado em paralelo (mas nem precisa — dispensa otimização nesta fase).

**Princípio importante (instrução do Bruno 2026-04-22):**
> "Sobre o que 'não prova': essas coisas que gerarem dúvidas ou algo nesse sentido envie para um humano revisar e aprenda com o feedback que ele deu."

→ **Toda divergência ambígua é input para revisão humana, não decisão autônoma do agente.** Construa o `HUMAN_FEEDBACK.md` ao longo de várias sessões; ele vira a base de conhecimento do produto.

---

## 📍 Onde paramos (estado consolidado em 2026-04-22 noite)

**Workflow BMAD:** `bmad-create-epics-and-stories` · Step 3 · Lote 1 codificado + Lote 2 (Epic 4) iniciado em forma de MVP.

**Lote 1 — todos concluídos:**
- ✅ Epic 1 (infra core): base_models, middlewares, EncryptedCharField, tasks
- ✅ Epic 2 (accounts/auth): User UUID, magic-link, MFA TOTP, cadastro progressivo, logout, scope `MagicLink.purpose`
- ✅ Epic 3 (auditoria + LGPD): 7/7 stories — AuditLog hash-chain, signals, verify_audit_chain, Políticas, self-service titular Ver/Corrigir/Exportar/Anonimizar/Revogar, EncryptedField + User.cpf

**Lote 2 — Epic 4 em modo MVP (Caminho C — síntese Party Mode):**
- ✅ `apps/ai_providers/providers/openai_llm.py` — provider ativo GPT-4o-mini (Files API + Responses API + Structured Outputs `strict=True`).
- ✅ `apps/ai_providers/providers/claude_llm.py` — preservado como base do 2º driver pós-H1 (Anthropic Sonnet 4.5).
- ✅ `apps/ai_providers/prompts/rp_extract_v1.py` — prompt PT-BR Green House + 2 few-shots, `PROMPT_VERSION` bumpável.
- ✅ `apps/ai_providers/models.py::AiExtractionLog` — FSM PENDING→RUNNING→READY/FAILED + tokens/latency/cost/confidence/result/raw + notes editável. Migration 0001.
- ✅ `apps/ai_providers/tasks.py::extract_rp_async` — `@idempotent_actor`, lê PDF de `MEDIA_ROOT/ai_lab/<uuid>.pdf`, grava envelope no log, limpa stash.
- ✅ `apps/ai_providers/views.py` — `/lab/ia/` staff-only + feature flag `AI_LAB_ENABLED`. POST upload → 202 + HTMX poll 2s.
- ✅ Settings: `OPENAI_API_KEY`, `OPENAI_MODEL_ID` (default `gpt-4o-mini`), preços `0.15/0.60` por 1M tokens. Anthropic mantido para 2º driver.
- ✅ `.gitignore`: `_bmad-output/h1-corpus/` protegido (PDFs reais nunca vão pro git).
- ✅ 25 testes em `apps/ai_providers/tests/` (10 openai_llm + 5 tasks + 10 views) — fixtures `patch_openai` (FakeOpenAI + FakeFilesAPI + FakeResponsesAPI).
- ✅ Smoke test 1-PDF executado com sucesso em 2026-04-22 (latência 12.5s, custo $0.00015/RP, schema válido).
- ✅ `scripts/smoke_test_h1.py` criado para testes em terminal sem precisar do browser.

**Suíte de testes:** **350/350 passed**.

---

## 📦 Corpus H1 — estado real

**Localização:** `_bmad-output/h1-corpus/` (no caminho correto após move manual do erro do Cowork rodada 1).

**Conteúdo:**
- `raw/` — 6 PDFs com PII real (uso interno, gitignored)
- `anonimizado/` — 6 PDFs anonimizados (`rp-01..06-AAAA-MM-DD-tomador.pdf`)
- `_rp_data.json` — **GROUND TRUTH** curado pelo Cowork (use isto na Opção A)
- `_anonymization_maps.json` — mapas nome→token por RP
- `_gen_pdfs.py` — script gerador (ReportLab) — **prova de que rodada 1 foi sintética**
- `CORPUS_REPORT.md` — relatório da rodada 1

**Ressalvas conhecidas (NÃO esquecer na nova janela):**
1. Os 6 PDFs **são sintéticos** (gerados via ReportLab a partir dos dados extraídos dos emails). Smoke test valida pipeline, **não valida hipótese de produto**.
2. Diversidade pobre: 5 INEP + 1 Golgi (deveria ter ≥3 tomadores).
3. Só PDFs digitais — zero escaneados (que é onde a extração realmente sofre).

**Solução em curso:** prompt rodada 2 do Cowork em `_bmad-output/planning-artifacts/COWORK_PROMPT_RODADA_2.md` pede 14 PDFs **originais** (Print-to-PDF do Outlook + anexos baixados sem regeneração) com diversidade de tomadores. Bruno executará em paralelo.

**Plano híbrido aprovado (C):**
1. **Smoke test em lote** com os 6 sintéticos → revisão humana das divergências (Opção A — ação imediata)
2. **2ª rodada Cowork** → 14 PDFs originais
3. **Gate H1 formal** com 20 RPs (6 sintéticos + 14 originais) — aplicar fórmula `(corretos + 0.5*parciais) / total ≥ 0.80` em ≥16 de 20 → prossegue Epic 4 completo. <0.65 → pivô.

---

## 🧠 Princípio operacional novo (instrução Bruno 2026-04-22)

> **"Sobre o que 'não prova': essas coisas que gerarem dúvidas ou algo nesse sentido envie para um humano revisar e aprenda com o feedback que ele deu."**

**Aplicação:** sempre que o agente identificar incerteza/ambiguidade (campo extraído suspeito, prompt poderia ser melhor, decisão de produto que tangencia código, etc), **interrompa a execução autônoma e peça revisão humana com pergunta específica**. Salve a resposta em `_bmad-output/h1-corpus/HUMAN_FEEDBACK.md` ou similar para informar futuras decisões.

→ Não decidir sozinho o que é "aceitável". Hipótese é de produto; quem julga produto é o Bruno.

---

## 🔧 Decisões-âncora (inalteradas)

| # | Decisão | Onde foi travada |
|---|---|---|
| Stack | Django 5.x + HTMX + Tailwind + daisyUI + Alpine.js monolítico | ADR-001 |
| Porta dev | 3005 | ADR-002 |
| Postgres | local `gestao_vagas_dev` + pgvector | ADR-003 |
| Processos | PM2 — gv-web + gv-worker + gv-email-ingestion | ADR-004 |
| Redis | Docker redis:7-alpine 6379 | ADR-005 |
| Storage | Filesystem dev, MinIO prod | ADR-006 |
| VPS | 12GB RAM / 6 vCPU (Swarm + Traefik + Portainer) | ADR-014 |
| Typing | django-stubs + mypy strict | ADR-008 |
| URLs | path kebab-PT-BR, name snake-EN | ADR-009 |
| Jobs | `@idempotent_actor` em `apps/core/tasks.py` (fila única `default`) | ADR-010/011 |
| Grafo apps | 5 camadas; **apps.audit é folha terminal** — usar `apps/core/audit_bridge.py` | ADR-012 |
| E-mail | IMAP IDLE genérico (daemon gv-email-ingestion) | ADR-013 |
| Provider IA MVP | OpenAI GPT-4o-mini hardcoded; Anthropic preservado p/ 2º driver pós-H1 | Party Mode 2026-04-21 + switch 2026-04-22 |

---

## 🎯 Padrões arquiteturais novos estabelecidos

- **Reauth com escopo isolado** via `MagicLink.Purpose` enum — replicável para outras ações críticas.
- **Digest SHA-256 truncado (16 chars)** em audit logs para campos PII (`_pii_digest` em `self_service.py`).
- **System checks de deploy** via `@register(deploy=True)` em `apps/accounts/checks.py` — bloqueiam boot se `DPO_EMAIL`/`FIELD_ENCRYPTION_KEY` ausentes.
- **Bridge pattern** para respeitar grafo de camadas: `apps/core/audit_bridge.py` (audit) + `apps/core/policy_bridge.py` (policies).
- **Provider IA com fronteira de módulo estável**: `extract_rp_from_pdf(bytes) → ExtractionEnvelope` é o contrato; trocar Claude↔OpenAI é trocar 1 import + settings (provado em 2026-04-22, zero refactor em tasks/views/models).
- **Stash de PDF em `MEDIA_ROOT/ai_lab/<uuid>.pdf`** evita passar bytes no broker Redis (Dramatiq).
- **HTMX poll de 2s** via template parcial `_job_row.html` — UX não-bloqueante para jobs IA.

---

## 🧪 Padrões de teste estabelecidos

- `@pytest.fixture` autouse para bypass do bug Python 3.14 + Django `Context.__copy__` (override `Template._render`). Ver `apps/policies/tests/conftest.py` e fixture inline em `apps/accounts/tests/test_self_service.py`.
- `DRAMATIQ_EAGER=True` em `config/settings/test.py` — actors rodam síncrono em testes (via `.fn(...)`).
- Para corromper audit em testes (e validar detecção), usar SQL raw no SQLite (UUIDs sem dashes) — manager bloqueia `update()`. Ver `apps/audit/tests/test_verify_audit_chain.py`.
- Fixtures de User completo: criar `Tomador`, passar `nome`/`tipo_gestor`/`tomador` (ver `test_self_service.py`).
- **Mock OpenAI**: `patch_openai` fixture em `apps/ai_providers/tests/conftest.py` — substitui `openai.OpenAI` por `FakeOpenAI` com `FakeFilesAPI` + `FakeResponsesAPI`. Suporta sucesso, APIError em files.create, APIError em responses.create.

---

## ❗ Pendências não-bloqueantes para dev (bloqueantes de prod)

1. 3 decisões DPO (PRD Appendix B) — base legal match IA, retenção CVs, LAI gestor servidor público.
2. Credenciais IMAP da caixa `curriculos@greenhousedf.com.br` (Epic 7).
3. API keys providers extras (Mistral, Groq, ocr.space, Claude — Anthropic key não-bloqueante para MVP atual com OpenAI).
4. Subdomínio VPS apontado (Epic 14).
5. Lista de tomadores reais.
6. **Email do DPO** — necessário para Story 3.6b (notificação de ações críticas).
7. **14 PDFs originais da Rodada 2 do Cowork** — bloqueia gate H1 formal (mas não bloqueia Opção A do smoke test em lote).

---

## 📊 Progress Tracker atualizado

- ✅ PRD v1.0 + Validation PASS 5/5 + Shard 16 arquivos
- ✅ Architecture v1.0 (14 ADRs)
- ⏳ Epics & Stories (Step 3, Lote 1 ✅, Lote 2 iniciado em modo MVP)
  - ✅ Step 1: Validate Prerequisites
  - ✅ Step 2: Design Epics (14 épicos)
  - ⏳ Step 3:
    - ✅ Epic 1 / Epic 2 / Epic 3 (Lote 1)
    - ⏳ Epic 4 em modo **Epic 4.0-MVP (Caminho C)** aguardando gate H1
  - ⬜ Step 4: Final Validation
- ⬜ Lotes 3-4 (Epics 5-14) — bloqueados pelo gate H1
- ⬜ UX Spec (Sally) — após gate H1 + Epic 4 completo
- ⬜ Deploy em produção (gate `GO_LIVE_GATE.md`)

---

## 📂 Arquivos-fonte (ordem de leitura na nova sessão)

1. **Este arquivo** (`HANDOFF.md`) — estado atual.
2. **`_bmad-output/planning-artifacts/COWORK_PROMPT_RODADA_2.md`** — prompt para Bruno executar no Cowork em paralelo.
3. **`_bmad-output/h1-corpus/CORPUS_REPORT.md`** — relatório da rodada 1 (sintético).
4. **`_bmad-output/h1-corpus/_rp_data.json`** — ground truth para comparar com extração LLM.
5. **`scripts/smoke_test_h1.py`** — base do smoke test (precisa estender para batch).
6. **`apps/ai_providers/providers/openai_llm.py`** — provider ativo, contrato `extract_rp_from_pdf`.
7. **`apps/ai_providers/prompts/rp_extract_v1.py`** — prompt atual (pode precisar v2 após feedback humano).

---

## 🧠 Memória persistente

Em `C:\Users\cery0\.claude\projects\c--Users-cery0-projetos-gestao-vagas\memory\`:
- `MEMORY.md` — índice
- `user_profile.md`, `project_gestao_vagas.md`, `session_handoff_2026_04_21.md`

**Ao iniciar nova sessão**, consulte memória + leia este HANDOFF + execute Opção A.

---

## ✅ Checklist da nova sessão

Na nova janela, em ordem:

1. Ler este HANDOFF.md por inteiro.
2. Confirmar que `350/350 passed` ainda é verdade: `.venv/Scripts/python.exe -m pytest`
3. Executar Opção A — estender `scripts/smoke_test_h1.py` para batch + ground truth comparison + gerar `SMOKE_REPORT.md` + `smoke_results.json`.
4. **PARAR** e apresentar tabela + lista de divergências ao Bruno com perguntas específicas para classificação humana.
5. Salvar respostas em `_bmad-output/h1-corpus/HUMAN_FEEDBACK.md`.
6. Aguardar instrução do Bruno sobre próximo passo (prompt v2? esperar Rodada 2 do Cowork? algum ajuste do código?).

---

**Fim do HANDOFF.** Custo da Opção A: ~$0.001. Latência total: ~75s. Tempo de revisão humana esperado: 10-15 min.
