# Appendix A — Matriz de Rastreabilidade (Jornada → FR → NFR)

Relaciona cada Jornada do PRD às capacidades (FRs) e aos atributos de qualidade (NFRs) que precisam existir para que a jornada aconteça. Serve de contrato executável para derivação de Épicos.

| Jornada | Capacidades (FRs) | Qualidade (NFRs) |
|---|---|---|
| **J1 — Gestor servidor público submete via áudio (Happy Path)** | FR1–FR6 (auth + cadastro progressivo + tipo_gestor), FR10, FR14, FR16–FR17 (submissão multimodal + notificação), FR25, FR27, FR29–FR33 (pipeline IA + revisão RH), FR61, FR73, FR76 (notificação + help + breadcrumb) | NFR1 (latência link mágico), NFR2 (latência pipeline), NFR3–NFR4 (latência portal), NFR11–NFR13 (segurança auth), NFR26–NFR28 (LGPD bases), NFR45–NFR48 (acessibilidade), NFR47 (help contextual) |
| **J2 — Gestor Edge Case / Ambiguidade** | FR11–FR13 (PDF/imagem/texto), FR28, FR33–FR34 (confiança + ambiguidade), FR31 (edit), FR64 (audit) | NFR2 (latência pipeline), NFR19 (hash-chain), NFR26–NFR33 (privacidade) |
| **J3 — RH revisa diariamente** | FR29–FR32 (revisão), FR35 (reverter), FR41 (aprova vira vaga), FR48–FR52 (painel kanban + export), FR51 (sugestão template similar), FR61–FR62 (notif config), FR64–FR65 (audit) | NFR3 (latência painel), NFR11–NFR19 (segurança RH), NFR37–NFR40 (observabilidade) |
| **J4 — Ingestão de currículo por e-mail encaminhado** | FR19 (upload manual), FR20–FR24 (caixa monitorada + dedup + anti-loop + whitelist), FR43–FR47 (matching + notif), FR61 (notif RH) | NFR5 (latência detecção e-mail), NFR9 (fila absorve rajada), NFR15–NFR16 (upload seguro), NFR24 (idempotência), NFR41–NFR42 (webhooks seguros) |
| **J5 — Troca de provider OCR em runtime** | FR53–FR60 (gestão plugável + cotas + fallback + notif e-mail) | NFR34–NFR36 (custo/cota), NFR40 (audit configuração), NFR43–NFR44 (rotação keys, resiliência provider) |

## Cobertura por área de capacidade

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

## Métricas de Sucesso → FRs/NFRs que as habilitam

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

## FRs/NFRs não cobertos por nenhuma Jornada narrada

Normais — são infraestruturais ou preparatórios, não aparecem em jornadas de usuário:

- **Configuração inicial:** FR84–FR89 (cadastro de tomadores, listas de remetentes/admins, thresholds, feature flags, backup)
- **Compliance de titular:** FR70–FR72 (direitos LGPD, anonimização, flag sensível) — usados em caso de exercício de direito, sem jornada feliz associada
- **Telemetria/IA-lê-logs:** FR79–FR83 (trabalho contínuo de self-improvement)
- **NFRs operacionais:** NFR7–NFR10 (escalabilidade), NFR50–NFR54 (manutenibilidade/entrega) — propriedades, não jornadas

Estes itens podem virar **Épicos independentes** ("Compliance LGPD — Direitos do Titular", "Operações e DevOps", "Configuração inicial do Tomador").
