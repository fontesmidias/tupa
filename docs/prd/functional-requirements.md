# Functional Requirements

## 1. Acesso e Identidade

- **FR1:** Usuário pode solicitar acesso digitando apenas seu e-mail; recebe código de uso único por e-mail.
- **FR2:** Usuário pode autenticar-se usando o código recebido dentro de uma janela de validade; o código torna-se inválido após uso ou expiração.
- **FR3:** Sistema pode invalidar automaticamente um código se detectar tentativa de uso de IP ou dispositivo diferente do que solicitou.
- **FR4:** Usuário pode completar seu cadastro após submeter sua primeira ação de valor (cadastro progressivo "valor primeiro").
- **FR5:** Sistema pode pré-preencher campos do cadastro a partir de sinais disponíveis (domínio do e-mail, assinatura de e-mail encaminhado, base de tomadores conhecidos, conteúdo da própria submissão).
- **FR6:** Sistema pode classificar automaticamente o `tipo_gestor` (servidor público, Green House ou empresa privada cliente) a partir do domínio do e-mail.
- **FR7:** Conta RH administrativa pode habilitar autenticação adicional (MFA por TOTP) para a própria conta.
- **FR8:** RH administrador pode atribuir/alterar manualmente o círculo de visibilidade (órgão, departamento, coordenação) de qualquer gestor.
- **FR9:** Usuário pode encerrar sua sessão ativa a qualquer momento, invalidando o cookie.

## 2. Submissão de Requisição de Pessoal

- **FR10:** Gestor pode submeter uma requisição de pessoal gravando áudio diretamente no navegador (desktop ou mobile).
- **FR11:** Gestor pode submeter uma requisição anexando arquivo PDF (nativo ou escaneado).
- **FR12:** Gestor pode submeter uma requisição anexando imagens (JPG/PNG), incluindo prints de conversas.
- **FR13:** Gestor pode submeter uma requisição colando texto em campo livre.
- **FR14:** Gestor pode combinar múltiplos tipos de entrada na mesma requisição (ex.: áudio + PDF).
- **FR15:** Sistema rejeita arquivos que excedam o limite de tamanho ou cujo MIME-type real não corresponda aos formatos suportados, informando o motivo ao gestor.
- **FR16:** Gestor pode acompanhar o status da sua requisição (recebida, em extração IA, em revisão RH, aprovada, rejeitada) via portal e por notificação externa.
- **FR17:** Gestor pode receber resumo em linguagem natural do que o sistema entendeu da sua submissão, via e-mail, em até alguns minutos após enviar.
- **FR18:** Gestor pode editar/reenviar uma requisição rejeitada pelo RH; histórico é preservado.

## 3. Ingestão de Currículos

- **FR19:** RH pode fazer upload manual de currículos (PDF/Word) individuais ou em lote.
- **FR20:** Sistema pode ingerir automaticamente currículos recebidos em uma caixa de e-mail monitorada, extraindo anexos, lendo corpo do e-mail e salvando binário original.
- **FR21:** Sistema rejeita ingestão de e-mails não originários de remetentes em lista autorizada, ou coloca-os em fila de quarentena para decisão do RH.
- **FR22:** Sistema pode deduplicar candidatos recém-ingeridos contra a base existente, usando múltiplas chaves (CPF, e-mail+telefone, nome+telefone).
- **FR23:** Sistema pode detectar e ignorar reingestões do mesmo e-mail/anexo já processado (anti-loop).
- **FR24:** RH pode visualizar todos os currículos ingeridos, com origem identificada (upload manual ou e-mail monitorado).

## 4. Extração IA e Revisão Humana

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

## 5. Detecção de Duplicatas e Correlações

- **FR36:** Sistema pode identificar requisições candidatas a duplicata usando (a) hash de anexo, (b) headers de e-mail, (c) fingerprint estruturado (tomador, posto, cidade, data) e (d) similaridade semântica por embeddings.
- **FR37:** Sistema pode produzir um veredito explicativo (via LLM) sobre a relação entre duas requisições candidatas: duplicata pura, vagas irmãs, substituição vs. ampliação, ou sem relação.
- **FR38:** RH pode, sobre cada par suspeito, mesclar (preservando parent_id), relacionar como irmãs, descartar alerta, ou notificar os gestores envolvidos.
- **FR39:** Sistema preserva histórico auditável de toda decisão de mesclagem ou relação, permitindo reverter.
- **FR40:** RH pode configurar thresholds de similaridade por tomador.

## 6. Vagas e Matching

- **FR41:** Requisição aprovada vira vaga ativa, com número de controle e prazo estimado de preenchimento.
- **FR42:** RH pode marcar uma vaga como PcD-preferencial.
- **FR43:** Sistema pode computar matches entre vaga ativa e base de currículos estruturados, combinando regras rígidas (requisitos obrigatórios) e similaridade semântica (desejáveis/diferenciais).
- **FR44:** Sistema pode produzir explicabilidade básica do match ("bateu em X requisitos obrigatórios; teve similaridade Y nos desejáveis").
- **FR45:** RH pode visualizar, filtrar e ordenar candidatos ranqueados para uma vaga.
- **FR46:** RH pode marcar candidato como "avançar em R&S", "não compatível" ou "reserva".
- **FR47:** Sistema pode notificar RH quando um novo currículo ingerido tiver match acima de limiar com uma vaga ativa.

## 7. Painel RH e Operação

