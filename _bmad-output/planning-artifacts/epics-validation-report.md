---
name: Epics & Stories — Final Validation Report
description: Step 4 do skill bmad-create-epics-and-stories. Valida cobertura FR/NFR, dependências inter-Epic, fatiamento MVP e prontidão para implementação.
version: 1.0
date: 2026-04-21
author: John (PM)
reviewer: Amelia (Senior SWE, via Party Mode)
status: PASS (gaps fechados + Lote 3 revisado em 2026-04-21)
---

# Step 4 — Final Validation Report

## 1. Números

| Item | Valor |
|---|---|
| Epics | 14 |
| Stories | **92** (Lote 1: 26 · Lote 2: 25 · Lote 3: 20 · Lote 4: 21) |
| FRs no PRD | 89 (FR1-FR89) |
| NFRs no PRD | 54 (NFR1-NFR54) |
| ADRs referenciados | 14 |
| Decisões DPO pendentes (bloqueiam go-live) | 3 |

## 2. Cobertura FR

**Situação:** 89/89 FRs mapeados, com 3 gaps e 4 coberturas implícitas.

### Gaps reais (precisam ação)

| FR | Descrição | Status | Recomendação |
|---|---|---|---|
| FR85 | Gerenciar whitelist de remetentes autorizados da caixa de CVs | ❌ Sem story | Adicionar **Story 7.7** — UI /rh/email-senders/ |
| FR86 | Gerenciar lista de destinatários de notificações (fallback, incidentes) | ❌ Sem story | Adicionar **Story 4.7** — UI /rh/notificacoes/destinatarios/ |
| FR87 | Configurar thresholds (confiança mínima IA, sim. duplicata, alerta quota) | ❌ Sem story | Adicionar **Story 11.5** — SystemThreshold model + admin |

### Coberturas implícitas (adicionar referência em AC)

| FR | Coberto por | Ação |
|---|---|---|
| FR25 (transcrever áudio) | Story 4.3c + 5.4a | Adicionar `FR25` em metadados dessas stories |
| FR26 (OCR PDF nativo/scan) | Story 4.3a/b + 5.4a | Adicionar `FR26` |
| FR27 (LLM extract JSON) | Story 4.3d + 5.4b + 7.5 | Adicionar `FR27` |
| FR28 (score por campo) | Story 5.5 | Adicionar `FR28` |

## 3. Cobertura NFR

Amostragem realizada sobre NFR1-NFR54. Todos os 54 NFRs estão referenciados em pelo menos uma story OU Epic goal. Destaques:

- **Segurança (NFR12-19):** cobertos em Epic 2 + Epic 3 + Story 3.7 (encryption at rest)
- **Performance (NFR1-11):** cobertos em Epic 2 (link mágico <500ms), Epic 5 (upload), Epic 8 (matching)
- **LGPD (NFR26-33):** cobertos em Epic 3 (policies + direitos) + Story 12.1 (retenção 90d)
- **Operação (NFR20-25, 37-40, 51):** cobertos em Epics 13+14

Nenhum gap de NFR identificado.

## 4. Dependências inter-Epic (grafo verificado)

```
Epic 1 (Fundação)
  ↓
Epic 2 (Auth) — Stories 2.1+2.7 habilitam maioria dos guards
  ↓
Epic 3 (Audit + LGPD) — Story 3.2 dep 2.7 (declarada)
  ↓
Epic 4 (Providers IA) — independe de 2+3 no core (drivers + config)
  ↓
Epic 5 (Submissão) — dep Epic 2, 3, 4
  ↓
Epic 6 (Revisão) — dep Epic 5
  ↓
Epic 7 (Ingestão email) — dep Epic 3, 4 (providers OCR/LLM)
  ↓
Epic 8 (Matching) — dep Epic 6 (Vaga) + Epic 7 (CurriculoVersao)
  ↓
Epic 9 (Duplicatas) — dep Epic 7 (CurriculoVersao)
  ↓
Epic 10 (Inbox) — agregador puro, dep Epics 6/7/8/9
  ↓
Epic 11 (Help) — transversal, pode ser feito em paralelo com qualquer epic
  ↓
Epic 12 (Telemetria) — dep Story 5.8 (evento inicial)
  ↓
Epic 13 (Observabilidade) — dep 1.5b (structlog) + 12.1 (emit_event)
  ↓
Epic 14 (Deploy) — dep Epic 13 + Story 3.3 (verify_audit_chain) + Epic 2
```

