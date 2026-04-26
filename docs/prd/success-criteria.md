# Success Criteria

## User Success

**Gestor Demandante:**
- Da 1ª interação à submissão da requisição em ≤ 2 minutos, sem preencher formulário tradicional de cadastro. Sensação alvo: "mais rápido que WhatsApp".
- Confirmação por e-mail/WhatsApp em ≤ 3 minutos da submissão, com resumo do que a IA entendeu.
- Requisição recorrente (mesmo posto/tomador) submetida em ≤ 30 segundos.
- ≥ 90% dos rascunhos IA aprovados pelo RH com no máximo 2 ajustes manuais.

**RH (Bruno + equipe):**
- Zero requisição perdida — 100% rastreáveis com SLA visível.
- Tempo médio de revisão de rascunho IA ≤ 5 min.
- Dashboard único: fila de revisão, vagas ativas por tomador, candidatos em matching, SLA próximo do vencimento.
- Na 2ª requisição de um posto/tomador recorrente, sistema sugere template com ≥ 80% do conteúdo.

## Business Success

**30 dias pós-lançamento:**
- Adoção ≥ 50% das requisições pelo sistema (curva S de mudança de hábito).
- ≥ 15 dos 100 tomadores com gestores ativos.
- Baseline T2F medido com ≥ 20 requisições reais.
- Baseline CSAT do tomador (1-5) estabelecido pós-preenchimento.

**60 dias:**
- Adoção ≥ 80%.

**3–6 meses:**
- T2F reduzido ≥ 25% vs baseline.
- Requisições perdidas → praticamente zero.
- ≥ 200 currículos estruturados no pool (upload RH + caixa e-mail monitorada).
- Glosa contratual evitada medida em R$/mês — % de requisições cumpridas dentro do SLA contratual ≥ 80%.
- CSAT do tomador ≥ 4,0/5,0.

**12 meses:**
- T2F reduzido ≥ 40%.
- Sistema percebido "mais rápido que WhatsApp" (pesquisa qualitativa leve).
- RH opera 2× o volume com a mesma equipe.
- Taxa de reaproveitamento do pool ≥ 30% — vagas preenchidas por CV já no pool vs. captação nova. Prova ROI do pipeline OCR/IA.

## Technical Success

- Disponibilidade ≥ 99% mensal (~7h downtime).
- Latência do pipeline multimodal (upload válido → rascunho em fila de revisão): ≤ 3 min p95 / ≤ 8 min p99.
- Latência do link mágico (geração + envio e-mail): < 10 s p95.
- Taxa de sucesso da ingestão (uploads válidos — PDF/JPG/PNG/MP3 <20MB): ≥ 95% geram rascunho completo. Falhas caem em fila de fallback visível ao RH.
- Custo LLM/OCR por vaga processada ≤ R$ 0,15 p95 (tokens OCR + Vision + extração consolidados).
- Alerta em 80% de cota por provedor OCR/Vision; troca de provedor deve ser possível em runtime, sem deploy.
- Log imutável: 100% das escritas com hash encadeado; comando de verificação de integridade disponível.
- Link mágico seguro: TTL ≤ 15 min, single-use, bound a IP/UA; zero incidentes de sequestro em 6 meses.
- Backups automatizados diários (Postgres + MinIO); RPO ≤ 24h, RTO ≤ 4h, com restore testado trimestralmente.
- Compliance checklist de go-live: ROPA preenchido, política de privacidade publicada, runbook de incidente ANPD pronto, 3 decisões DPO travadas, canal dpo@ operante.

## Measurable Outcomes

| Métrica | Baseline | Meta 30d | Meta 60d | Meta 6m | Meta 12m |
|---|---|---|---|---|---|
| % requisições via sistema | 0% | 50% | 80% | 95% | 99% |
| T2F (posto vago → preenchido) | medir | baseline firme | — | −25% | −40% |
| Tempo médio revisão RH/rascunho | — | ≤ 8 min | — | ≤ 5 min | ≤ 3 min |
| % rascunhos IA aceitos sem ajuste material | — | ≥ 70% | — | ≥ 85% | ≥ 90% |
| Requisições "perdidas" | alta | 0 reincidência | 0 | 0 | 0 |
| Currículos estruturados no pool | 0 | 50 | — | 200 | 500+ |
| Glosa contratual evitada (R$/mês) | a mapear | baseline | — | tendência ↓ | redução material |
| SLA contratual cumprido | — | — | — | ≥ 80% | ≥ 90% |
| CSAT do tomador (1-5) | — | baseline | — | ≥ 4,0 | ≥ 4,3 |
| Reaproveitamento do pool (%) | 0% | — | — | — | ≥ 30% |
| Custo LLM+OCR/vaga (R$ p95) | — | ≤ 0,20 | — | ≤ 0,15 | ≤ 0,12 |
| Uptime mensal | — | 99% | 99% | 99,5% | 99,5% |
| Incidentes segurança (link mágico, leak) | — | 0 | 0 | 0 | 0 |
