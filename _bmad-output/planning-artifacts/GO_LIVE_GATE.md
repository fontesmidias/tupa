# 🚦 GO-LIVE GATE — gestao-vagas

Checklist que deve estar 100% verde antes de qualquer promoção para produção.
Origem: Party Mode 2026-04-21 (Mary + Amelia + Winston + John) — rota A.

## Como executar

```bash
python manage.py check --deploy --fail-level ERROR
python manage.py verify_audit_chain
python -m pytest
```

Nenhum ERROR pode emergir. Warnings devem estar justificados por ADR.

---

## 1. Segurança e criptografia

- [ ] `FIELD_ENCRYPTION_KEY` configurada em `.env` de prod (Fernet key, 32 bytes base64 urlsafe). Verificado via `accounts.E002`.
- [ ] `SECRET_KEY` rotacionada — valor de dev nunca vai a prod.
- [ ] `DEBUG=False` + `ALLOWED_HOSTS` explícito (sem `*`).
- [ ] HTTPS obrigatório: `SESSION_COOKIE_SECURE=True`, `CSRF_COOKIE_SECURE=True` (já defaults em `base.py`).

## 2. LGPD e compliance

- [ ] `DPO_EMAIL` configurado (inbox monitorada). Verificado via `accounts.E001`.
- [ ] 3 decisões DPO ratificadas (PRD Appendix B):
  - [ ] (a) Retenção de CVs não contratados — prazo e política de expurgo
  - [ ] (b) Base legal match IA (LIA formal ou consentimento)
  - [ ] (c) Mascaramento LAI para gestor servidor público
- [ ] `apps/policies/legal_basis.py` atualizado com decisões acima (data-as-code).
- [ ] Política de privacidade e Termos publicados em `PolicyVersion` com `effective_at` <= now.
- [ ] Caixa `curriculos@greenhousedf.com.br` configurada (ou bloqueada até Epic 7).
- [ ] Auto-responder informando SLA 15 dias para pedidos LGPD fora do self-service.
- [ ] `LgpdRequest` model implementado para pedidos off-system (backlog pós-3.6b).

## 3. Auditoria

- [ ] `verify_audit_chain` agendado como cron diário + alerta em failure.
- [ ] Backup de `audit_log` com retenção >= 5 anos (requisito de auditoria).
- [ ] Monitoramento de `dpo.notify.failed` e `dpo.notify.skipped` no chain.

## 4. Infraestrutura

- [ ] Subdomínio VPS apontado (Traefik + Let's Encrypt).
- [ ] Postgres com `pgvector` habilitado + backup diário.
- [ ] Redis 7 rodando + persistência configurada.
- [ ] PM2 com processos `gv-web`, `gv-worker`, `gv-email-ingestion` (ADR-004).
- [ ] Logs centralizados (stdout → journald ou agregador).
- [ ] Métricas `/metrics` expostas, scraping configurado.

## 5. Dados e integrações

- [ ] Lista de tomadores reais importada + `dominio_email` preenchido.
- [ ] API keys providers IA (Mistral, Groq, ocr.space, Claude) em `.env` de prod.
- [ ] Credenciais IMAP da caixa de CVs (Epic 7).

## 6. Testes e qualidade

- [ ] Suíte 100% verde em CI (target: >= 315 testes).
- [ ] `manage.py check --deploy` zero errors.
- [ ] `mypy --strict` zero errors.
- [ ] Smoke-test manual pós-deploy: login, anonimização, export, verify_audit_chain.

---

## Itens declaradamente FORA do gate (entram em releases futuras)

- Epic 4+ (providers IA plugáveis) — gate próprio quando codado.
- Epic 7+ (ingestão IMAP) — gate próprio.
- Rotação automática de `FIELD_ENCRYPTION_KEY` — exige restart, documentado como operação manual até N > X tomadores ativos.

---

Última atualização: 2026-04-21 (pós-Party Mode Rota A).