- **FR48:** RH pode ver um kanban de requisições por status (em revisão, ativas, em R&S, preenchidas, arquivadas).
- **FR49:** RH pode filtrar requisições/vagas por tomador, período, tipo de gestor e SLA.
- **FR50:** RH pode visualizar SLA contratual próximo do vencimento em destaque.
- **FR51:** RH pode, ao revisar uma requisição, receber sugestão do sistema quando ela for similar a requisições anteriores do mesmo tomador ("copiar template?").
- **FR52:** RH pode exportar relatórios de vagas, requisições e candidatos em formatos abertos (CSV, PDF).

## 8. Providers de IA Plugáveis

- **FR53:** RH administrador pode listar todos os providers de IA configurados, por categoria (OCR/Vision, transcrição de áudio, LLM).
- **FR54:** RH administrador pode adicionar, remover, ativar, desativar e definir provider de fallback em cada categoria, em runtime, sem necessidade de redeploy.
- **FR55:** RH administrador pode atualizar API key de qualquer provider; a chave é armazenada criptografada em repouso.
- **FR56:** Sistema pode validar credencial e saúde de um provider (health check) antes de torná-lo ativo.
- **FR57:** Sistema contabiliza uso local (quantidade, bytes, tokens) por provider e expõe visualmente cota consumida, restante e data de renovação configurável.
- **FR58:** Sistema alerta visualmente quando uso do provider atingir limiar configurável (default 80%).
- **FR59:** Sistema pode trocar automaticamente para o provider de fallback de uma categoria quando o ativo falhar por cota esgotada, erro recorrente ou health check ruim.
- **FR60:** Sistema notifica por e-mail os administradores configurados a cada troca automática de provider, informando provider falho, motivo, provider ativado, timestamp e link ao dashboard.

## 9. Notificações e Comunicação

- **FR61:** Sistema envia notificações transacionais por e-mail (SMTP) para gestor e RH em eventos relevantes (requisição recebida, em revisão, aprovada, rejeitada, match relevante, duplicata detectada).
- **FR62:** RH pode configurar quais eventos disparam notificação e para quais destinatários.
- **FR63:** Usuário pode visualizar histórico das notificações que recebeu dentro do sistema.

## 10. Auditoria, Compliance e Políticas

- **FR64:** Sistema registra em log append-only com hash encadeado toda ação de escrita (criação, alteração, mesclagem, aprovação, configuração), incluindo ator, IP, user-agent e timestamp.
- **FR65:** Sistema oferece comando administrativo para verificar integridade da cadeia de hash do log.
- **FR66:** RH administrador pode exportar trilha de auditoria filtrada por requisição, vaga ou usuário, com campos privilegiados mascarados quando apropriado (pedidos LAI).
- **FR67:** Sistema versiona Termos de Uso e Política de Privacidade; cada versão tem `effective_at`, texto completo e resumo humanizado das mudanças.
- **FR68:** Ao logar após uma nova versão de política, usuário vê modal com resumo em tópicos do que mudou e link ao documento completo; só prossegue após aceitar.
- **FR69:** Sistema registra de forma imutável cada aceite de política (user, versão, resumo mostrado, timestamp, IP, UA).
- **FR70:** Titular de dados pode solicitar, via página dedicada, acesso, correção, anonimização, portabilidade ou revogação de consentimento.
- **FR71:** Sistema pode anonimizar (não excluir) registros de titular ao atender revogação de consentimento, preservando trilha de auditoria.
- **FR72:** Candidato pode ter seu currículo classificado automaticamente com flag de "contém dados sensíveis" (saúde, sindical, foto), ativando criptografia específica.

## 11. Help Contextual e Orientação

- **FR73:** Usuário pode acessar explicação contextual sobre qualquer campo, botão, coluna, status ou métrica visível, via hover (desktop) ou tap (mobile/tablet).
- **FR74:** RH administrador pode editar diretamente o conteúdo de qualquer tooltip, sem redeploy, por interface dedicada.
- **FR75:** Sistema registra cada abertura de tooltip em telemetria UX.
- **FR76:** Usuário pode ver breadcrumb contextual no topo de cada tela indicando onde está na hierarquia.
- **FR77:** Telas de submissão e revisão mostram card "próximos passos" explicando o que acontecerá após a ação.
- **FR78:** Telas em estado vazio mostram explicação educativa sobre o que aparecerá ali e como chegar nesse conteúdo.

## 12. Telemetria e Aprendizado do Sistema

- **FR79:** Sistema captura eventos estruturados de uso (rota, ação, duração, erro) sem conter PII direta (user_id hasheado com salt).
- **FR80:** Sistema armazena telemetria em estrutura particionada por período.
- **FR81:** Sistema pode gerar periodicamente, via LLM, relatório de "oportunidades de melhoria" a partir da telemetria agregada.
- **FR82:** RH administrador pode visualizar relatórios gerados em interface dedicada e marcar insights como "aplicado", "descartado" ou "acompanhar".
- **FR83:** Sistema pode identificar tooltips com alta taxa de abertura, sinalizando labels/campos candidatos a melhoria.

## 13. Configuração e Administração

- **FR84:** RH administrador pode gerenciar tomadores (CRUD), com atributos: razão social, CNPJ/identificador, endereço, contatos, CCT aplicável padrão, SLA contratual padrão.
- **FR85:** RH administrador pode gerenciar a lista de remetentes autorizados da caixa monitorada de currículos.
- **FR86:** RH administrador pode gerenciar a lista de destinatários de notificações automáticas (fallback, incidentes).
- **FR87:** RH administrador pode configurar thresholds do sistema (confiança mínima IA, similaridade de duplicata, uso de cota para alerta).
- **FR88:** Sistema pode ativar ou desativar features específicas via feature flags sem redeploy.
- **FR89:** Sistema pode agendar backup automático diário do banco e do object storage, com verificação periódica de restore testado.