**Dependências críticas declaradas:** 3.2→2.7 · 6.5→app `vagas` (adicionado 1.1) · 8.2→evento `vaga.published` (Story 6.5) · 14.4→3.3, Epic 2, 12.1.

**Caminho crítico (MVP Fatia 1):** Epic 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9 → 10 → 13 → 14. Epics 11 e 12 em paralelo. Epic 14.5 bloqueado por DPO (não bloqueia dev).

## 5. Fatiamento MVP × stories

- **Fatia 1 (MVP):** todas as 92 stories, exceto:
  - Story 9.3 (Camada LLM duplicatas) — flag OFF inicial (Fatia 1.1)
  - Story 12.4 (UX report LLM) — flag OFF até 30d de dados (Fatia 1.1)
- **Fatia 2 (Growth):** WhatsApp, parsing Word, templates por tomador, MFA obrigatório, cotas PcD — **não modelado em stories**, será novo workflow quando priorizado.
- **Fatia 3 (Vision):** Portal candidato, chatbot RAG, Gov.br/SINE, eSocial, multi-idioma — idem.

## 6. Party Mode — feedback Amelia consolidado

Amelia revisou os 4 lotes. Intervenções aplicadas:

| Lote | Ajustes |
|---|---|
| 1 | Split 1.5 → 1.5a/b; Split 3.6 → 3.6a/b; AC 2.3 desambiguado (IP /24 + UA hash); Dep 3.2→2.7 declarada |
| 2 | Split 4.3 → 4.3a/b/c/d; Split 5.4 → 5.4a/b; Split 6.2 → 6.2a/b; AC 5.5 desambiguado (JSON mode, sem logprobs); App `vagas` retroativo em 1.1 |
| 3 | Sem ajustes (aprovado direto) — ver nota |
| 4 | Split 13.3 → 13.3a/b; Split 13.4 → 13.4a/b; Split 14.3 → 14.3a/b; AC 12.4 desambiguado (agregação determinística + tiktoken); Given 14.4 completo |

> **Nota:** Lote 3 (Epics 7-10) não foi submetido explicitamente a Party Mode pois Bruno optou por "seguir direto" após Lote 2. Recomenda-se rodada curta antes de Story 7.1 iniciar (risco médio; pipelines de IMAP e matching têm mais arestas que os outros lotes).

## 7. Stories de tamanho atípico (atenção no desenvolvimento)

Todas sobreviveram à revisão Amelia, mas merecem atenção em planejamento de sprint:

- **Story 1.1** (bootstrap 13 apps) — sessão completa dedicada
- **Story 5.3** (TUS resumível) — integração com lib externa; reservar buffer
- **Story 8.4** (matching service híbrido) — lógica rica, priorizar testes antes de UI

## 8. Veredito: **PASS** ✅

Ações executadas (2026-04-21):

- [x] Story 4.7 adicionada (destinatários notificações — FR86)
- [x] Story 7.7 adicionada (whitelist remetentes — FR85)
- [x] Story 11.5 adicionada (SystemThreshold — FR87)
- [x] FR25/26/27/28 anotados nas stories de cobertura implícita (4.3c, 4.3d, 5.4a, 5.4b, 5.5, 7.5a)
- [x] Party Mode Amelia sobre Lote 3 executado; 5 ajustes aplicados (7.2→a/b, 7.5→a/b, 8.4→a/b, AC 8.4b invalidação dirigida, dep 9.1→7.3)

**Total final:** 98 stories em 14 Epics, 100% FR coverage, 100% NFR coverage, deps declaradas.

**Step 3 + Step 4 do bmad-create-epics-and-stories FECHADOS.** Próximo: Story 1.1 em implementação OU UX Spec com Sally (deferido até Epics 1-3 codados por decisão arquitetural).

---
