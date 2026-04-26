---
stepsCompleted:
  - step-01-init
  - step-02-discovery
  - step-02b-vision
  - step-02c-executive-summary
  - step-03-success
  - step-04-journeys
  - step-05-domain
  - step-06-innovation
  - step-07-project-type
  - step-08-scoping
  - step-09-functional
  - step-10-nonfunctional
  - step-11-polish
  - step-12-complete
workflowStatus: complete
completedAt: 2026-04-21
vision:
  problem: 'Informalidade na entrada da requisição de pessoal quebra o SLA contratual de reposição da Green House — sintoma é "requisição perdida no WhatsApp", dor real é faturamento em risco, possível glosa/multa e retrabalho do RH.'
  productStatement: 'Transformar toda requisição de pessoal (áudio/print/PDF/Word/verbal transcrita) em registro estruturado, auditável e imediatamente acionável, onde a IA faz o trabalho chato e o humano faz o trabalho caro.'
  differentiators:
    - 'Ingestão multimodal onde o usuário já está — aceita áudio bagunçado, print ruim, PDF feio; gestor redireciona, não muda de canal'
    - 'IA propõe, humano decide — assistente ao RH, não substituto; revisão humana é feature nativa (LGPD Art. 20)'
    - 'Memória institucional por tomador — templates de posto, peculiaridades recorrentes, talent pool aprendem a cada ciclo'
    - 'Compliance nativo — log hash-encadeado, consentimento granular, trilha LAI condicional por tipo de gestor'
    - 'Contexto B2G — entende Termo de Referência, CCT, pisos salariais, peculiaridades do gestor público'
  coreInsight: 'LLMs multimodais em 2026 são confiáveis o suficiente para extração estruturada de áudio+PDF+imagem com JSON schema; combinado com revisão humana rápida, o erro residual é tolerável. Há 3 anos era pesquisa; hoje é commodity.'
  buildVsBuyRationale: 'Nenhum ATS do mercado (Gupy/Kenoby/Solides) aceita áudio bagunçado do gestor como entrada, nem entende o contexto B2G (Termo de Referência, peculiaridades do gestor público, CCT Asseio). Construir custa menos que customizar.'
  valueStatement: 'Receba, organize e preencha vagas mais rápido: o gestor fala (como preferir), a IA estrutura, o RH valida, a Green House cumpre SLA.'
  primaryMetrics:
    - 'T2F — Tempo médio do posto vago até preenchido (baseline a medir no MVP)'
    - 'Requisições perdidas → zero (canal único estruturado substitui WhatsApp/telefonema/verbal)'
  gestorProfileTypes:
    - 'A — Funcionário Green House operando conta do cliente'
    - 'B — Servidor público do órgão cliente (ativa trilha LAI + TCU/CGU)'
    - 'C — Funcionário de empresa privada cliente'
  volumeEstimates:
    requisicoesPorMes: 20
    vagasAtivasMedia: 10
    tomadoresCadastrados: 100
    implicacao: 'Volume baixo → foco em confiabilidade e UX, não throughput. Postgres+Redis single-node + 1 VPS suportam 10× esse volume. Justifica Django (velocidade > performance).'
  cadastroStrategy:
    approach: 'Valor primeiro, identidade depois — jornada invertida'
    layers:
      - 'Camada 1 — Gestor vai direto para "Nova requisição" ao clicar no link mágico; cadastro só após submeter (quando já recebeu valor)'
      - 'Camada 2 — Pré-preenchimento por IA usando domínio do e-mail (.gov.br → servidor), assinatura do e-mail encaminhado, base de tomadores já cadastrados; gestor valida com 1 clique'
      - 'Camada 3 — Onboarding por convite iniciado pelo RH quando o gestor é recorrente/conhecido'
      - 'Camada 4 — Cadastro progressivo: campos secundários só aparecem quando necessários, nunca formulário longo'
    derivedAttribute: 'tipo_gestor derivado automaticamente do domínio do e-mail — .gov.br → servidor público → habilita exports LAI'
classification:
  projectType: 'Web Application interna (portal gestor + painel RH) + workers assíncronos + serviço de ingestão de e-mail'
  domain: 'Staffing/Body Shop B2G (HR Tech + Public Procurement)'
  complexity: 'Alta'
  projectContext: 'greenfield'
  complianceRequirements:
    - 'LGPD (Lei 13.709/18) — Arts. 7, 11, 20'
    - 'Marco Civil Internet (Lei 12.965/14) Art. 15'
    - 'Lei 8.213/91 (Cotas PcD)'
    - 'Lei 12.527/11 (LAI) quando gestor for servidor público'
    - 'ANPD Res. CD/ANPD 15/2024 (incidentes)'
    - 'CCT Asseio e Conservação (SEAC-DF) — a confirmar aplicabilidade'
    - 'Lei 13.467/17 + eSocial (interface, Fase 2)'
  primaryUsers:
    - 'Gestor demandante (casual, pode ser servidor público OU Green House — a confirmar)'
    - 'RH Green House (Bruno, Coord. de RH)'
  nonFunctionalKeys:
    - 'SLA contratual de preenchimento (a mapear nos contratos vigentes)'
    - 'Auditoria imutável (hash-chain + IP + timestamp)'
    - 'Link mágico com TTL ≤15min, single-use'
    - 'Revisão humana obrigatória (LGPD Art. 20)'
inputDocuments:
  - path: 'C:\Users\cery0\Downloads\Formulário de Vagas.pdf'
    type: 'reference-form'
    summary: 'Formulário manual (Word→PDF) usado hoje pela Green House para enviar dados de vaga à Secretaria da Pessoa com Deficiência do DF. Referência de campos estruturais.'
  - path: 'C:\Users\cery0\.claude\plans\neste-projeto-tenho-instalado-floofy-unicorn.md'
    type: 'session-plan'
    summary: 'Plano desta sessão (2026-04-20) com decisões D1-D6, fatiamento de MVP em 4 fatias, stack hipótese e riscos R1-R5.'
documentCounts:
  briefs: 0
  research: 0
  brainstorming: 0
  projectDocs: 0
  referenceForms: 1
  sessionPlans: 1
