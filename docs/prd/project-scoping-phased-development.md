# Project Scoping & Phased Development

## Resumo de Fatias (Scanning rápido)

| Fatia | Objetivo | FRs incluídos | NFRs críticos | Critério de saída |
|---|---|---|---|---|
| **1 (MVP)** | Validar hipótese central: ingestão informal + IA + revisão RH reduz requisições perdidas e melhora T2F | FR1–FR78, FR79–FR83 (captura), FR84–FR89 (core) | NFR1–NFR10 (latência/escala), NFR11–NFR19 (segurança), NFR20–NFR25 (confiabilidade), NFR26–NFR33 (LGPD baseline), NFR34–NFR40 (custo+obs), NFR41–NFR54 | ≥5 tomadores ativos; ≥50% reqs pelo sistema em 30d; pipeline IA estável; compliance checklist completo |
| **1.1 (Follow-up)** | Amadurecer MVP com aprendizado dos primeiros usuários | FR34 (ambiguidade split), FR51 (templates formais), FR81 (job LLM ativo), FR37 (Camada 3 duplicata), FR73 cobertura periférica | Mesmos do MVP (sem regressão) | Saída: telemetria com ≥30d, todos tooltips, LLM de insights operante |
| **2 (Growth)** | WhatsApp + Word nativo + analytics + providers extras | FR relacionados a canais/providers adicionais | NFR de antivírus, MFA obrigatório, disparate impact | Adoção ≥80%, redução T2F comprovada ≥25% |
| **3 (Vision)** | Portal candidato, suporte IA, Gov.br/SINE, eSocial, multi-idioma, i18n AA | Novos FR a derivar | Novos NFR de acessibilidade e interop | Quando o produto ultrapassar uso interno |

Detalhes de cada fatia estão nas subseções abaixo.

## MVP Strategy & Philosophy

**Abordagem MVP:** Problem-solving MVP com arquitetura defensável.

- Resolver a dor real: requisições perdidas e T2F alto.
- Arquitetura correta desde o dia 1 em tudo que é caro de refazer (auth, log append-only, providers plugáveis, schema de dados, privacy-by-design, telemetria).
- Polimento/coverage reduzidos no que é barato iterar depois (nº de providers concretos, polish visual do painel, features secundárias do help).

**Resource Requirements:** 1 engenheiro (Bruno) em ritmo solo; ideal ter um revisor externo ocasional para PR review crítico; apoio jurídico/DPO pontual.

## MVP Feature Set (Fatia 1) — Objetivo: em produção interna com ≥5 tomadores ativos

### Core User Journeys Suportadas

- **J1** (Gestor servidor público submete via áudio) — completa
- **J2** (Edge case / ambiguidade) — simplificada: mostra apenas campos de baixa confiança amarelos; sem split de "2 vagas em 1 áudio" (vai para Fatia 1.1 se acontecer muito)
- **J3** (RH revisa) — completa com kanban + diff visual + reaproveitamento de template
- **J4** (Ingestão currículo por e-mail) — completa, mas com 1 só provedor de e-mail suportado (o que a Green House usar)
- **J5** (Troca de provider OCR) — UI operante, 2 providers concretos por categoria (Mistral + ocr.space; Groq + OpenAI; Groq + Claude). Demais providers em Growth.

### Must-Have Capabilities (Fatia 1)

