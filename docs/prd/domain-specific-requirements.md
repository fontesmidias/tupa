# Domain-Specific Requirements

## Compliance & Regulatório

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

## Constraints Técnicos

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

## Integration Requirements

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

## Risk Mitigations

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

## Decisões pendentes para DPO / Jurídico

Não bloqueiam início do desenvolvimento; bloqueiam go-live em produção.

1. **Base legal do match IA** — LIA documentada (legítimo interesse) ou consentimento explícito do candidato?
2. **Prazo de retenção de currículos não contratados** — default conservador 12 meses; DPO valida.
3. **Enquadramento LAI quando gestor é servidor público** — quais campos da requisição são públicos vs. anonimizados em eventual pedido LAI?
