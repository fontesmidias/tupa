# Non-Functional Requirements

> Nota: p95/p99 são percentis — "p95 = 2s" significa que 95% das operações terminam em 2s ou menos; os 5% mais lentos podem demorar mais. São métricas honestas para SLOs (média esconde outliers).

## Performance

- **NFR1:** Geração e envio do código de link mágico devem completar em ≤ 10s p95 do momento da solicitação.
- **NFR2:** Pipeline multimodal completo (upload válido → rascunho pronto para revisão RH) deve completar em ≤ 3 min p95 e ≤ 8 min p99.
- **NFR3:** Tempo de resposta de qualquer ação síncrona do portal (submit de formulário, navegação) deve ser ≤ 1,5 s p95.
- **NFR4:** Carregamento inicial do portal do gestor em conexão 4G deve ser ≤ 3 s até primeira ação possível (Time to Interactive).
- **NFR5:** Job de ingestão de e-mail deve detectar novo e-mail em ≤ 60 s da chegada na caixa monitorada (via webhook ou IMAP IDLE polling).
- **NFR6:** Busca semântica de duplicatas (pgvector, vizinhos ≥ 0,85) deve retornar em ≤ 500 ms para base de até 10.000 requisições.

## Escalabilidade

- **NFR7:** Sistema deve suportar pico de 10× o volume baseline (20 req/mês → picos de 200 req/mês) sem degradação de latência p95.
- **NFR8:** Base de candidatos/currículos deve escalar para 50.000 registros sem degradar latência de match acima de 2 s p95.
- **NFR9:** Fila de jobs deve absorver rajada de 50 submissões simultâneas sem perder mensagens; processamento pode ser diferido, mas aceitação deve ser imediata.
- **NFR10:** Arquitetura deve permitir escalonamento horizontal de workers Dramatiq sem alterações de código — só adicionando réplicas no Swarm.

## Segurança

- **NFR11:** Toda comunicação HTTP usa TLS 1.3; HTTP é redirecionado para HTTPS; headers HSTS, CSP restritiva, X-Content-Type-Options, X-Frame-Options, Referrer-Policy habilitados.
- **NFR12:** Código do link mágico tem TTL ≤ 15 min, é single-use, e vinculado a IP + User-Agent do solicitante.
- **NFR13:** Cookies de sessão têm atributos `HttpOnly`, `Secure`, `SameSite=Lax`, e são rotacionados em mudança de privilégio.
- **NFR14:** Campos sensíveis (API keys de providers, CPF, CID/laudo, foto) são criptografados em repouso via biblioteca consolidada, com chave mestra fora do banco.
- **NFR15:** Upload valida MIME-type real (não apenas extensão), tem limite de 20 MB por arquivo, e sanitiza nome de arquivo.
- **NFR16:** Sistema rejeita uploads com conteúdo malformado, zip bombs, ou MIME inconsistente com extensão — com resposta clara ao usuário e log de auditoria.
- **NFR17:** MFA por TOTP está disponível para contas administrativas; sua ativação é auditada.
- **NFR18:** Tentativas repetidas de autenticação ou solicitação de link mágico são rate-limited por IP e por e-mail (default: 5 solicitações em 10 min, ajustável).
- **NFR19:** Logs de auditoria são append-only com hash encadeado SHA-256; existe comando administrativo que valida integridade da cadeia inteira.

## Confiabilidade e Disponibilidade

- **NFR20:** Disponibilidade mensal do portal ≥ 99% (equivalente a ≤ 7h de downtime não-planejado).
- **NFR21:** Backup automatizado diário de Postgres + MinIO para storage externo (S3-compatible off-site); retenção mínima 30 dias diários + 6 meses semanais.
- **NFR22:** RPO (Recovery Point Objective) ≤ 24h; RTO (Recovery Time Objective) ≤ 4h.
- **NFR23:** Restore de backup é testado trimestralmente em ambiente isolado; falha no teste é incidente de severidade alta.
- **NFR24:** Jobs da fila são idempotentes — reprocessamento de mensagem duplicada não produz efeitos colaterais adicionais.
- **NFR25:** Sistema degrada graciosamente se um provider de IA estiver indisponível: ativa fallback automático; se ambos falharem, aceita a submissão e coloca em fila de reprocessamento com notificação ao RH.

## Privacidade, LGPD e Compliance

