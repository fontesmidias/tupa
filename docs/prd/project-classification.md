# Project Classification

- **Project Type:** Web Application interna (portal do gestor + painel administrativo do RH) + workers assíncronos (fila de jobs de IA) + serviço de ingestão de e-mail monitorado.
- **Domain:** Staffing / Body Shop B2G — subdomínio HR Tech com camada de Public Procurement (Termo de Referência, Lei de Cotas, eSocial na interface, CCT de asseio/conservação quando aplicável).
- **Domain Complexity:** **Alta** — pela combinação de (1) requisitos regulatórios densos (LGPD Arts. 7/11/20, Marco Civil, LAI, Lei 8.213, ANPD Res. 15/2024); (2) risco de discriminação algorítmica no match IA; (3) três perfis distintos de gestor (servidor público, Green House, privado) com regras de visibilidade e auditoria distintas; (4) integração multimodal com LLM e validação humana. Arquitetura em si é de complexidade média (CRUD + fila + LLM); a complexidade vem do domínio.
- **Project Context:** Greenfield — sem código legado, sem sistema a migrar; a solução atual é manual (PDF por e-mail, WhatsApp, telefonema).
- **Compliance Requirements:** LGPD · Marco Civil da Internet · Lei 8.213/91 (Cotas PcD) · Lei 12.527/11 (LAI, condicional) · ANPD Res. CD/ANPD 15/2024 · CCT Asseio e Conservação (SEAC-DF) quando aplicável · eSocial (interface, Fase 2).