openNotes:
  - 'Bruno (2026-04-20): infra de dados mínima obrigatória — PostgreSQL eficiente + Redis (ou equivalente para cache/filas). Confirmar no Step 2/Arquitetura: pgvector para matching futuro, Redis para sessões de link mágico + fila de jobs de IA (transcrição de áudio, parsing de PDF, OCR). Considerar Celery/RQ/Dramatiq.'
  - 'Bruno (2026-04-20) — VISIBILIDADE: NÃO é multi-tenant. Pool único. RH vê tudo. Gestor enxerga apenas as vagas que ele demandou + vagas do seu "círculo" (colegas do mesmo órgão/departamento/coordenação). Círculo derivado do cadastro no 1º acesso (link mágico), ajustável manualmente pelo RH.'
  - 'Bruno (2026-04-20) — CURRÍCULOS v1 (MVP): RH faz upload manual; sistema extrai dados por IA/algoritmo e faz match com vagas abertas. Decidir custo-benefício IA vs algoritmo (hipótese John: híbrido — regras rígidas para obrigatórios + embeddings nos desejáveis/diferenciais). V2: portal do candidato.'
  - 'Bruno (2026-04-20) — CURRÍCULOS POR E-MAIL ENCAMINHADO (MVP, NÃO futuro): caixa monitorada recebe e-mails encaminhados pelo RH com currículos anexados. Sistema extrai anexos (PDF/Word), lê corpo via IA, grava registro estruturado + salva binário original, disponibiliza para matching. Reusa a mesma stack multimodal. Pendências: (a) provedor de e-mail da Green House (Google Workspace/M365/outro) define IMAP IDLE vs webhook; (b) anti-loop por Message-Id + hash; (c) whitelist de remetentes ou quarentena; (d) deduplicação por CPF → e-mail+telefone → nome+telefone.'
  - 'Bruno (2026-04-20) — FILOSOFIA: prefere investir energia no planejamento agora do que retrabalhar no código depois. Manter complexidade ALTA confirmada; planejamento rigoroso é valor, não overhead.'
  - 'Party Mode Round 1 (2026-04-20) — Mary (Analyst) reenquadrou domínio como Staffing/Body Shop B2G (não HR Tech genérico); SLA contratual vira requisito não-funcional duro; clarificar se gestor demandante é servidor público ou Green House; mapa regulatório expandido por Paige (ver partyModeArtifacts.regulatoryMap).'
  - 'Party Mode Round 1 (2026-04-20) — Winston (Architect) recomenda Django (não FastAPI) por Admin embutido + maturidade do ecossistema; Dramatiq (não Celery) para fila; webhook (Google Workspace Pub/Sub ou M365 Graph) em vez de IMAP IDLE; Swarm OK em 2026; stack faltando: Loki+Grafana (obs), backup Postgres+MinIO, secrets (Doppler/SOPS), feature flags.'
  - 'Party Mode Round 1 (2026-04-20) — Sally (UX) — 3 alertas: (1) link mágico + cadastro longo no 1º acesso é fricção letal para usuário casual; dividir cadastro progressivo; (2) trocar "círculo" por "minhas vagas" + "vagas da minha área"; (3) projetar para caso real (1 áudio bagunçado), não ideal (multimodal combinado); (4) Django Admin para RH vira dívida rápido — planejar UI dedicada do RH já na Fatia 1 ou Fatia 2; (5) revisão IA precisa de diff visual, não JSON.'
  - 'Party Mode Round 1 (2026-04-20) — Paige (Tech Writer) entregou mapa regulatório completo (ver partyModeArtifacts.regulatoryMap). Destaque: LGPD Art. 20 (revisão humana obrigatória em decisão automatizada) justifica legalmente a D3 "RH sempre revisa". Três decisões DPO obrigatórias antes de produção: base legal do match IA, prazo de retenção de currículos, enquadramento LAI de gestor servidor público.'
  - 'Bruno (2026-04-21) — OCR/VISION PROVIDER PLUGÁVEL (MVP): abstração OcrProvider com drivers iniciais ocr.space (OCR puro, free com limites) e Mistral (AI vision, free com limites). UI do RH permite trocar provedor ativo e atualizar API key por provedor. Dashboard visível de cota total/consumido/restante/data de renovação (quando API expuser). Preferência de Bruno = Mistral como default; ocr.space como fallback/alternativa. Abrir caminho para Claude vision / GPT-4o vision / Google Vision / Tesseract local em Growth.'
  - 'Bruno (2026-04-21) — IA LENDO LOGS DE UX PROMOVIDA PARA MVP (era Vision): telemetria estruturada de eventos (clicks, tempo em tela, abandono, erros, trilhas de submissão) desde o dia 1. Job agendado (ex: semanal) alimenta LLM com amostragem dos logs e produz relatório "oportunidades de melhoria" sem depender de formulários de feedback do usuário. Requisito #19 original do Bruno, que deveria ter ficado no MVP desde o início.'
  - 'Bruno (2026-04-21) — Decisão contra recomendação Mary+Winston: IA-lê-logs COMPLETA (captura + job LLM + dashboard) fica no MVP. Razão: aposta de capacidade, não de demanda atual — se volume surpreender pra cima, telemetria+análise já estará pronta. Custo LLM estimado ~R$ 0,20/mês (Winston). Impacto: +3-5 dias na Fatia 1 (Winston). Aceitar relatórios iniciais com sinal fraco até acumular volume.'
  - 'Bruno (2026-04-21) — Adoção reescalonada aceitando pushback Mary: ≥50% das requisições pelo sistema em 30d, ≥80% em 60d (era 80% em 30d — agressivo contra hábito de WhatsApp).'
  - 'Mary Round 2 (2026-04-21) — 3 métricas vitais B2G adicionadas: (1) Glosa contratual evitada (R$/mês) — reqs dentro do SLA contratual / total; conecta produto a P&L. (2) Taxa de reaproveitamento do pool — % vagas preenchidas com CV já estruturado vs. captação nova. (3) CSAT do tomador (1-5) pós-preenchimento — base pequena (100 tomadores) torna NPS impraticável.'
  - 'Winston Round 2 (2026-04-21) — Metas técnicas apertadas: rascunho ≤3min p95 / ≤8min p99 (era ≤5min); custo LLM ≤R$0,15/vaga processada p95 (novo KPI); alerta em 80% de cota por provedor; latência link mágico <10s p95; restore test trimestral obrigatório (senão RTO 4h é fantasia). Denominador de uploads: apenas "válidos" (PDF/JPG/PNG/MP3 <20MB).'
  - 'Winston Round 2 (2026-04-21) — Arquitetura OcrProvider: Protocol Python com extract/health/quota; drivers MistralProvider + OcrSpaceProvider; registry em apps/ocr; tabela ocr_provider_config com API key criptografada (django-fernet-fields ou django-cryptography, chave mestra OCR_SECRETS_KEY em env). Cotas: nem ocr.space nem Mistral expõem endpoint de cota → contador local ocr_usage(provider, date, count, bytes) no worker; data de reset configurável manualmente (quota_resets_on); ler headers x-ratelimit-* quando presentes.'
  - 'Winston Round 2 (2026-04-21) — Pipeline telemetria UX: tabela particionada por semana ux_events_YYYY_WW (Postgres, não ClickHouse — boring tech); evento captura user_id_hash (salt), session_id, route, action, duration_ms, error_code, ts — sem PII direto; job Dramatiq semanal (seg 6h) amostra 200-500 eventos → prompt Mistral → relatório markdown em ux_reports; UI /admin/ux-insights.'
  - 'Bruno (2026-04-21) — DETECÇÃO DE REQUISIÇÕES DUPLICADAS/CORRELATAS (MVP): múltiplos gestores do mesmo tomador frequentemente pedem a mesma vaga por canais separados. Sistema detecta automaticamente em 3 camadas: (1) determinística — hash do anexo, Message-Id/In-Reply-To, fingerprint (tomador_id, posto_normalizado, cidade, data); (2) semântica — embedding do texto extraído em pgvector, busca vizinhos ≥0,85 coseno no mesmo tomador em 30 dias abertas/recentes; (3) LLM raciocina sobre candidatos e retorna veredito com score e motivo. RH decide no painel: mesclar (parent_id), relacionar como irmãs, descartar como diferentes, ou notificar gestores. Campos em requisicao: content_hash, fingerprint_estruturado, embedding vector(768), parent_id, duplicata_status enum. Job Dramatiq check_duplicates pós-extração. Custo LLM estimado <R$2/mês no volume atual. Thresholds configuráveis por tomador. Auditoria de fusão/relação preserva histórico. Importante: distinguir substituição (mesmo posto, reposição de X) vs ampliação (mesmo posto, novo quadro) — não são duplicata.'
  - 'Bruno (2026-04-21) — CHANGELOG DE POLÍTICAS estilo Nubank (MVP): ao logar, se Termos de Uso ou Política de Privacidade mudaram desde o último aceite, modal exibe RESUMO EM TÓPICOS do que mudou (diff humanizado escrito pelo RH ao versionar) + link para documento completo. Tabela policy_acceptance(user_id, policy_version_id, summary_shown, accepted_at, ip, ua). Imutável. Atende LGPD (transparência e novo consentimento) com UX que o usuário realmente lê.'
  - 'Bruno (2026-04-21) — PROVIDERS PLUGÁVEIS UNIVERSAIS (MVP): estender abstração OcrProvider para TODAS as categorias de IA externa — (1) OCR/Vision: Mistral, ocr.space, Claude vision, GPT-4o, Google Vision, Tesseract local; (2) Transcrição áudio: Groq Whisper (free), OpenAI Whisper, Whisper local; (3) LLM extração/raciocínio: Claude, Mistral, Groq. Interface comum: name, kind (ocr/vision/audio/llm), método da categoria, health, quota. Tabela ai_provider_config unificada. Dashboard único lista todos com status/cota/key. Preferência = alternativas free-tier como default (Mistral + Groq); upgrade pago opcional. Chave criptografada.'
  - 'Bruno (2026-04-21) — NOTIFICAÇÃO AUTOMÁTICA EM FALLBACK (MVP): toda troca AUTOMÁTICA de provider (cota esgotada, health fail, erro recorrente) dispara e-mail para lista de admins com: provider que falhou + motivo, provider ativado, timestamp, link ao dashboard. Troca MANUAL pelo RH só grava audit log (já é deliberada). Lista de admins configurável (default: Bruno). Evita o cenário "sistema degradado silenciosamente".'
  - 'Terminologia esclarecida (2026-04-21): LIA = Legítimo Interesse Avaliação — documento interno exigido pela LGPD quando a empresa adota legítimo interesse como base legal (Art. 7º IX). Tem 3 partes: finalidade legítima, necessidade/proporcionalidade, balanceamento. Não é enviado à ANPD mas tem que existir. É uma das 3 pendências DPO do PRD (definir se match IA usa LIA ou consentimento explícito).'
  - 'Bruno (2026-04-21) — HELP CONTEXTUAL INLINE (MVP): ícone (?) ou ⓘ ao lado de cada campo, botão, coluna, status e métrica em TODAS as telas. Desktop: hover → popover 2-5 linhas + "ver mais" (drawer detalhado). Mobile/tablet: tap → bottom-sheet. Linguagem humana, não jargão. Conteúdo centralizado em tabela help_snippets(key, locale, title, body_md, related_keys) — editável pelo RH sem deploy. Telemetria UX captura cada abertura; IA-lê-logs identifica campos com labels ruins (muita consulta = provavelmente mal nomeado). Breadcrumbs contextuais no topo das telas. Cards "próximos passos" no rodapé das telas de submissão/revisão. Empty states educativos. Motivação: reduzir dependência de suporte humano que a Green House não tem capacidade de oferecer agora.'
  - 'Bruno (2026-04-21) — SUPORTE IA ESTILO CLAUDE (VISION, não MVP): Bruno considerou mas decidiu postergar. Concordância com pushback John: construir chatbot bom exige base de conhecimento curada, prompt eval, fallback humano — produto dentro do produto. Com 20 req/mês custo-benefício negativo agora. CAMINHO para Vision: tooltips + telemetria + help_snippets construídos no MVP já formam base retrieval-ready. Vision implementa chatbot flutuante com RAG sobre help_snippets + eventos UX recentes + wiki interna; se não souber, abre ticket RH; auditável.'
partyModeArtifacts:
  regulatoryMap:
    - norma: 'LGPD Art. 7º (base legal)'
      exige: 'Definir base legal por finalidade'
      impacto: 'Campo base_legal; política versionada; ROPA'
      severidade: 'Alta / MVP'
    - norma: 'LGPD Art. 11 (dados sensíveis)'
      exige: 'Consentimento granular para PcD, foto, sindical'
      impacto: 'Flag contem_dados_sensiveis; criptografia em repouso'
      severidade: 'Alta / MVP'
    - norma: 'LGPD Art. 20 (decisão automatizada)'
      exige: 'Revisão humana obrigatória de match IA'
      impacto: 'RH aprova rascunho IA (já D3); log explicável'
      severidade: 'Alta / MVP'
    - norma: 'ANPD Res. CD/ANPD 15/2024'
      exige: 'Runbook de notificação de incidente'
      impacto: 'Alertas + canal dpo@'
      severidade: 'Alta / MVP'
    - norma: 'Marco Civil Internet Art. 15'
      exige: 'Logs aplicação ≥ 6 meses'
      impacto: 'Log append-only hash-encadeado + timestamp + IP'
      severidade: 'Alta / MVP'
    - norma: 'Discriminação algorítmica (LGPD Art. 6 II + CF)'
      exige: 'Evitar viés gênero/idade/raça/CEP'
      impacto: 'Auditoria de features; métricas disparate impact'
      severidade: 'Alta / Fase 2'
    - norma: 'Lei 8.213/91 Art. 93 (Cotas PcD)'
      exige: 'Monitorar percentual em clientes ≥100 func'
      impacto: 'Relatório PcD por vaga/cliente; campo CID/laudo'
      severidade: 'Média / Fase 2'
    - norma: 'Lei 13.467/17 + eSocial S-2200'
      exige: 'Evento admissão se CLT'
      impacto: 'Export folha (interface, não escopo)'
      severidade: 'Média / Fase 2'
    - norma: 'Lei 12.527/11 (LAI) + TCU/CGU'
      exige: 'Trilha auditável imutável para servidor público'
      impacto: 'Hash-chain já atende; export por processo'
      severidade: 'Alta / MVP'
    - norma: 'CCT Asseio e Conservação (SEAC-DF)'
      exige: 'Validar piso salarial e insalubridade'
      impacto: 'Campo CCT + validação de piso'
      severidade: 'Média / Fase 2'
    - norma: 'Autenticação link mágico'
      exige: 'Mitigar sequestro de e-mail'
      impacto: 'TTL ≤15min, single-use, bind IP/UA, MFA p/ RH'
      severidade: 'Alta / MVP'
    - norma: 'Lei 14.129/21 (Gov Digital)'
      exige: 'Só se integrar Gov.br'
      impacto: 'Verificar com DPO'
      severidade: 'Baixa / Consultoria'
  dpoDecisionsRequired:
    - 'Base legal do match IA: legítimo interesse (com LIA) vs. consentimento explícito'
    - 'Prazo de retenção de currículos não contratados (6/12/24 meses)'
    - 'Enquadramento LAI quando gestor demandante é servidor público (doc público vs anonimização)'
workflowType: 'prd'
project_name: gestao-vagas
user_name: Bruno
communication_language: Portugues do brasil
document_output_language: Portugues do brasil
date: 2026-04-20
---

# Product Requirements Document — Sistema de Requisição e Gestão de Pessoal (Green House)

**Autor:** Bruno
**Data:** 2026-04-20 (sessão inicial) · 2026-04-21 (refinamentos)
**Projeto:** gestao-vagas
**PM Facilitador:** John (bmad-agent-pm)
**Versão:** 1.0 (PRD inicial completo)

## Como ler este documento

