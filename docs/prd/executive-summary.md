# Executive Summary

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

## What Makes This Special

1. **Ingestão onde o usuário já está.** Não exigimos que o gestor mude de comportamento — só que redirecione o que já faz. Áudio confuso é aceito; print ruim é aceito; PDF feio é aceito. Concorrentes (Gupy, Kenoby, Solides) exigem formulário estruturado na entrada — o que replica a fricção que o gestor hoje evita usando WhatsApp.

2. **Valor primeiro, identidade depois.** O gestor casual clica no link mágico e vai **direto para "Nova requisição"**, não para um formulário de cadastro. Só após submeter — quando já recebeu valor — o sistema pede identificação, pré-preenchida por IA a partir do domínio do e-mail (`.gov.br` → servidor público), assinatura do e-mail encaminhado, e base de tomadores já conhecidos. Gestor confirma com 1 clique em vez de preencher campos.

3. **IA propõe, humano decide.** Não é "ATS que rankeia e decide"; é "assistente que elimina retrabalho do RH". Isso destrava adesão de duas pontas: o gestor não se sente auditado, e o RH não se sente substituído. Legalmente blindado por LGPD Art. 20.

4. **Memória institucional por tomador.** Cada requisição enriquece templates por posto/tomador, mapeia peculiaridades recorrentes do gestor e alimenta o talent pool. A 10ª requisição de "Apoio Administrativo I" para a mesma secretaria tende a 1 clique.

5. **Contexto B2G nativo.** Sistema entende Termo de Referência, hierarquia obrigatório/desejável/diferencial, CCT aplicável (ex.: SEAC-DF), pisos salariais, Lei de Cotas — nenhum ATS de mercado cobre isso sem customização cara.

6. **Compliance espinhal.** Log append-only com hash encadeado (atende Marco Civil + LAI + LGPD + TCU/CGU), consentimento granular (Art. 11), base legal por finalidade (Art. 7º), trilha LAI ativada automaticamente quando o gestor é servidor público.

**Core Insight:** LLMs multimodais em 2026 são suficientemente confiáveis para extração estruturada de áudio + imagem + PDF com um único prompt e schema JSON. Combinados com revisão humana rápida do RH, o erro residual é tolerável para o contexto de Staffing B2G. Há três anos isso era pesquisa; hoje é commodity. Esta é a janela.

**Frase-valor:** *Receba, organize e preencha vagas mais rápido: o gestor fala (como preferir), a IA estrutura, o RH valida, a Green House cumpre SLA.*

## Diagrama de Contexto (C4 Nível 1)

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
