# User Journeys

## Jornada 1 — Gestor Demandante (Servidor Público / Tipo B) — Happy Path

**Personagem:** Dra. Marlene Siqueira, 47, coordenadora-substituta numa secretaria de saúde do DF. Duas recepcionistas acabaram de pedir demissão. Segunda-feira, 7h42.

**Abertura:** Abre WhatsApp por reflexo; lembra do portal novo; clica no link do último e-mail.

**Subida:** Tela minimalista pede e-mail. Digita `marlene.siqueira@saude.df.gov.br`. Código de 6 dígitos chega em ≤10s. Cola. Entra direto em "Nova requisição" — não em cadastro. Botão grande "🎙️ Gravar áudio". Grava 90s explicando o posto. Envia. "Recebemos. Volte em 3 min."

**Clímax:** 2 min depois, e-mail com resumo da requisição extraída pela IA. Rascunho correto em 90%. Marca "validar como está". Só então sistema pede confirmação de 3 campos pré-preenchidos (Secretaria / Coordenação / Cargo). Um clique. Nunca preencheu formulário.

**Resolução:** 8h05, café. Requisição submetida, RH ciente, Marlene tranquila. O portal foi mais rápido que WhatsApp seria.

**Capacidades:** link mágico; redirecionamento para "Nova requisição"; upload áudio mobile; pipeline Whisper + Claude; notificação e-mail com resumo; cadastro progressivo pós-submissão; pré-preenchimento por domínio de e-mail (`.gov.br` → servidor público); detecção de CCT aplicável.

## Jornada 2 — Gestor Demandante — Edge Case / Recovery

**Personagem:** Roberto Paiva, 52, diretor administrativo de empresa privada (Tipo C). Manda áudio confuso de 4 min falando de posto vago, reclamando do colaborador anterior e mencionando um contrato diferente. IA identifica ambiguidade.

**Cena:** 3 min depois recebe: "Sua requisição precisa de esclarecimento — a IA identificou 2 possíveis vagas".

**Subida:** Abre e vê dois rascunhos candidatos lado a lado. Botões: "Só a A" / "Só a B" / "Ambas" / "Nenhuma — deixa eu escrever". Clica "Só a B". Campos em amarelo pedem confirmação: piso, escala, experiência. Confirma em 30s.

**Resolução:** requisição salva corretamente. Histórico guarda o áudio, as duas interpretações e a decisão. RH nem precisa envolver-se.

**Capacidades:** detecção de ambiguidade (múltiplos candidatos com score); UI de resolução em 1 tela; marcação visual de baixa confiança; persistência auditável de todas as hipóteses.

## Jornada 3 — RH (Bruno) — Operação diária

**Personagem:** Bruno Fontes, Coord. RH Green House. 9h, 4 requisições pendentes.

**Cena:** Entra no painel. Kanban horizontal: "Em revisão (4)" | "Ativas (7)" | "Em R&S (3)" | "Preenchidas" | "Arquivadas".

**Subida:** Clica na 1ª. Tela com 3 painéis: **esquerda** — inputs originais (áudio com player sincronizado à transcrição; PDF; texto); **centro** — rascunho IA estruturado em campos editáveis; **direita** — ações Aprovar / Esclarecer / Rejeitar. Campos amarelos = baixa confiança. Áudio pula direto para o trecho relevante. Ajusta 1 piso. Aprova. 90 segundos por revisão.

**Clímax:** Card lateral: "Este posto é semelhante a 3 requisições anteriores do mesmo tomador. Reaproveitar template?" Clica "Sim" — campos secundários preenchidos.

**Resolução:** 4 revisões em ~8 min. Gestores notificados. Vagas publicadas. Bruno livre para R&S onde agrega valor humano.

**Capacidades:** kanban por status; visualizador sincronizado multimodal; diff visual; destaque de baixa confiança; reaproveitamento de template por tomador/posto; notificação automática pós-aprovação; histórico auditável.

## Jornada 4 — Ingestão de currículo por e-mail encaminhado — Automática

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

## Jornada 5 — Operação técnica / Troca de provedor OCR

**Personagem:** Bruno como admin técnico.

**Cena:** Alerta: "Mistral Vision atingiu 85% da cota mensal".

**Subida:** Configurações → Provedores OCR/Vision. Tabela: provedor, status, consumido, restante, reset. Clica "Tornar ocr.space o ativo". Sistema valida API key (health check). Salvo. Próximos jobs usarão ocr.space.

**Clímax:** sem deploy. Sem reinicialização. Pode atualizar API key direto na UI (campo criptografado; audit log).

**Resolução:** operação segue. Sem chamar técnico.

**Capacidades:** OcrProvider plugável em runtime; API keys criptografadas; health check; contador local de cota; dashboard comparativo; audit log de configuração.

## Journey Requirements Summary

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
