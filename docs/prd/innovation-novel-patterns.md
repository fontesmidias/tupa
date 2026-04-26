# Innovation & Novel Patterns

## Detected Innovation Areas

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

## Market Context & Competitive Landscape

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

## Validation Approach

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

## Risk Mitigation

- "Inovação demais assusta usuário": UI esconde a complexidade (gestor nunca vê "provider de IA" ou "embedding"). Toda a inovação é invisível.
- "LLM alucina em contexto B2G": revisão RH obrigatória + diff visual + campos de baixa confiança destacados + input original sempre disponível.
- "Free tiers podem ser removidos": abstração plugável permite trocar provider sem deploy; audit de custo embutido.
- "Detecção de duplicata falsa positiva mescla coisas diferentes": RH sempre decide (nunca automático); auditoria permite desfazer; `parent_id` é reversível.
- "Tooltips viram lixo de informação se não curados": help_snippets tem owner (RH) + telemetria de uso + job de IA identificando termos sub-explicados.