Este PRD é construído para **dupla audiência**: humanos que tomam decisões e LLMs/agentes que vão derivar artefatos (Épicos, Histórias, Arquitetura, UX). Por isso combina narrativa densa com identificadores rastreáveis (FR#, NFR#).

**Ordem sugerida de leitura:**

1. **Executive Summary + Project Classification** — panorama em 2 minutos.
2. **Success Criteria + Product Scope** — o que é "ganhar" e o que está (e não está) no MVP.
3. **User Journeys** — como o produto se sente para cada ator.
4. **Domain-Specific Requirements** — compliance, integrações, riscos.
5. **Innovation & Novel Patterns** — o que torna o produto diferenciado.
6. **Web Application Technical Requirements** — stack consolidada.
7. **Project Scoping & Phased Development** — Fatia 1 → 1.1 → 2 → 3.
8. **Functional Requirements (FR1–FR89)** — o contrato de capacidades.
9. **Non-Functional Requirements (NFR1–NFR54)** — quão bem o sistema precisa funcionar.

**Metadados estruturados** (vision, classification, decisões de Party Mode, mapa regulatório, ROPA) estão no **frontmatter YAML** deste arquivo — leia via parser quando for gerar artefatos derivados.

### Terminologia canônica

Usar nesta ordem, sem sinonimizar:

| Termo | Significado exato |
|---|---|
| **Requisição de Pessoal (RP)** | Ato administrativo: a solicitação submetida pelo gestor (áudio/PDF/texto). Ciclo: rascunho IA → revisão RH → aprovada ou rejeitada. |
| **Vaga** | Posição ativa após aprovação da RP. É sobre a Vaga que ocorre matching, R&S e preenchimento. |
| **Posto** | Função padronizada (ex.: "Apoio Administrativo I", "Recepcionista 12x36") vinculada a um Tomador. Vagas instanciam Postos. |
| **Tomador** | Cliente da Green House (órgão público, empresa privada, ou conta operada pela Green House). |
| **Gestor demandante** | Pessoa que submete a RP. Pode ser servidor público (Tipo B), funcionário Green House (Tipo A), ou funcionário de cliente privado (Tipo C). |
| **Candidato** | Pessoa cujo currículo existe na base. |
| **Currículo** | Documento + dados estruturados do Candidato. |
| **Círculo** | Grupo de visibilidade (tomador/departamento/coordenação). Nunca exibido ao usuário com essa palavra — na UI é "minhas vagas" + "vagas da minha área". |
| **Rascunho IA** | Saída estruturada da extração; existe até ser aprovado/rejeitado pelo RH. |

## Sumário

- [Executive Summary](#executive-summary)
- [Project Classification](#project-classification)
- [Success Criteria](#success-criteria)
- [Product Scope](#product-scope)
- [User Journeys](#user-journeys)
- [Domain-Specific Requirements](#domain-specific-requirements)
- [Innovation & Novel Patterns](#innovation--novel-patterns)
- [Web Application + Async Workers — Technical Requirements](#web-application--async-workers--technical-requirements)
- [Project Scoping & Phased Development](#project-scoping--phased-development)
- [Functional Requirements](#functional-requirements)
- [Non-Functional Requirements](#non-functional-requirements)
- [Appendix A — Matriz de Rastreabilidade](#appendix-a--matriz-de-rastreabilidade-jornada--fr--nfr)
- [Appendix B — Pendências DPO / Jurídico](#appendix-b--pendências-dpo--jurídico)
- [Appendix C — Changelog](#appendix-c--changelog-deste-prd)

## Executive Summary

**gestao-vagas** é um portal interno da **Green House Serviços de Locação de Mão de Obra LTDA** para capturar, estruturar e operacionalizar **Requisições de Pessoal** vindas dos gestores demandantes dos tomadores de serviço (órgãos públicos, empresas privadas, ou equipes Green House operando contas). Hoje essas requisições chegam por WhatsApp, telefone, e-mail e conversas verbais — sem padronização, sem rastreabilidade e sem extração estruturada dos requisitos, resultando em **perda de SLA contratual de reposição** e **retrabalho recorrente do RH**.

O produto aceita a requisição **como ela nasce no mundo real** — áudio bagunçado gravado no carro, print de WhatsApp, PDF de Termo de Referência, Word, ou combinações — e usa LLM multimodal para extrair requisitos obrigatórios, desejáveis, diferenciais e peculiaridades do gestor em JSON estruturado. **O RH revisa o rascunho gerado pela IA e aprova antes da vaga ficar ativa** — atendendo ao direito à revisão humana da LGPD Art. 20 como feature nativa, não como afterthought.

Uma segunda entrada ingere **currículos por e-mail encaminhado** (caixa monitorada pelo sistema), reutilizando o mesmo pipeline de IA para extrair dados estruturados, salvar o binário original e alimentar o talent pool. Upload manual de currículos pelo RH também é suportado no MVP; portal do candidato fica para V2.

**Usuários-alvo:**
- **Gestor demandante** (casual, ~20 requisições/mês distribuídas em 100 tomadores) — pode ser servidor público, funcionário Green House, ou privado.
- **RH Green House** (operacional, Bruno + equipe) — revisa rascunhos, opera fila de requisições, conduz R&S.

**Métricas de sucesso primárias:**
1. **T2F (Time to Fill)** — tempo médio do posto vago até preenchido.
2. **Requisições perdidas → zero** — canal único estruturado substitui WhatsApp/telefonema/verbal.

**Volume de referência:** 20 requisições/mês · 10 vagas ativas simultâneas · 100 tomadores cadastrados. Baixo volume justifica engenharia simples, com foco em confiabilidade e UX.

### What Makes This Special

1. **Ingestão onde o usuário já está.** Não exigimos que o gestor mude de comportamento — só que redirecione o que já faz. Áudio confuso é aceito; print ruim é aceito; PDF feio é aceito. Concorrentes (Gupy, Kenoby, Solides) exigem formulário estruturado na entrada — o que replica a fricção que o gestor hoje evita usando WhatsApp.

2. **Valor primeiro, identidade depois.** O gestor casual clica no link mágico e vai **direto para "Nova requisição"**, não para um formulário de cadastro. Só após submeter — quando já recebeu valor — o sistema pede identificação, pré-preenchida por IA a partir do domínio do e-mail (`.gov.br` → servidor público), assinatura do e-mail encaminhado, e base de tomadores já conhecidos. Gestor confirma com 1 clique em vez de preencher campos.

3. **IA propõe, humano decide.** Não é "ATS que rankeia e decide"; é "assistente que elimina retrabalho do RH". Isso destrava adesão de duas pontas: o gestor não se sente auditado, e o RH não se sente substituído. Legalmente blindado por LGPD Art. 20.

4. **Memória institucional por tomador.** Cada requisição enriquece templates por posto/tomador, mapeia peculiaridades recorrentes do gestor e alimenta o talent pool. A 10ª requisição de "Apoio Administrativo I" para a mesma secretaria tende a 1 clique.

5. **Contexto B2G nativo.** Sistema entende Termo de Referência, hierarquia obrigatório/desejável/diferencial, CCT aplicável (ex.: SEAC-DF), pisos salariais, Lei de Cotas — nenhum ATS de mercado cobre isso sem customização cara.

6. **Compliance espinhal.** Log append-only com hash encadeado (atende Marco Civil + LAI + LGPD + TCU/CGU), consentimento granular (Art. 11), base legal por finalidade (Art. 7º), trilha LAI ativada automaticamente quando o gestor é servidor público.

**Core Insight:** LLMs multimodais em 2026 são suficientemente confiáveis para extração estruturada de áudio + imagem + PDF com um único prompt e schema JSON. Combinados com revisão humana rápida do RH, o erro residual é tolerável para o contexto de Staffing B2G. Há três anos isso era pesquisa; hoje é commodity. Esta é a janela.

**Frase-valor:** *Receba, organize e preencha vagas mais rápido: o gestor fala (como preferir), a IA estrutura, o RH valida, a Green House cumpre SLA.*

### Diagrama de Contexto (C4 Nível 1)

```
                ┌──────────────────────────────────────────────────┐
                │           Ecossistema Green House                │
                │                                                  │
    ┌──────────┐│  ┌─────────────┐            ┌────────────────┐  │
    │ Gestor   │├─▶│             │            │                │  │
    │ Dem. (A) │││  │             │            │   RH           │  │
    │ GH       ││   │             │ ◀─────────▶│   (Bruno +     │  │
    └──────────┘│   │             │  revisa,   │    equipe)     │  │
    ┌──────────┐│   │             │  aprova,   │                │  │
    │ Gestor   ││── │             │  opera     │                │  │
    │ Dem. (B) │── ▶│ gestao-vagas│            └────────────────┘  │
    │ Servidor ││   │   (sistema) │                               │
    └──────────┘│   │             │ ◀──encaminha CV por email── ┐ │
    ┌──────────┐│   │             │                              │ │
    │ Gestor   ││   │             │                              │ │
    │ Dem. (C) │├──▶│             │                              │ │
    │ Privado  ││   │             │                              │ │
    └──────────┘│   └─────┬───────┘                              │ │
                │         │                                       │ │
                └─────────┼───────────────────────────────────────┼─┘
                          │                                       │
            ┌─────────────┼─────────────┬─────────────┐          │
            ▼             ▼             ▼             ▼          │
    ┌─────────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐   │
    │ Providers   │ │   SMTP    │ │ Caixa     │ │Evolution  │   │
    │ IA          │ │ (e-mail   │ │ email     │─┘(WhatsApp, │   │
    │ (OCR/Vision,│ │ transac.) │ │ monitora- │   Growth)   │   │
    │  Áudio, LLM)│ │           │ │ da (IMAP/ │ └───────────┘   │
    │ plugáveis:  │ │           │ │ webhook)  │                 │
    │ Mistral/Groq│ └───────────┘ └───────────┘                 │
    │ /OCR.space/ │                                              │
    │ /Claude     │                                              │
    └─────────────┘                                              │
                                                                 │
                    Artefatos internos (dentro do sistema):      │
                    ┌──────────────────────────────────────────┐ │
                    │ Postgres + pgvector │ Redis │ MinIO      │ │
                    │ Dramatiq workers │ Django web │ Email    │ │
                    │ ingestion worker │ Loki+Grafana obs      │ │
                    └──────────────────────────────────────────┘ │
                                                                 │
                        Infra: Docker Swarm + Traefik + VPS      │
                                                                 │
                             (subdomínio da Green House) ────────┘
```

Legenda:
- **3 perfis de Gestor** (A/B/C) submetem Requisições por áudio/PDF/texto/imagem.
- **RH** opera o sistema, revisa rascunhos IA, gerencia providers e vagas.
- **Providers de IA plugáveis** (OCR, áudio, LLM) são trocáveis em runtime pela UI.
- **Caixa de e-mail monitorada** recebe currículos encaminhados, processa automaticamente.
- **SMTP** envia notificações transacionais; **Evolution API** (Growth) fará o mesmo via WhatsApp.
- **Infra** roda em VPS única com Docker Swarm + Traefik; subdomínio da Green House expõe portal + painel RH.

## Project Classification

- **Project Type:** Web Application interna (portal do gestor + painel administrativo do RH) + workers assíncronos (fila de jobs de IA) + serviço de ingestão de e-mail monitorado.
- **Domain:** Staffing / Body Shop B2G — subdomínio HR Tech com camada de Public Procurement (Termo de Referência, Lei de Cotas, eSocial na interface, CCT de asseio/conservação quando aplicável).
- **Domain Complexity:** **Alta** — pela combinação de (1) requisitos regulatórios densos (LGPD Arts. 7/11/20, Marco Civil, LAI, Lei 8.213, ANPD Res. 15/2024); (2) risco de discriminação algorítmica no match IA; (3) três perfis distintos de gestor (servidor público, Green House, privado) com regras de visibilidade e auditoria distintas; (4) integração multimodal com LLM e validação humana. Arquitetura em si é de complexidade média (CRUD + fila + LLM); a complexidade vem do domínio.
- **Project Context:** Greenfield — sem código legado, sem sistema a migrar; a solução atual é manual (PDF por e-mail, WhatsApp, telefonema).
- **Compliance Requirements:** LGPD · Marco Civil da Internet · Lei 8.213/91 (Cotas PcD) · Lei 12.527/11 (LAI, condicional) · ANPD Res. CD/ANPD 15/2024 · CCT Asseio e Conservação (SEAC-DF) quando aplicável · eSocial (interface, Fase 2).

## Success Criteria

### User Success

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

### Business Success

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

### Technical Success

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

### Measurable Outcomes

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

## Product Scope

### MVP — Minimum Viable Product (Fatia 1)

**Objetivo:** validar "ingestão informal + IA + revisão RH resolve requisições perdidas e melhora T2F" E preparar o sistema para crescimento surpresa com telemetria e análise de UX ativas desde o dia 1.

- Portal web mobile-first para gestor
- Link mágico (e-mail → código TTL 15min single-use bound IP/UA) + cadastro "valor primeiro" com pré-preenchimento IA (domínio e-mail, assinatura, base de tomadores)
- Nova requisição aceitando: formulário estruturado + upload de áudio + PDF + texto colado + imagem/print (OCR via provedor plugável)
- Pipeline IA: Whisper (áudio) + pdfplumber (PDF texto) + OcrProvider plugável (Mistral default, ocr.space fallback) + Claude extraction (JSON schema) para requisitos
- Dashboard de provedores OCR/Vision: cota consumida/restante (contador local), data de reset, troca de provedor ativo, troca de API key criptografada, alerta em 80% de cota
- Revisão RH com UI dedicada (não Django Admin puro): diff visual rascunho IA vs. campos estruturados, aprovação/edição
- Publicação da vaga
- Ingestão de currículos: caixa de e-mail monitorada + upload manual RH; extração IA + armazenamento do binário original
- Match básico — algoritmo híbrido (regras rígidas em obrigatórios + embeddings pgvector nos desejáveis/diferenciais)
- Notificações e-mail (SMTP) para gestor e RH
- Log append-only hash-encadeado (LGPD + Marco Civil + LAI)
- Painel RH: fila de revisão, vagas ativas, candidatos, SLA próximo do vencimento
- "Minhas vagas" + "vagas da minha área" (rótulo amigável, nunca "círculo" na UI)
- Telemetria UX estruturada + job LLM semanal + dashboard /admin/ux-insights (completo no MVP, decisão consciente de Bruno)
- Consentimento granular, política de privacidade versionada, canal dpo@
- Compliance-checklist mínimo de go-live (ROPA, runbook incidente, 3 decisões DPO)

**Fora do MVP (explícito):** Word, WhatsApp Evolution API, portal do candidato, cotas PcD monitoradas, integração eSocial, análise de disparate impact.

### Growth Features (Post-MVP)

- Parsing de Word
- WhatsApp via Evolution API (notificações bidirecionais)
- Templates de posto por tomador (memória institucional explícita)
- Relatório de SLA contratual por tomador
- Dashboard analítico do gestor (além da submissão)
- Métricas de disparate impact no match (viés algorítmico)
- Monitoramento de cotas PcD (Lei 8.213/91 Art. 93)
- Provedores adicionais de OCR/Vision (Claude, GPT-4o, Google Vision, Tesseract local)

### Vision (Future)

- Portal do candidato self-service
- Integração Gov.br, SINE, Secretaria DIP
- Export estruturado eSocial S-2200
- Compliance automatizado (revisão anual, renovação consentimentos, purga por retenção)
- Multi-idioma / acessibilidade AA

## User Journeys

### Jornada 1 — Gestor Demandante (Servidor Público / Tipo B) — Happy Path

**Personagem:** Dra. Marlene Siqueira, 47, coordenadora-substituta numa secretaria de saúde do DF. Duas recepcionistas acabaram de pedir demissão. Segunda-feira, 7h42.

**Abertura:** Abre WhatsApp por reflexo; lembra do portal novo; clica no link do último e-mail.

**Subida:** Tela minimalista pede e-mail. Digita `marlene.siqueira@saude.df.gov.br`. Código de 6 dígitos chega em ≤10s. Cola. Entra direto em "Nova requisição" — não em cadastro. Botão grande "🎙️ Gravar áudio". Grava 90s explicando o posto. Envia. "Recebemos. Volte em 3 min."

**Clímax:** 2 min depois, e-mail com resumo da requisição extraída pela IA. Rascunho correto em 90%. Marca "validar como está". Só então sistema pede confirmação de 3 campos pré-preenchidos (Secretaria / Coordenação / Cargo). Um clique. Nunca preencheu formulário.

**Resolução:** 8h05, café. Requisição submetida, RH ciente, Marlene tranquila. O portal foi mais rápido que WhatsApp seria.

**Capacidades:** link mágico; redirecionamento para "Nova requisição"; upload áudio mobile; pipeline Whisper + Claude; notificação e-mail com resumo; cadastro progressivo pós-submissão; pré-preenchimento por domínio de e-mail (`.gov.br` → servidor público); detecção de CCT aplicável.

### Jornada 2 — Gestor Demandante — Edge Case / Recovery

**Personagem:** Roberto Paiva, 52, diretor administrativo de empresa privada (Tipo C). Manda áudio confuso de 4 min falando de posto vago, reclamando do colaborador anterior e mencionando um contrato diferente. IA identifica ambiguidade.

**Cena:** 3 min depois recebe: "Sua requisição precisa de esclarecimento — a IA identificou 2 possíveis vagas".

**Subida:** Abre e vê dois rascunhos candidatos lado a lado. Botões: "Só a A" / "Só a B" / "Ambas" / "Nenhuma — deixa eu escrever". Clica "Só a B". Campos em amarelo pedem confirmação: piso, escala, experiência. Confirma em 30s.

**Resolução:** requisição salva corretamente. Histórico guarda o áudio, as duas interpretações e a decisão. RH nem precisa envolver-se.

**Capacidades:** detecção de ambiguidade (múltiplos candidatos com score); UI de resolução em 1 tela; marcação visual de baixa confiança; persistência auditável de todas as hipóteses.

### Jornada 3 — RH (Bruno) — Operação diária

**Personagem:** Bruno Fontes, Coord. RH Green House. 9h, 4 requisições pendentes.

**Cena:** Entra no painel. Kanban horizontal: "Em revisão (4)" | "Ativas (7)" | "Em R&S (3)" | "Preenchidas" | "Arquivadas".

**Subida:** Clica na 1ª. Tela com 3 painéis: **esquerda** — inputs originais (áudio com player sincronizado à transcrição; PDF; texto); **centro** — rascunho IA estruturado em campos editáveis; **direita** — ações Aprovar / Esclarecer / Rejeitar. Campos amarelos = baixa confiança. Áudio pula direto para o trecho relevante. Ajusta 1 piso. Aprova. 90 segundos por revisão.

**Clímax:** Card lateral: "Este posto é semelhante a 3 requisições anteriores do mesmo tomador. Reaproveitar template?" Clica "Sim" — campos secundários preenchidos.

**Resolução:** 4 revisões em ~8 min. Gestores notificados. Vagas publicadas. Bruno livre para R&S onde agrega valor humano.

**Capacidades:** kanban por status; visualizador sincronizado multimodal; diff visual; destaque de baixa confiança; reaproveitamento de template por tomador/posto; notificação automática pós-aprovação; histórico auditável.

### Jornada 4 — Ingestão de currículo por e-mail encaminhado — Automática

**Personagem:** Bruno, papel "curador passivo".

**Cena:** 14h20. Ex-colega manda currículo para o e-mail do RH. Bruno encaminha para `curriculos@greenhousedf.com.br`.

**Subida (invisível ao usuário):**
1. Sistema detecta novo e-mail em ≤1 min.
2. Extrai anexos; valida MIME/hash (anti-loop).
3. Pipeline IA extrai nome, contato, experiência, formação, pretensões.
4. Deduplica (CPF → e-mail+telefone → nome+telefone); atualiza ou cria candidato.
5. Salva binário em MinIO.
6. Dispara matching contra vagas abertas.
7. Se match ≥ 70%, notifica Bruno.

**Resolução:** 1h depois Bruno vê o novo currículo em "Candidatos recentes" com tags e scores.

**Capacidades:** monitoramento caixa e-mail (webhook preferencial, IMAP IDLE fallback); whitelist ou quarentena; pipeline idempotente; deduplicação multi-chave; trigger matching; notificação condicional.

### Jornada 5 — Operação técnica / Troca de provedor OCR

**Personagem:** Bruno como admin técnico.

**Cena:** Alerta: "Mistral Vision atingiu 85% da cota mensal".

**Subida:** Configurações → Provedores OCR/Vision. Tabela: provedor, status, consumido, restante, reset. Clica "Tornar ocr.space o ativo". Sistema valida API key (health check). Salvo. Próximos jobs usarão ocr.space.

**Clímax:** sem deploy. Sem reinicialização. Pode atualizar API key direto na UI (campo criptografado; audit log).

**Resolução:** operação segue. Sem chamar técnico.

**Capacidades:** OcrProvider plugável em runtime; API keys criptografadas; health check; contador local de cota; dashboard comparativo; audit log de configuração.

### Journey Requirements Summary

| Área de capacidade | Jornadas | Prioridade |
|---|---|---|
| Auth / Link mágico / Cadastro progressivo | J1, J2 | MVP |
| Upload multimodal (áudio, PDF, texto, imagem) | J1, J2 | MVP |
| Pipeline IA de extração estruturada | J1, J2, J4 | MVP |
| Tratamento de ambiguidade/baixa confiança | J2 | MVP |
| Painel RH — kanban + revisão + diff visual | J3 | MVP |
| Reaproveitamento de template por tomador | J3 | MVP |
| Notificações por e-mail | J1-J4 | MVP |
| Monitoramento de caixa de e-mail | J4 | MVP |
| Deduplicação multi-chave de candidatos | J4 | MVP |
| Matching vaga × currículo | J4 | MVP |
| OcrProvider plugável + dashboard de cotas | J5 | MVP |
| Audit log / hash-chain (LGPD/LAI) | todas | MVP |
| Detecção automática de tipo_gestor | J1 | MVP |
| CCT / piso salarial aplicável | J1 | MVP |
| WhatsApp (Evolution API) | — | Growth |
| Portal do candidato | — | Vision |

## Domain-Specific Requirements

### Compliance & Regulatório

**Proteção de dados pessoais (LGPD — Lei 13.709/18):**
- **Art. 7º (Bases legais):** cada finalidade com base legal explícita; campo `base_legal` por registro; ROPA mantido e revisado trimestralmente. Para match IA: **LIA (Legítimo Interesse Avaliação)** documentada OU consentimento explícito — decisão DPO.
- **Art. 11 (Dados sensíveis):** currículos podem conter saúde (PcD, CID/laudo), filiação sindical, foto — consentimento específico destacado + criptografia em repouso. Flag `contem_dados_sensiveis` ativa fluxo protegido.
- **Art. 20 (Decisão automatizada):** match IA e ranking oferecem revisão humana obrigatória — RH sempre aprova rascunho IA antes da vaga publicar e antes de match virar contato. Log explicável acessível ao titular.
- **ANPD Res. CD/ANPD 15/2024 (Incidentes):** runbook documentado, canal `dpo@greenhousedf.com.br` público, alertas de acesso anômalo, comunicação a titular e ANPD em prazo regulamentar.

**Changelog de políticas (Termos de Uso / Política de Privacidade) estilo Nubank:**
- Ao logar, se houve nova versão desde o último aceite, modal exibe **resumo em tópicos do que mudou** (diff humanizado, escrito pelo RH ao versionar) + link "ver documento completo".
- Tabela `policy_acceptance(user_id, policy_version_id, summary_shown, accepted_at, ip, ua)` — imutável.
- Toda versão de política tem `version`, `effective_at`, `full_text`, `summary_of_changes` (markdown).

**Rastreabilidade (Marco Civil Lei 12.965/14 Art. 15 + LAI Lei 12.527/11 + TCU/CGU):**
- Log **append-only com hash encadeado** — cada entrada encadeia hash da anterior.
- Retenção mínima 6 meses (Marco Civil); 5 anos quando gestor for servidor público (boa prática contratual) — final DPO.
- Cada ação: `user_id`, `IP`, `UA`, `timestamp`, `acao`, `entidade`, `antes`, `depois`, `hash_prev`, `hash_atual`.
- Comando CLI de verificação de integridade da cadeia.
- Export auditável por processo (pedidos LAI) com campos privilegiados mascarados.

**Trabalhista / Cotas:**
- **Lei 8.213/91 Art. 93 (Cotas PcD):** vaga pode ser marcada PcD-preferencial; monitoramento de percentual por tomador ≥100 func. — Fase 2.
- **Convenções coletivas (CCT):** sistema identifica CCT aplicável (ex.: SEAC-DF / SIEMACO-DF) e valida piso salarial no cadastro da vaga; alerta se abaixo do piso.
- **eSocial S-2200 (Fase 2):** export estruturado quando gestor efetiva contratação.

**Risco de discriminação algorítmica (LGPD Art. 6º II + CF Art. 5º):**
- Proxies sensíveis (gênero por nome, idade por ano de formação, raça por foto, CEP por bairro) excluídos de features de ranking.
- Auditoria de features documentada.
- Métricas de disparate impact — Fase 2.

### Constraints Técnicos

**Segurança:**
- Link mágico: TTL ≤15 min, single-use, bound a IP+UA. Código não utilizável sem o e-mail correspondente.
- MFA (TOTP) opcional para contas RH.
- TLS 1.3 obrigatório (Traefik redireciona HTTP→HTTPS).
- Criptografia em repouso para campos sensíveis (CID/laudo, foto, CPF, API keys) via `django-fernet-fields` / `django-cryptography`; chave mestra em env/secrets manager.
- CSRF, XSS, SQL injection protegidos nativamente pelo Django; CSP restritiva nos templates.
- Upload: validação de MIME-type real, limite 20 MB, antivírus ClamAV (recomendado Fase 2).

**Privacidade & Retenção:**
- Política de privacidade e Termos de Uso **versionados** — cada consentimento com `policy_version_id`.
- Direitos do titular (LGPD Arts. 17-22): endpoint/página para acesso, correção, anonimização, portabilidade, revogação.
- Retenção de currículos não contratados: default conservador **12 meses** com extensão por consentimento — final DPO.
- Anonimização de logs após 5 anos (exceto em processo judicial ativo).

**Performance & Disponibilidade:**
- Pipeline multimodal ≤3 min p95 / ≤8 min p99.
- Link mágico <10 s p95.
- Uptime ≥99% mensal.
- Backup diário (Postgres + MinIO); RPO ≤24h, RTO ≤4h; **restore testado trimestralmente** (obrigatório).
- Observabilidade: Loki + Grafana + alertas em canal do RH.

**Custo operacional:**
- LLM + OCR por vaga processada ≤ R$ 0,15 p95.
- Alerta em 80% de cota por provider ativo.
- Troca de provider em runtime sem deploy.

### Integration Requirements

**Arquitetura de Providers de IA plugável e universal (MVP):**

Todas as categorias de IA externa abstraídas sob interface comum, selecionáveis e trocáveis via UI RH, com API keys criptografadas e contador local de cota:

| Categoria | Free-tier default | Alternativas no MVP | Futuras (Growth) |
|---|---|---|---|
| **OCR / Vision** (imagem, PDF escaneado) | Mistral Vision | ocr.space | Claude Vision, GPT-4o, Google Vision, Tesseract local |
| **Transcrição de áudio** | Groq Whisper | OpenAI Whisper | Whisper local, AssemblyAI |
| **LLM (extração + raciocínio)** | Groq (Llama/Mixtral) ou Mistral | Claude | GPT-4o, local (Ollama) |

Tabela `ai_provider_config(kind, name, is_active, is_fallback, encrypted_api_key, quota_resets_on, updated_by, updated_at)`.
Interface Python Protocol com `kind`, `name`, método da categoria (`extract` / `transcribe` / `complete`), `health()`, `quota()`.

**Notificação automática em fallback (MVP):** toda troca AUTOMÁTICA de provider (cota esgotada / health fail / erro recorrente) dispara e-mail para `admin_notification_list` contendo provider falho + motivo + provider ativado + timestamp + link ao dashboard. Troca manual só grava audit log.

**Outros sistemas externos:**

| Sistema | Finalidade | Prioridade | Modo |
|---|---|---|---|
| SMTP | notificações + código do link mágico | MVP | saída |
| Caixa IMAP/webhook `curriculos@...` | ingestão automática de currículos encaminhados | MVP | entrada |
| pgvector (Postgres) | embeddings para match e duplicata | MVP | interno |
| MinIO (S3-compatible) | armazenamento de binários originais | MVP | interno |
| Evolution API (WhatsApp) | notificações bidirecionais | Growth | saída/entrada |
| Gov.br / SINE / Secretaria DIP | bancos de currículos externos | Vision | API |
| eSocial (S-2200) | evento de admissão | Vision | saída |

### Risk Mitigations

| Risco | Mitigação |
|---|---|
| Sequestro de e-mail corporativo → acesso indevido via link mágico | TTL curto, single-use, bind IP+UA, MFA opcional, reautenticação em IP atípico |
| Extração IA incorreta publica vaga errada | Revisão RH obrigatória (LGPD Art. 20); diff visual; campos amarelos de baixa confiança; originais sempre disponíveis |
| Requisições duplicadas por múltiplos gestores do mesmo tomador | Detecção em 3 camadas (determinística + pgvector + LLM); RH decide mesclar/relacionar/descartar; `parent_id` preserva vínculo; auditoria de decisão |
| Cota de provider esgotada em horário crítico | ≥2 providers por categoria; alerta em 80%; fallback automático em runtime; **e-mail obrigatório ao admin quando fallback dispara** |
| Degradação silenciosa após fallback | Notificação por e-mail torna a troca visível; dashboard destaca provider ativo ≠ default |
| Discriminação algorítmica inadvertida | Features sensíveis excluídas; auditoria; disparate impact (Fase 2); "explicar este match" |
| Perda de dados (VPS única) | Backup diário offsite + restore trimestral testado; replicação Fase 2 |
| Vazamento via export/log | Hash de user_id; export LAI mascara campos privilegiados; CSP + headers segurança |
| Gestor servidor público cai em pedido LAI | Trilha privilegiada (candidatos) separada da pública (requisição + decisões); export LAI filtra automaticamente |
| Loop infinito na ingestão de e-mail | Anti-loop por Message-Id + hash do conteúdo; whitelist ou quarentena |
| Candidato envia CV por 3 canais diferentes | Dedup multi-chave: CPF → e-mail+telefone → nome+telefone; merge com preservação de origens |
| Revogação de consentimento cria registros órfãos | Anonimização em vez de exclusão; campo `anonimizado_em`; auditoria preservada |
| Usuário nunca lê mudanças de políticas | Modal com resumo humanizado dos diffs (estilo Nubank) antes do documento completo |

### Decisões pendentes para DPO / Jurídico

Não bloqueiam início do desenvolvimento; bloqueiam go-live em produção.

1. **Base legal do match IA** — LIA documentada (legítimo interesse) ou consentimento explícito do candidato?
2. **Prazo de retenção de currículos não contratados** — default conservador 12 meses; DPO valida.
3. **Enquadramento LAI quando gestor é servidor público** — quais campos da requisição são públicos vs. anonimizados em eventual pedido LAI?

## Innovation & Novel Patterns

### Detected Innovation Areas

**1. Jornada invertida "valor primeiro, identidade depois".**
Padrão comum em apps B2C mas raríssimo em HR Tech/ATS corporativo, onde o dogma é "primeiro cadastre-se, depois use". Aqui o gestor submete a requisição (entrega valor) antes de completar cadastro — que é depois preenchido com IA pré-populando a partir de sinais (domínio do e-mail, assinatura, base de tomadores, conteúdo da própria requisição). A inovação não é cada peça isolada, é a orquestração dos sinais para que o gestor clique "1" vez onde normalmente clicaria "10".

**2. Ingestão genuinamente "como você manda no WhatsApp".**
O mercado de ATS trata áudio/print/PDF como anexo decorativo. Aqui eles são a entrada primária, processada por LLM multimodal com schema JSON no momento da submissão. O RH nunca mais lê áudio a primeira vez; ele revisa uma extração estruturada, com timestamp clicável de volta ao trecho do áudio.

**3. Detecção de duplicata em 3 camadas com LLM raciocinador.**
(i) Determinística, (ii) semântica via embeddings pgvector, (iii) LLM que raciocina sobre a distinção entre duplicata pura, vagas irmãs, substituição vs. ampliação — e entrega veredito com justificativa. O LLM não decide, ele explica para o RH decidir. Humano-no-loop como princípio.

**4. Providers de IA universalmente plugáveis em runtime.**
Qualquer categoria de IA (OCR/Vision/Áudio/LLM) é selecionável e trocável em runtime pela UI do RH — com prioridade a alternativas free-tier (Mistral, Groq). Combinado com notificação automática por e-mail toda vez que fallback dispara, oferece visibilidade ao operador que sistemas "automatizados" escondem. Anti-lock-in, anti-cost-surprise, pró-resiliência.

**5. Log append-only com hash encadeado como feature pública.**
Integridade auditável não é feature de segurança escondida — é promessa de marca, diferencial. "Você consegue provar que esse registro não foi adulterado" vira argumento B2G (TCU, CGU, LAI). Comando CLI público de verificação de integridade.

**6. "Changelog humano" de políticas estilo Nubank.**
Em vez de empurrar "Termos Atualizados, clique OK", sistema exibe resumo em tópicos do que mudou — escrito pelo RH ao versionar. Transparência que respeita tempo do usuário. Padrão fintech raramente visto em HR Tech.

**7. IA lendo logs de UX para sugerir melhorias do próprio sistema.**
Meta-recursão: sistema usa seu próprio pipeline de IA para analisar como é usado. Custo desprezível (~R$ 0,20/mês), mas cria ciclo de melhoria contínua sem depender de formulários de feedback.

**8. Help contextual onipresente como substituto de suporte humano.**
Ícone "(?)" ao lado de cada campo, botão, coluna, status e métrica. Hover (desktop) ou tap (mobile) revela explicação em linguagem humana. Breadcrumbs contextuais + cards "próximos passos" + empty states educativos compõem a orientação "de onde vim, onde estou, para onde vou". Conteúdo centralizado em help_snippets editável pelo RH sem deploy. Telemetria de cada abertura alimenta IA-lê-logs que identifica labels ruins (muita consulta = provavelmente mal nomeado). Sistema guia o usuário antes que ele precise de suporte — inovação-processo sobre inovação-tecnológica. Prepara a base para suporte IA em Vision.

### Market Context & Competitive Landscape

| Concorrente | O que faz | Onde perde para gestao-vagas |
|---|---|---|
| Gupy | ATS líder BR, foco em seleção e candidate experience | Exige formulário rígido de vaga; não aceita áudio; não entende Termo de Referência; caro para uso interno |
| Kenoby (Solides Talent) | ATS com automação e pipeline | Igual Gupy + menos flexibilidade de customização |
| Solides | Gestão de pessoas + recrutamento | Foco em CLT e cultura; ingestão formal |
| Recrutei, Abler, Trampolim, Vagas.com | ATS nacionais menores | Ingestão estruturada clássica; sem contexto B2G |
| Google Forms + Planilha + WhatsApp (solução atual da Green House) | Registro informal | Sem auditoria, sem extração, sem match, sem rastreabilidade — a dor que motiva o projeto |
| LinkedIn Recruiter / Indeed | Sourcing externo | Captação de candidatos, não gestão de requisição interna |

Conclusão competitiva: Gupy e similares resolvem "seleção de candidato". A parte "receber a requisição informal do gestor e estruturá-la" fica sem dono no mercado — território de gestao-vagas. Potencialmente integrável a um ATS de mercado em Vision (export da vaga pronta via API).

Contexto B2G: nenhum ATS brasileiro trata Termo de Referência, Lei de Cotas, CCT aplicável, hierarquia obrigatório/desejável/diferencial e trilha LAI como features nativas. Território aberto.

### Validation Approach

Hipóteses testáveis no MVP (primeiros 60 dias):

| Hipótese | Métrica de validação | Meta |
|---|---|---|
| H1 — Gestor aceita submeter por áudio | % das requisições submetidas com ≥1 áudio | ≥ 40% |
| H2 — Jornada invertida reduz abandono | Conversão "clicou no link mágico → submeteu" | ≥ 70% |
| H3 — IA acerta extração em 1ª tentativa | % rascunhos aprovados RH com ≤2 ajustes | ≥ 70% em 30d, ≥ 90% em 12m |
| H4 — Duplicata IA economiza tempo RH | % duplicatas verdadeiras identificadas | ≥ 80% |
| H5 — Free tiers cobrem o volume | R$/mês em APIs pagas | ≤ R$ 50/mês |
| H6 — Gestor percebe sistema como "mais rápido que WhatsApp" | Pesquisa qualitativa com 10 gestores em 60 dias | ≥ 7/10 |
| H7 — Help contextual reduz suporte | Solicitações ao RH sobre "como faço X?" | ≥ 50% de redução vs. baseline percebido |

Fallback se hipótese falhar:
- H1 → reforçar onboarding com vídeo 30s; se persistir, áudio vira opcional.
- H2 → remover "valor primeiro" e voltar ao cadastro tradicional.
- H3 → aumentar intervenção RH; expor mais campos de baixa confiança até ajustar prompt.
- H4 → marcar suspeitas como "pending_review" e RH decide; sem fluxo automático.
- H5 → ativar providers pagos com limite de gasto + alerta.
- H6 → qualitativo real dos gestores, iterar UX.
- H7 → revisar textos dos tooltips via job IA-lê-logs; se não resolver, reforçar help com vídeos curtos.

### Risk Mitigation

- "Inovação demais assusta usuário": UI esconde a complexidade (gestor nunca vê "provider de IA" ou "embedding"). Toda a inovação é invisível.
- "LLM alucina em contexto B2G": revisão RH obrigatória + diff visual + campos de baixa confiança destacados + input original sempre disponível.
- "Free tiers podem ser removidos": abstração plugável permite trocar provider sem deploy; audit de custo embutido.
- "Detecção de duplicata falsa positiva mescla coisas diferentes": RH sempre decide (nunca automático); auditoria permite desfazer; `parent_id` é reversível.
- "Tooltips viram lixo de informação se não curados": help_snippets tem owner (RH) + telemetria de uso + job de IA identificando termos sub-explicados.

## Web Application + Async Workers — Technical Requirements

### Project-Type Overview

Sistema web server-rendered predominantemente (Django templates + HTMX para interações dinâmicas, sem SPA full) com 3 superfícies:

1. Portal do Gestor (público autenticado por link mágico) — mobile-first, focado em submissão de requisição.
2. Painel do RH (admin) — UI dedicada em Django templates (ou Django Admin customizado com django-unfold para visual moderno), com kanban de requisições, revisão de rascunhos IA, configuração de providers.
3. Serviço de ingestão de e-mail (worker/daemon separado) — monitora caixa `curriculos@greenhousedf.com.br` por IMAP IDLE ou webhook; emite jobs para fila.

Tudo orquestrado como serviços Docker em Docker Swarm com Traefik expondo apenas o portal via subdomínio da Green House.

### Technical Architecture Considerations

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

### Functional Architecture — Componentes principais

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

### Authentication & Authorization Model

Autenticação:
- Link mágico default (gestores e RH).
- MFA (TOTP) opcional para contas administrativas.
- Sessão Django com cookie HttpOnly, Secure, SameSite=Lax; rotação em mudança de privilégio.

Autorização (pool único com visibilidade por círculo):
- Perfis: `rh_admin`, `rh_operator`, `gestor`, `system`.
- Atributo derivado `tipo_gestor` (A/B/C) define trilha de auditoria (B ativa LAI).
- Tabela `circulo(tomador_id, departamento, coordenacao)` agrupa gestores.
- Queryset mixin no Django filtra automaticamente por círculo para `gestor`.

### API Surface (mínima)

Sistema server-rendered — sem API pública no MVP:
- `/webhooks/email-inbound` — webhook do provedor de e-mail quando chega mensagem na caixa monitorada. Alternativa IMAP IDLE é worker daemon sem endpoint.
- `/webhooks/whatsapp` (Growth) — callbacks Evolution API.
- `/api/internal/*` — endpoints autenticados por sessão para chamadas HTMX.

DRF entra apenas se houver API externa em Growth/Vision.

### Data Model — Entidades principais (MVP)

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

### Implementation Considerations

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

### Estimativa de esforço (Fatia 1 — MVP, solo)

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

## Project Scoping & Phased Development

### Resumo de Fatias (Scanning rápido)

| Fatia | Objetivo | FRs incluídos | NFRs críticos | Critério de saída |
|---|---|---|---|---|
| **1 (MVP)** | Validar hipótese central: ingestão informal + IA + revisão RH reduz requisições perdidas e melhora T2F | FR1–FR78, FR79–FR83 (captura), FR84–FR89 (core) | NFR1–NFR10 (latência/escala), NFR11–NFR19 (segurança), NFR20–NFR25 (confiabilidade), NFR26–NFR33 (LGPD baseline), NFR34–NFR40 (custo+obs), NFR41–NFR54 | ≥5 tomadores ativos; ≥50% reqs pelo sistema em 30d; pipeline IA estável; compliance checklist completo |
| **1.1 (Follow-up)** | Amadurecer MVP com aprendizado dos primeiros usuários | FR34 (ambiguidade split), FR51 (templates formais), FR81 (job LLM ativo), FR37 (Camada 3 duplicata), FR73 cobertura periférica | Mesmos do MVP (sem regressão) | Saída: telemetria com ≥30d, todos tooltips, LLM de insights operante |
| **2 (Growth)** | WhatsApp + Word nativo + analytics + providers extras | FR relacionados a canais/providers adicionais | NFR de antivírus, MFA obrigatório, disparate impact | Adoção ≥80%, redução T2F comprovada ≥25% |
| **3 (Vision)** | Portal candidato, suporte IA, Gov.br/SINE, eSocial, multi-idioma, i18n AA | Novos FR a derivar | Novos NFR de acessibilidade e interop | Quando o produto ultrapassar uso interno |

Detalhes de cada fatia estão nas subseções abaixo.

### MVP Strategy & Philosophy

**Abordagem MVP:** Problem-solving MVP com arquitetura defensável.

- Resolver a dor real: requisições perdidas e T2F alto.
- Arquitetura correta desde o dia 1 em tudo que é caro de refazer (auth, log append-only, providers plugáveis, schema de dados, privacy-by-design, telemetria).
- Polimento/coverage reduzidos no que é barato iterar depois (nº de providers concretos, polish visual do painel, features secundárias do help).

**Resource Requirements:** 1 engenheiro (Bruno) em ritmo solo; ideal ter um revisor externo ocasional para PR review crítico; apoio jurídico/DPO pontual.

### MVP Feature Set (Fatia 1) — Objetivo: em produção interna com ≥5 tomadores ativos

#### Core User Journeys Suportadas

- **J1** (Gestor servidor público submete via áudio) — completa
- **J2** (Edge case / ambiguidade) — simplificada: mostra apenas campos de baixa confiança amarelos; sem split de "2 vagas em 1 áudio" (vai para Fatia 1.1 se acontecer muito)
- **J3** (RH revisa) — completa com kanban + diff visual + reaproveitamento de template
- **J4** (Ingestão currículo por e-mail) — completa, mas com 1 só provedor de e-mail suportado (o que a Green House usar)
- **J5** (Troca de provider OCR) — UI operante, 2 providers concretos por categoria (Mistral + ocr.space; Groq + OpenAI; Groq + Claude). Demais providers em Growth.

#### Must-Have Capabilities (Fatia 1)

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

### Fatia 1.1 (Quick follow-up, ~1 semana após Fatia 1)

- Completar help contextual em telas periféricas
- Split de "2 vagas em 1 áudio" (se acontecer em campo)
- Formalização de templates por tomador/posto (hoje é "copiar similar" → biblioteca editável)
- Ativação do job LLM de insights UX (se houver volume)
- Ativação da Camada 3 do duplicate detection (LLM raciocinador)

### Fatia 2 — Growth (Post-MVP)

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

### Fatia 3 — Vision (Future)

- Portal do candidato self-service
- Suporte IA estilo Claude (chatbot RAG sobre help_snippets + eventos + wiki)
- Integração Gov.br / SINE / Secretaria DIP
- Export estruturado eSocial S-2200
- Compliance automatizado (revisão anual, renovação, purga)
- Multi-idioma / acessibilidade AA
- Integração bidirecional com ATS de mercado (Gupy/Solides)
- IA que monta "Formulário DIP" automaticamente a partir da vaga

### Risk Mitigation Strategy

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

## Functional Requirements

### 1. Acesso e Identidade

- **FR1:** Usuário pode solicitar acesso digitando apenas seu e-mail; recebe código de uso único por e-mail.
- **FR2:** Usuário pode autenticar-se usando o código recebido dentro de uma janela de validade; o código torna-se inválido após uso ou expiração.
- **FR3:** Sistema pode invalidar automaticamente um código se detectar tentativa de uso de IP ou dispositivo diferente do que solicitou.
- **FR4:** Usuário pode completar seu cadastro após submeter sua primeira ação de valor (cadastro progressivo "valor primeiro").
- **FR5:** Sistema pode pré-preencher campos do cadastro a partir de sinais disponíveis (domínio do e-mail, assinatura de e-mail encaminhado, base de tomadores conhecidos, conteúdo da própria submissão).
- **FR6:** Sistema pode classificar automaticamente o `tipo_gestor` (servidor público, Green House ou empresa privada cliente) a partir do domínio do e-mail.
- **FR7:** Conta RH administrativa pode habilitar autenticação adicional (MFA por TOTP) para a própria conta.
- **FR8:** RH administrador pode atribuir/alterar manualmente o círculo de visibilidade (órgão, departamento, coordenação) de qualquer gestor.
- **FR9:** Usuário pode encerrar sua sessão ativa a qualquer momento, invalidando o cookie.

### 2. Submissão de Requisição de Pessoal

- **FR10:** Gestor pode submeter uma requisição de pessoal gravando áudio diretamente no navegador (desktop ou mobile).
- **FR11:** Gestor pode submeter uma requisição anexando arquivo PDF (nativo ou escaneado).
- **FR12:** Gestor pode submeter uma requisição anexando imagens (JPG/PNG), incluindo prints de conversas.
- **FR13:** Gestor pode submeter uma requisição colando texto em campo livre.
- **FR14:** Gestor pode combinar múltiplos tipos de entrada na mesma requisição (ex.: áudio + PDF).
- **FR15:** Sistema rejeita arquivos que excedam o limite de tamanho ou cujo MIME-type real não corresponda aos formatos suportados, informando o motivo ao gestor.
- **FR16:** Gestor pode acompanhar o status da sua requisição (recebida, em extração IA, em revisão RH, aprovada, rejeitada) via portal e por notificação externa.
- **FR17:** Gestor pode receber resumo em linguagem natural do que o sistema entendeu da sua submissão, via e-mail, em até alguns minutos após enviar.
- **FR18:** Gestor pode editar/reenviar uma requisição rejeitada pelo RH; histórico é preservado.

### 3. Ingestão de Currículos

- **FR19:** RH pode fazer upload manual de currículos (PDF/Word) individuais ou em lote.
- **FR20:** Sistema pode ingerir automaticamente currículos recebidos em uma caixa de e-mail monitorada, extraindo anexos, lendo corpo do e-mail e salvando binário original.
- **FR21:** Sistema rejeita ingestão de e-mails não originários de remetentes em lista autorizada, ou coloca-os em fila de quarentena para decisão do RH.
- **FR22:** Sistema pode deduplicar candidatos recém-ingeridos contra a base existente, usando múltiplas chaves (CPF, e-mail+telefone, nome+telefone).
- **FR23:** Sistema pode detectar e ignorar reingestões do mesmo e-mail/anexo já processado (anti-loop).
- **FR24:** RH pode visualizar todos os currículos ingeridos, com origem identificada (upload manual ou e-mail monitorado).

### 4. Extração IA e Revisão Humana

- **FR25:** Sistema pode transcrever áudio em texto usando provider de transcrição configurado.
- **FR26:** Sistema pode extrair texto de PDF nativo e, em fallback, de PDF/imagem escaneada via provider OCR/Vision configurado.
- **FR27:** Sistema pode extrair requisitos estruturados (obrigatórios, desejáveis, diferenciais, peculiaridades, piso salarial, escala, CCT aplicável) de entradas multimodais via LLM, produzindo JSON validado por schema.
- **FR28:** Sistema pode atribuir score de confiança por campo extraído.
- **FR29:** RH pode visualizar, em interface dedicada, o rascunho IA lado a lado com os inputs originais (áudio com player sincronizado à transcrição, PDF aberto, texto).
- **FR30:** RH pode clicar em qualquer campo da extração para saltar diretamente ao trecho do áudio ou documento que originou o valor.
- **FR31:** RH pode editar qualquer campo do rascunho IA antes de aprovar.
- **FR32:** RH pode aprovar, rejeitar (com motivo) ou solicitar esclarecimento sobre um rascunho IA.
- **FR33:** Sistema pode destacar visualmente campos com confiança abaixo de um limiar configurável.
- **FR34:** Sistema pode apresentar múltiplas interpretações candidatas quando a IA detectar ambiguidade no input do gestor (Fatia 1.1; infra preparada).
- **FR35:** Aprovação de rascunho é ação reversível somente dentro de janela limitada, com registro de auditoria e motivo.

### 5. Detecção de Duplicatas e Correlações

- **FR36:** Sistema pode identificar requisições candidatas a duplicata usando (a) hash de anexo, (b) headers de e-mail, (c) fingerprint estruturado (tomador, posto, cidade, data) e (d) similaridade semântica por embeddings.
- **FR37:** Sistema pode produzir um veredito explicativo (via LLM) sobre a relação entre duas requisições candidatas: duplicata pura, vagas irmãs, substituição vs. ampliação, ou sem relação.
- **FR38:** RH pode, sobre cada par suspeito, mesclar (preservando parent_id), relacionar como irmãs, descartar alerta, ou notificar os gestores envolvidos.
- **FR39:** Sistema preserva histórico auditável de toda decisão de mesclagem ou relação, permitindo reverter.
- **FR40:** RH pode configurar thresholds de similaridade por tomador.

### 6. Vagas e Matching

- **FR41:** Requisição aprovada vira vaga ativa, com número de controle e prazo estimado de preenchimento.
- **FR42:** RH pode marcar uma vaga como PcD-preferencial.
- **FR43:** Sistema pode computar matches entre vaga ativa e base de currículos estruturados, combinando regras rígidas (requisitos obrigatórios) e similaridade semântica (desejáveis/diferenciais).
- **FR44:** Sistema pode produzir explicabilidade básica do match ("bateu em X requisitos obrigatórios; teve similaridade Y nos desejáveis").
- **FR45:** RH pode visualizar, filtrar e ordenar candidatos ranqueados para uma vaga.
- **FR46:** RH pode marcar candidato como "avançar em R&S", "não compatível" ou "reserva".
- **FR47:** Sistema pode notificar RH quando um novo currículo ingerido tiver match acima de limiar com uma vaga ativa.

### 7. Painel RH e Operação

- **FR48:** RH pode ver um kanban de requisições por status (em revisão, ativas, em R&S, preenchidas, arquivadas).
- **FR49:** RH pode filtrar requisições/vagas por tomador, período, tipo de gestor e SLA.
- **FR50:** RH pode visualizar SLA contratual próximo do vencimento em destaque.
- **FR51:** RH pode, ao revisar uma requisição, receber sugestão do sistema quando ela for similar a requisições anteriores do mesmo tomador ("copiar template?").
- **FR52:** RH pode exportar relatórios de vagas, requisições e candidatos em formatos abertos (CSV, PDF).

### 8. Providers de IA Plugáveis

- **FR53:** RH administrador pode listar todos os providers de IA configurados, por categoria (OCR/Vision, transcrição de áudio, LLM).
- **FR54:** RH administrador pode adicionar, remover, ativar, desativar e definir provider de fallback em cada categoria, em runtime, sem necessidade de redeploy.
- **FR55:** RH administrador pode atualizar API key de qualquer provider; a chave é armazenada criptografada em repouso.
- **FR56:** Sistema pode validar credencial e saúde de um provider (health check) antes de torná-lo ativo.
- **FR57:** Sistema contabiliza uso local (quantidade, bytes, tokens) por provider e expõe visualmente cota consumida, restante e data de renovação configurável.
- **FR58:** Sistema alerta visualmente quando uso do provider atingir limiar configurável (default 80%).
- **FR59:** Sistema pode trocar automaticamente para o provider de fallback de uma categoria quando o ativo falhar por cota esgotada, erro recorrente ou health check ruim.
- **FR60:** Sistema notifica por e-mail os administradores configurados a cada troca automática de provider, informando provider falho, motivo, provider ativado, timestamp e link ao dashboard.

### 9. Notificações e Comunicação

- **FR61:** Sistema envia notificações transacionais por e-mail (SMTP) para gestor e RH em eventos relevantes (requisição recebida, em revisão, aprovada, rejeitada, match relevante, duplicata detectada).
- **FR62:** RH pode configurar quais eventos disparam notificação e para quais destinatários.
- **FR63:** Usuário pode visualizar histórico das notificações que recebeu dentro do sistema.

### 10. Auditoria, Compliance e Políticas

- **FR64:** Sistema registra em log append-only com hash encadeado toda ação de escrita (criação, alteração, mesclagem, aprovação, configuração), incluindo ator, IP, user-agent e timestamp.
- **FR65:** Sistema oferece comando administrativo para verificar integridade da cadeia de hash do log.
- **FR66:** RH administrador pode exportar trilha de auditoria filtrada por requisição, vaga ou usuário, com campos privilegiados mascarados quando apropriado (pedidos LAI).
- **FR67:** Sistema versiona Termos de Uso e Política de Privacidade; cada versão tem `effective_at`, texto completo e resumo humanizado das mudanças.
- **FR68:** Ao logar após uma nova versão de política, usuário vê modal com resumo em tópicos do que mudou e link ao documento completo; só prossegue após aceitar.
- **FR69:** Sistema registra de forma imutável cada aceite de política (user, versão, resumo mostrado, timestamp, IP, UA).
- **FR70:** Titular de dados pode solicitar, via página dedicada, acesso, correção, anonimização, portabilidade ou revogação de consentimento.
- **FR71:** Sistema pode anonimizar (não excluir) registros de titular ao atender revogação de consentimento, preservando trilha de auditoria.
- **FR72:** Candidato pode ter seu currículo classificado automaticamente com flag de "contém dados sensíveis" (saúde, sindical, foto), ativando criptografia específica.

### 11. Help Contextual e Orientação

- **FR73:** Usuário pode acessar explicação contextual sobre qualquer campo, botão, coluna, status ou métrica visível, via hover (desktop) ou tap (mobile/tablet).
- **FR74:** RH administrador pode editar diretamente o conteúdo de qualquer tooltip, sem redeploy, por interface dedicada.
- **FR75:** Sistema registra cada abertura de tooltip em telemetria UX.
- **FR76:** Usuário pode ver breadcrumb contextual no topo de cada tela indicando onde está na hierarquia.
- **FR77:** Telas de submissão e revisão mostram card "próximos passos" explicando o que acontecerá após a ação.
- **FR78:** Telas em estado vazio mostram explicação educativa sobre o que aparecerá ali e como chegar nesse conteúdo.

### 12. Telemetria e Aprendizado do Sistema

- **FR79:** Sistema captura eventos estruturados de uso (rota, ação, duração, erro) sem conter PII direta (user_id hasheado com salt).
- **FR80:** Sistema armazena telemetria em estrutura particionada por período.
- **FR81:** Sistema pode gerar periodicamente, via LLM, relatório de "oportunidades de melhoria" a partir da telemetria agregada.
- **FR82:** RH administrador pode visualizar relatórios gerados em interface dedicada e marcar insights como "aplicado", "descartado" ou "acompanhar".
- **FR83:** Sistema pode identificar tooltips com alta taxa de abertura, sinalizando labels/campos candidatos a melhoria.

### 13. Configuração e Administração

- **FR84:** RH administrador pode gerenciar tomadores (CRUD), com atributos: razão social, CNPJ/identificador, endereço, contatos, CCT aplicável padrão, SLA contratual padrão.
- **FR85:** RH administrador pode gerenciar a lista de remetentes autorizados da caixa monitorada de currículos.
- **FR86:** RH administrador pode gerenciar a lista de destinatários de notificações automáticas (fallback, incidentes).
- **FR87:** RH administrador pode configurar thresholds do sistema (confiança mínima IA, similaridade de duplicata, uso de cota para alerta).
- **FR88:** Sistema pode ativar ou desativar features específicas via feature flags sem redeploy.
- **FR89:** Sistema pode agendar backup automático diário do banco e do object storage, com verificação periódica de restore testado.

## Non-Functional Requirements

> Nota: p95/p99 são percentis — "p95 = 2s" significa que 95% das operações terminam em 2s ou menos; os 5% mais lentos podem demorar mais. São métricas honestas para SLOs (média esconde outliers).

### Performance

- **NFR1:** Geração e envio do código de link mágico devem completar em ≤ 10s p95 do momento da solicitação.
- **NFR2:** Pipeline multimodal completo (upload válido → rascunho pronto para revisão RH) deve completar em ≤ 3 min p95 e ≤ 8 min p99.
- **NFR3:** Tempo de resposta de qualquer ação síncrona do portal (submit de formulário, navegação) deve ser ≤ 1,5 s p95.
- **NFR4:** Carregamento inicial do portal do gestor em conexão 4G deve ser ≤ 3 s até primeira ação possível (Time to Interactive).
- **NFR5:** Job de ingestão de e-mail deve detectar novo e-mail em ≤ 60 s da chegada na caixa monitorada (via webhook ou IMAP IDLE polling).
- **NFR6:** Busca semântica de duplicatas (pgvector, vizinhos ≥ 0,85) deve retornar em ≤ 500 ms para base de até 10.000 requisições.

### Escalabilidade

- **NFR7:** Sistema deve suportar pico de 10× o volume baseline (20 req/mês → picos de 200 req/mês) sem degradação de latência p95.
- **NFR8:** Base de candidatos/currículos deve escalar para 50.000 registros sem degradar latência de match acima de 2 s p95.
- **NFR9:** Fila de jobs deve absorver rajada de 50 submissões simultâneas sem perder mensagens; processamento pode ser diferido, mas aceitação deve ser imediata.
- **NFR10:** Arquitetura deve permitir escalonamento horizontal de workers Dramatiq sem alterações de código — só adicionando réplicas no Swarm.

### Segurança

- **NFR11:** Toda comunicação HTTP usa TLS 1.3; HTTP é redirecionado para HTTPS; headers HSTS, CSP restritiva, X-Content-Type-Options, X-Frame-Options, Referrer-Policy habilitados.
- **NFR12:** Código do link mágico tem TTL ≤ 15 min, é single-use, e vinculado a IP + User-Agent do solicitante.
- **NFR13:** Cookies de sessão têm atributos `HttpOnly`, `Secure`, `SameSite=Lax`, e são rotacionados em mudança de privilégio.
- **NFR14:** Campos sensíveis (API keys de providers, CPF, CID/laudo, foto) são criptografados em repouso via biblioteca consolidada, com chave mestra fora do banco.
- **NFR15:** Upload valida MIME-type real (não apenas extensão), tem limite de 20 MB por arquivo, e sanitiza nome de arquivo.
- **NFR16:** Sistema rejeita uploads com conteúdo malformado, zip bombs, ou MIME inconsistente com extensão — com resposta clara ao usuário e log de auditoria.
- **NFR17:** MFA por TOTP está disponível para contas administrativas; sua ativação é auditada.
- **NFR18:** Tentativas repetidas de autenticação ou solicitação de link mágico são rate-limited por IP e por e-mail (default: 5 solicitações em 10 min, ajustável).
- **NFR19:** Logs de auditoria são append-only com hash encadeado SHA-256; existe comando administrativo que valida integridade da cadeia inteira.

### Confiabilidade e Disponibilidade

- **NFR20:** Disponibilidade mensal do portal ≥ 99% (equivalente a ≤ 7h de downtime não-planejado).
- **NFR21:** Backup automatizado diário de Postgres + MinIO para storage externo (S3-compatible off-site); retenção mínima 30 dias diários + 6 meses semanais.
- **NFR22:** RPO (Recovery Point Objective) ≤ 24h; RTO (Recovery Time Objective) ≤ 4h.
- **NFR23:** Restore de backup é testado trimestralmente em ambiente isolado; falha no teste é incidente de severidade alta.
- **NFR24:** Jobs da fila são idempotentes — reprocessamento de mensagem duplicada não produz efeitos colaterais adicionais.
- **NFR25:** Sistema degrada graciosamente se um provider de IA estiver indisponível: ativa fallback automático; se ambos falharem, aceita a submissão e coloca em fila de reprocessamento com notificação ao RH.

### Privacidade, LGPD e Compliance

- **NFR26:** Sistema mantém Registro de Operações de Tratamento (ROPA) atualizado por finalidade, com base legal explicitada (LGPD Art. 7º).
- **NFR27:** Dados sensíveis (LGPD Art. 11) têm consentimento específico registrado separadamente do consentimento geral, com `policy_version_id` vinculado.
- **NFR28:** Toda decisão automatizada relevante (match IA, publicação de vaga) é revisável por humano, com log explicável acessível ao titular (LGPD Art. 20).
- **NFR29:** Incidentes de segurança têm runbook documentado que inclui notificação a titulares e ANPD dentro do prazo regulamentar vigente.
- **NFR30:** Logs de aplicação são retidos por no mínimo 6 meses (Marco Civil Art. 15); logs com vínculo a gestor servidor público são retidos por 5 anos ou até decisão DPO diferente.
- **NFR31:** Titular pode exercer direitos LGPD (acesso, correção, portabilidade, anonimização, revogação) através de página dedicada; solicitações são atendidas em até 15 dias corridos.
- **NFR32:** Sistema suporta anonimização (não exclusão) de dados de titular que revogue consentimento, preservando integridade da cadeia de auditoria.
- **NFR33:** Export por pedido LAI mascara automaticamente campos privilegiados (dados de candidatos, informações sensíveis) quando solicitante não tem privilégio para vê-los.

### Custo Operacional

- **NFR34:** Custo médio de IA (tokens LLM + OCR + transcrição) por vaga processada ≤ R$ 0,15 p95.
- **NFR35:** Sistema alerta quando uso de cota de qualquer provider atingir 80% do limite configurado; alerta é também registrado em audit log.
- **NFR36:** Sistema preserva default para providers free-tier (Mistral, Groq) sempre que viáveis; switch para provider pago requer ação explícita do RH ou trigger de fallback automático.

### Observabilidade e Auditabilidade

- **NFR37:** Todos os logs de aplicação são estruturados (JSON) com `trace_id` correlacionando request HTTP → jobs de fila → chamadas a providers externos.
- **NFR38:** Métricas expostas cobrem: latência por etapa do pipeline, taxa de sucesso/falha por provider, tokens consumidos por categoria, tamanho de fila, uptime, uso de cota.
- **NFR39:** Alertas operacionais são enviados ao RH quando fila > 20 jobs por > 5 min, erros de provider > 3× em 10 min, ou uptime diário < 99%.
- **NFR40:** Toda alteração de configuração (providers, thresholds, listas de admins/remetentes, políticas) é registrada no log de auditoria com ator e timestamp.

### Integração

- **NFR41:** Webhooks externos (Google Pub/Sub, Microsoft Graph, Evolution API) são autenticados por segredo compartilhado ou assinatura criptográfica.
- **NFR42:** Integrações externas têm timeout configurado (default 30 s) e retry com backoff exponencial em falhas transitórias.
- **NFR43:** API keys de serviços externos são rotacionáveis pela UI do RH sem redeploy.
- **NFR44:** Changes breaking em providers externos devem ser contornáveis trocando driver do provider — alternativa deve estar sempre configurada.

### Acessibilidade e Usabilidade

- **NFR45:** Portal do gestor é responsivo e funcional em resoluções mobile desde 360 px de largura.
- **NFR46:** Contraste de cores e tamanho de fonte atendem WCAG 2.1 AA como meta do MVP (pequena tolerância a exceções pontuais documentadas).
- **NFR47:** Qualquer campo/botão/status no sistema tem ajuda contextual disponível (tooltip ou equivalente).
- **NFR48:** Gestor pode concluir sua primeira submissão válida em ≤ 2 minutos após autenticar pela primeira vez.
- **NFR49:** Interface é apresentada em Português do Brasil; internacionalização (multi-idioma) é Vision.

### Manutenibilidade e Entrega

- **NFR50:** Deploy em produção é zero-downtime via rolling update do Swarm.
- **NFR51:** Pipeline de CI executa testes unitários, integração e smoke em cada PR; bloqueia merge em falhas.
- **NFR52:** Cobertura de testes ≥ 70% nas camadas críticas (auth, pipeline IA, log append-only, providers, detecção de duplicata).
- **NFR53:** Feature flags permitem ativar/desativar funcionalidades específicas em runtime sem redeploy (ex.: Camada 3 de duplicata, job LLM de telemetria, ingestão por e-mail).
- **NFR54:** Documentação técnica mínima (README, arquitetura, runbook operacional, procedimento de restore) existe e é versionada junto ao código.

## Appendix A — Matriz de Rastreabilidade (Jornada → FR → NFR)

Relaciona cada Jornada do PRD às capacidades (FRs) e aos atributos de qualidade (NFRs) que precisam existir para que a jornada aconteça. Serve de contrato executável para derivação de Épicos.

| Jornada | Capacidades (FRs) | Qualidade (NFRs) |
|---|---|---|
| **J1 — Gestor servidor público submete via áudio (Happy Path)** | FR1–FR6 (auth + cadastro progressivo + tipo_gestor), FR10, FR14, FR16–FR17 (submissão multimodal + notificação), FR25, FR27, FR29–FR33 (pipeline IA + revisão RH), FR61, FR73, FR76 (notificação + help + breadcrumb) | NFR1 (latência link mágico), NFR2 (latência pipeline), NFR3–NFR4 (latência portal), NFR11–NFR13 (segurança auth), NFR26–NFR28 (LGPD bases), NFR45–NFR48 (acessibilidade), NFR47 (help contextual) |
| **J2 — Gestor Edge Case / Ambiguidade** | FR11–FR13 (PDF/imagem/texto), FR28, FR33–FR34 (confiança + ambiguidade), FR31 (edit), FR64 (audit) | NFR2 (latência pipeline), NFR19 (hash-chain), NFR26–NFR33 (privacidade) |
| **J3 — RH revisa diariamente** | FR29–FR32 (revisão), FR35 (reverter), FR41 (aprova vira vaga), FR48–FR52 (painel kanban + export), FR51 (sugestão template similar), FR61–FR62 (notif config), FR64–FR65 (audit) | NFR3 (latência painel), NFR11–NFR19 (segurança RH), NFR37–NFR40 (observabilidade) |
| **J4 — Ingestão de currículo por e-mail encaminhado** | FR19 (upload manual), FR20–FR24 (caixa monitorada + dedup + anti-loop + whitelist), FR43–FR47 (matching + notif), FR61 (notif RH) | NFR5 (latência detecção e-mail), NFR9 (fila absorve rajada), NFR15–NFR16 (upload seguro), NFR24 (idempotência), NFR41–NFR42 (webhooks seguros) |
| **J5 — Troca de provider OCR em runtime** | FR53–FR60 (gestão plugável + cotas + fallback + notif e-mail) | NFR34–NFR36 (custo/cota), NFR40 (audit configuração), NFR43–NFR44 (rotação keys, resiliência provider) |

### Cobertura por área de capacidade

| Área | FRs | Cobre quais jornadas |
|---|---|---|
| 1. Acesso e Identidade | FR1–FR9 | J1, J2, J3 (login) |
| 2. Submissão de Requisição | FR10–FR18 | J1, J2 |
| 3. Ingestão de Currículos | FR19–FR24 | J4 |
| 4. Extração IA e Revisão Humana | FR25–FR35 | J1, J2, J3 |
| 5. Detecção de Duplicatas | FR36–FR40 | Trava para J1, J2 (fluxo lateral) |
| 6. Vagas e Matching | FR41–FR47 | J3, J4 |
| 7. Painel RH e Operação | FR48–FR52 | J3 |
| 8. Providers de IA Plugáveis | FR53–FR60 | J5 + infra de J1-J4 |
| 9. Notificações | FR61–FR63 | J1, J3, J4, J5 |
| 10. Auditoria, Compliance, Políticas | FR64–FR72 | Transversal (todas) |
| 11. Help Contextual | FR73–FR78 | Transversal (todas) |
| 12. Telemetria | FR79–FR83 | Transversal (todas) |
| 13. Configuração e Admin | FR84–FR89 | Pré-requisito operacional |

### Métricas de Sucesso → FRs/NFRs que as habilitam

| Métrica primária | FRs/NFRs habilitadores |
|---|---|
| **T2F (Time to Fill)** ↓ | FR10–FR18 (velocidade submissão), FR27–FR33 (extração acurada), FR43–FR47 (matching rápido), NFR2 (pipeline ≤3min p95) |
| **Requisições perdidas → 0** | FR10–FR24 (canal único + e-mail monitorado), FR20–FR23 (ingestão automática dedup) |
| **Adoção 50%/30d → 80%/60d** | FR4–FR5 (valor primeiro), FR10 (áudio), FR73–FR78 (help reduz fricção), NFR45–NFR48 (mobile + acessibilidade) |
| **Glosa contratual evitada** | FR50 (SLA destacado), FR41 (prazo estimado), NFR20–NFR25 (confiabilidade) |
| **CSAT tomador ≥ 4,0** | Toda J1 + help (FR73–FR78) + notificações (FR61) |
| **Reaproveitamento pool ≥ 30%** | FR20–FR24 (ingestão CV), FR43–FR47 (match) |
| **Custo ≤ R$0,15/vaga** | FR53–FR60 (providers plugáveis free-tier), NFR34–NFR36 |
| **Uptime ≥ 99%** | NFR20–NFR25 (confiabilidade + backup + idempotência) |

### FRs/NFRs não cobertos por nenhuma Jornada narrada

Normais — são infraestruturais ou preparatórios, não aparecem em jornadas de usuário:

- **Configuração inicial:** FR84–FR89 (cadastro de tomadores, listas de remetentes/admins, thresholds, feature flags, backup)
- **Compliance de titular:** FR70–FR72 (direitos LGPD, anonimização, flag sensível) — usados em caso de exercício de direito, sem jornada feliz associada
- **Telemetria/IA-lê-logs:** FR79–FR83 (trabalho contínuo de self-improvement)
- **NFRs operacionais:** NFR7–NFR10 (escalabilidade), NFR50–NFR54 (manutenibilidade/entrega) — propriedades, não jornadas

Estes itens podem virar **Épicos independentes** ("Compliance LGPD — Direitos do Titular", "Operações e DevOps", "Configuração inicial do Tomador").

## Appendix B — Pendências DPO / Jurídico

Não bloqueiam início do desenvolvimento; bloqueiam go-live em produção.

1. **Base legal do match IA** — LIA documentada (legítimo interesse) ou consentimento explícito do candidato? Afeta: FR27 (extração), FR43–FR47 (matching), FR70–FR72 (direitos titular).
2. **Prazo de retenção de currículos não contratados** — default conservador 12 meses; DPO valida. Afeta: NFR30 (retenção), FR20–FR24 (ingestão).
3. **Enquadramento LAI quando gestor é servidor público** — quais campos da requisição são públicos vs. anonimizados em eventual pedido LAI? Afeta: FR66 (export LAI), NFR33 (mascaramento).

## Appendix C — Changelog deste PRD

| Versão | Data | Resumo |
|---|---|---|
| 1.0 | 2026-04-21 | PRD inicial completo (11 steps BMAD + Party Mode Rounds 1-3 + Paige polish). |