| Bloco | Status na Fatia 1 | Observação |
|---|---|---|
| Auth link mágico + cadastro progressivo | Completo | IP/UA bind, TTL, single-use |
| Portal gestor submissão multimodal | Completo | Mobile-first, HTMX |
| Pipeline IA (Whisper/Groq + pdfplumber + Mistral Vision + Claude/Groq extraction) | Completo | 2 providers por categoria |
| Dashboard providers + cotas + troca runtime | Completo | Contador local |
| Notificação automática em fallback | Completo | E-mail ao admin |
| Painel RH kanban + revisão diff visual + baixa confiança | Completo | UI dedicada (não Admin puro) |
| Reaproveitamento de template por tomador/posto | Simplificado | "Este é similar a X — copiar?"; templates formalizados Fatia 2 |
| Ingestão e-mail encaminhado | Completo | 1 provedor concreto |
| Match vaga × candidato | Completo | Regras + embeddings; explicabilidade básica |
| Detecção de duplicata (3 camadas) | **Parcial (feature flag)** | Camadas 1 e 2 completas; Camada 3 (LLM) ligável após afinar prompt |
| Log append-only hash-encadeado + CLI verificação | Completo | LGPD/LAI baseline |
| Policy changelog estilo Nubank | Completo | Modal + summary_of_changes |
| Consentimento granular + direitos do titular | Completo | Endpoint/página |
| Telemetria UX captura | Completo | Middleware + tabela particionada |
| Job LLM semanal insights UX | **Ligável por flag** | Infra pronta; ativa após 30 dias de eventos |
| Dashboard /admin/ux-insights | Completo | Mesmo com poucos dados |
| Help contextual universal | **Essential coverage** | Campos críticos 100%; periféricos Fatia 1.1 |
| Breadcrumbs + empty states educativos | Completo | Barato |
| Notificações SMTP (gestor + RH) | Completo | Transacionais + alertas |
| Compliance checklist go-live (ROPA, runbook, restore test) | Completo | Bloqueante p/ produção |

**Estimativa refinada Fatia 1:** ~30–38 dias úteis solo. Ainda ~6–8 semanas.

## Fatia 1.1 (Quick follow-up, ~1 semana após Fatia 1)

- Completar help contextual em telas periféricas
- Split de "2 vagas em 1 áudio" (se acontecer em campo)
- Formalização de templates por tomador/posto (hoje é "copiar similar" → biblioteca editável)
- Ativação do job LLM de insights UX (se houver volume)
- Ativação da Camada 3 do duplicate detection (LLM raciocinador)

## Fatia 2 — Growth (Post-MVP)

- WhatsApp via Evolution API (notificações bidirecionais)
- Parsing de Word nativo (hoje: converte para PDF)
- Templates formalizados avançados por tomador (versioning, duplicação)
- Relatório de SLA contratual por tomador (conecta a glosa evitada)
- Dashboard analítico do gestor
- Monitoramento de cotas PcD (Lei 8.213/91 Art. 93)
- Métricas de disparate impact no match
- Providers adicionais (Claude Vision, GPT-4o, Google Vision, Tesseract local, AssemblyAI, Ollama)
- Segundo provedor de e-mail suportado
- Antivírus ClamAV no pipeline
- MFA TOTP para RH
- CSAT rápido pós-aprovação (1-5)
- Pesquisa qualitativa automatizada

## Fatia 3 — Vision (Future)

- Portal do candidato self-service
- Suporte IA estilo Claude (chatbot RAG sobre help_snippets + eventos + wiki)
- Integração Gov.br / SINE / Secretaria DIP
- Export estruturado eSocial S-2200
- Compliance automatizado (revisão anual, renovação, purga)
- Multi-idioma / acessibilidade AA
- Integração bidirecional com ATS de mercado (Gupy/Solides)
- IA que monta "Formulário DIP" automaticamente a partir da vaga

## Risk Mitigation Strategy

**Riscos Técnicos:**
- Maior risco: pipeline multimodal com LLM pode alucinar. Mitigação: revisão RH obrigatória + campos de baixa confiança + telemetria de aprovação/ajuste para ajustar prompt.
- Feature flag no pipeline inteiro: se algo quebra, degrada graciosamente para "RH preenche manualmente".
- Camada 3 de duplicata e job LLM de UX atrás de flags — ativam quando houver dados suficientes.

**Riscos de Mercado (adoção interna):**
- Maior risco: gestor continua preferindo WhatsApp. Mitigação: onboarding 1:1 com os 10 principais tomadores; vídeo de 30s; medida H6 em 60 dias; se falhar, bot WhatsApp Fatia 2.
- Adoção reescalonada (50%/30d → 80%/60d) incorpora curva S realista.

**Riscos de Recurso:**
- Cenário "menos tempo":
  1. **Inegociável:** auth + portal submissão + pipeline IA + revisão RH + log append-only + compliance baseline.
  2. **Adia para Fatia 1.1:** help contextual completo, job LLM UX, Camada 3 duplicata, reaproveitamento formal.
  3. **Corta até Fatia 2 se necessário:** segunda opção de provedor em cada categoria, ingestão por e-mail completa.
- Contingência: se ficar sem banda >2 semanas, desativar providers que gerem custo e manter sistema em modo "somente estrutura".