- **NFR26:** Sistema mantém Registro de Operações de Tratamento (ROPA) atualizado por finalidade, com base legal explicitada (LGPD Art. 7º).
- **NFR27:** Dados sensíveis (LGPD Art. 11) têm consentimento específico registrado separadamente do consentimento geral, com `policy_version_id` vinculado.
- **NFR28:** Toda decisão automatizada relevante (match IA, publicação de vaga) é revisável por humano, com log explicável acessível ao titular (LGPD Art. 20).
- **NFR29:** Incidentes de segurança têm runbook documentado que inclui notificação a titulares e ANPD dentro do prazo regulamentar vigente.
- **NFR30:** Logs de aplicação são retidos por no mínimo 6 meses (Marco Civil Art. 15); logs com vínculo a gestor servidor público são retidos por 5 anos ou até decisão DPO diferente.
- **NFR31:** Titular pode exercer direitos LGPD (acesso, correção, portabilidade, anonimização, revogação) através de página dedicada; solicitações são atendidas em até 15 dias corridos.
- **NFR32:** Sistema suporta anonimização (não exclusão) de dados de titular que revogue consentimento, preservando integridade da cadeia de auditoria.
- **NFR33:** Export por pedido LAI mascara automaticamente campos privilegiados (dados de candidatos, informações sensíveis) quando solicitante não tem privilégio para vê-los.

## Custo Operacional

- **NFR34:** Custo médio de IA (tokens LLM + OCR + transcrição) por vaga processada ≤ R$ 0,15 p95.
- **NFR35:** Sistema alerta quando uso de cota de qualquer provider atingir 80% do limite configurado; alerta é também registrado em audit log.
- **NFR36:** Sistema preserva default para providers free-tier (Mistral, Groq) sempre que viáveis; switch para provider pago requer ação explícita do RH ou trigger de fallback automático.

## Observabilidade e Auditabilidade

- **NFR37:** Todos os logs de aplicação são estruturados (JSON) com `trace_id` correlacionando request HTTP → jobs de fila → chamadas a providers externos.
- **NFR38:** Métricas expostas cobrem: latência por etapa do pipeline, taxa de sucesso/falha por provider, tokens consumidos por categoria, tamanho de fila, uptime, uso de cota.
- **NFR39:** Alertas operacionais são enviados ao RH quando fila > 20 jobs por > 5 min, erros de provider > 3× em 10 min, ou uptime diário < 99%.
- **NFR40:** Toda alteração de configuração (providers, thresholds, listas de admins/remetentes, políticas) é registrada no log de auditoria com ator e timestamp.

## Integração

- **NFR41:** Webhooks externos (Google Pub/Sub, Microsoft Graph, Evolution API) são autenticados por segredo compartilhado ou assinatura criptográfica.
- **NFR42:** Integrações externas têm timeout configurado (default 30 s) e retry com backoff exponencial em falhas transitórias.
- **NFR43:** API keys de serviços externos são rotacionáveis pela UI do RH sem redeploy.
- **NFR44:** Changes breaking em providers externos devem ser contornáveis trocando driver do provider — alternativa deve estar sempre configurada.

## Acessibilidade e Usabilidade

- **NFR45:** Portal do gestor é responsivo e funcional em resoluções mobile desde 360 px de largura.
- **NFR46:** Contraste de cores e tamanho de fonte atendem WCAG 2.1 AA como meta do MVP (pequena tolerância a exceções pontuais documentadas).
- **NFR47:** Qualquer campo/botão/status no sistema tem ajuda contextual disponível (tooltip ou equivalente).
- **NFR48:** Gestor pode concluir sua primeira submissão válida em ≤ 2 minutos após autenticar pela primeira vez.
- **NFR49:** Interface é apresentada em Português do Brasil; internacionalização (multi-idioma) é Vision.

## Manutenibilidade e Entrega

- **NFR50:** Deploy em produção é zero-downtime via rolling update do Swarm.
- **NFR51:** Pipeline de CI executa testes unitários, integração e smoke em cada PR; bloqueia merge em falhas.
- **NFR52:** Cobertura de testes ≥ 70% nas camadas críticas (auth, pipeline IA, log append-only, providers, detecção de duplicata).
- **NFR53:** Feature flags permitem ativar/desativar funcionalidades específicas em runtime sem redeploy (ex.: Camada 3 de duplicata, job LLM de telemetria, ingestão por e-mail).
- **NFR54:** Documentação técnica mínima (README, arquitetura, runbook operacional, procedimento de restore) existe e é versionada junto ao código.
