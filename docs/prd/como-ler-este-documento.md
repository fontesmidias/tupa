# Como ler este documento

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

## Terminologia canônica

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
