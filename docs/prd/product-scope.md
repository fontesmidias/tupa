# Product Scope

## MVP — Minimum Viable Product (Fatia 1)

**Objetivo:** validar "ingestão informal + IA + revisão RH resolve requisições perdidas e melhora T2F" E preparar o sistema para crescimento surpresa com telemetria e análise de UX ativas desde o dia 1.

- Portal web mobile-first para gestor
- Link mágico (e-mail → código TTL 15min single-use bound IP/UA) + cadastro "valor primeiro" com pré-preenchimento IA (domínio e-mail, assinatura, base de tomadores)
- Nova requisição aceitando: formulário estruturado + upload de áudio + PDF + texto colado + imagem/print (OCR via provedor plugável)
- Pipeline IA: Whisper (áudio) + pdfplumber (PDF texto) + OcrProvider plugável (Mistral default, ocr.space fallback) + Claude extraction (JSON schema) para requisitos
- Dashboard de provedores OCR/Vision: cota consumida/restante (contador local), data de reset, troca de provedor ativo, troca de API key criptografada, alerta em 80% de cota
- Revisão RH com UI dedicada (não Django Admin puro): diff visual rascunho IA vs. campos estruturados, aprovação/edição
- Publicação da vaga
- Ingestão de currículos: caixa de e-mail monitorada + upload manual RH; extração IA + armazenamento do binário original
- Match básico — algoritmo híbrido (regras rígidas em obrigatórios + embeddings pgvector nos desejáveis/diferenciais)
- Notificações e-mail (SMTP) para gestor e RH
- Log append-only hash-encadeado (LGPD + Marco Civil + LAI)
- Painel RH: fila de revisão, vagas ativas, candidatos, SLA próximo do vencimento
- "Minhas vagas" + "vagas da minha área" (rótulo amigável, nunca "círculo" na UI)
- Telemetria UX estruturada + job LLM semanal + dashboard /admin/ux-insights (completo no MVP, decisão consciente de Bruno)
- Consentimento granular, política de privacidade versionada, canal dpo@
- Compliance-checklist mínimo de go-live (ROPA, runbook incidente, 3 decisões DPO)

**Fora do MVP (explícito):** Word, WhatsApp Evolution API, portal do candidato, cotas PcD monitoradas, integração eSocial, análise de disparate impact.

## Growth Features (Post-MVP)

- Parsing de Word
- WhatsApp via Evolution API (notificações bidirecionais)
- Templates de posto por tomador (memória institucional explícita)
- Relatório de SLA contratual por tomador
- Dashboard analítico do gestor (além da submissão)
- Métricas de disparate impact no match (viés algorítmico)
- Monitoramento de cotas PcD (Lei 8.213/91 Art. 93)
- Provedores adicionais de OCR/Vision (Claude, GPT-4o, Google Vision, Tesseract local)

## Vision (Future)

- Portal do candidato self-service
- Integração Gov.br, SINE, Secretaria DIP
- Export estruturado eSocial S-2200
- Compliance automatizado (revisão anual, renovação consentimentos, purga por retenção)
- Multi-idioma / acessibilidade AA
