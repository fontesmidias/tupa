# Prompt Claude Cowork — Rodada 2 (RPs originais)

Cole o bloco abaixo inteiro na sessão do Claude Cowork (com Chrome logado em `bruno.fontes@greenhousedf.com.br`).

---

```
# TAREFA — COLETAR 14 REQUISIÇÕES DE PESSOAL (RPs) ORIGINAIS DO OUTLOOK — RODADA 2

## Contexto

Esta é a **rodada 2** da coleta de corpus para validação de extração LLM em RPs da Green House. Na rodada 1 você entregou 6 RPs em `C:\Users\cery0\projetos\gestao-vagas\_bmad-output\h1-corpus\` — mas com 2 problemas:

1. O caminho foi `gestao-vagas_bmad-output` (sem o separador correto) — já foi manualmente corrigido para `gestao-vagas\_bmad-output`.
2. Você **gerou PDFs sintéticos via ReportLab** a partir dos dados extraídos. Isso **invalida o experimento** — o objetivo é testar se o LLM lê RPs reais sujas, não documentos que você já pré-processou.

## Objetivo desta rodada

Coletar **14 RPs adicionais como PDFs ORIGINAIS** (não gerados). O que significa:

- **Emails com anexo PDF de RP:** baixar o PDF do anexo diretamente.
- **Emails cujo RP está no corpo:** usar "Imprimir → Salvar como PDF" do navegador (Ctrl+P no Outlook Web → Destino: Microsoft Print to PDF / Salvar como PDF). O objetivo é preservar a formatação visual do email como ele chegou.
- **Ofícios escaneados anexos:** baixar o PDF como está, mesmo que seja imagem.

**NÃO gerar PDFs com ReportLab, python-docx, ou qualquer biblioteca de geração.** Se tentar isso, pare e reporte.

## Pasta de destino (caminho exato — verifique a barra contrabarra)

```
C:\Users\cery0\projetos\gestao-vagas\_bmad-output\h1-corpus\raw\
```

```
C:\Users\cery0\projetos\gestao-vagas\_bmad-output\h1-corpus\anonimizado\
```

**Já existem 6 PDFs lá. Não apague, não sobrescreva.** Continue a numeração: `rp-07-...` até `rp-20-...`.

## Queries que funcionaram na rodada 1 (reuse)

- "substituição" + "vaga" + has:attachment
- "devolução" (emails de Greenhouse pra coord)
- "preenchimento de vaga"
- "Barbara solicitação"
- "Tonete substituição"

## Queries novas para diversificar (PRIORIDADE — rodada 1 ficou com 5/6 em INEP)

Precisamos de pelo menos **4 tomadores distintos** no corpus final. Rode estas buscas:

- `from:@tse.jus.br has:attachment`
- `from:@agu.gov.br has:attachment`
- `from:@agro.gov.br has:attachment`
- `from:@cushmanwakefield.com.br has:attachment`
- `from:@tjdft.jus.br has:attachment`
- `from:@receita.fazenda.gov.br has:attachment`
- `"requisição" OR "solicitação de contratação" to:bruno.fontes`
- Caixa compartilhada ou encaminhamentos do Wender/Leilian/Comercial se acessível

Se algum desses retornar RPs, **priorize-os sobre novos RPs do INEP** para balancear o corpus.

## Passo a passo por email

1. Abrir email candidato.
2. Confirmar que é RP (gestor do tomador pedindo contratação de pessoal).
3. **Se tem anexo PDF:** botão direito no anexo → Baixar → salvar direto em `raw\` com nome `rp-NN-AAAA-MM-DD-<tomador>.pdf`.
4. **Se o RP está no corpo do email:** Ctrl+P → "Salvar como PDF" → salvar em `raw\` com o mesmo padrão de nome.
5. **Se for thread longa com RP original encaminhado:** salvar o thread completo como PDF (não só o topo — o "RP original" do tomador costuma estar 2-3 forwards abaixo).

## Anonimização (mesmo protocolo da rodada 1)

Para cada novo PDF em `raw\`, gerar a versão anonimizada em `anonimizado\` com:

| Tipo de PII | Substituição |
|---|---|
| Nome de colaborador (devolvido, desligado, candidato) | `[PESSOA_NN]` |
| Nome de gestor do tomador que assina | `[GESTOR_NN]` |
| CPF | `XXX.XXX.XXX-XX` |
| RG | `XX.XXX.XXX-X` |
| Email pessoal (@gmail, @hotmail, @outlook, @yahoo) | `[EMAIL_REDACTED]` |
| Telefone pessoal | `(XX) XXXXX-XXXX` |
| Endereço residencial | `[ENDERECO_NN]` |
| Data de nascimento | `XX/XX/XXXX` |

**NÃO substituir:** nome do tomador/órgão, cargo, requisitos, motivo, emails institucionais (`@inep.gov.br`, `@agro.gov.br`, etc), emails `@greenhousedf.com.br`.

Para PDFs **nativos** (texto selecionável): use uma ferramenta de redação de PDF que substitua texto preservando layout (ex: `pypdf` + `PyMuPDF` modificando layer de texto; ou `pdf-redactor`).

Para PDFs **escaneados** (imagem): rode OCR (`pytesseract` com `lang='por'`), identifique bounding boxes das PIIs, e aplique retângulos pretos ou brancos sobre elas usando `PyMuPDF` (`page.add_redact_annot` → `page.apply_redactions()`). NÃO gere um PDF novo do zero — apenas modifique o original adicionando redactions.

Se não conseguir redactar preservando o original, marque no CORPUS_REPORT e **deixe o PDF de fora** em vez de gerar sintético.

## Atualizar o ground truth

Adicione os novos RPs ao arquivo `_rp_data.json` existente (não sobrescreva — append). Para cada RP:

```json
{
  "file": "rp-07-AAAA-MM-DD-tomador.pdf",
  "source": "anexo" | "corpo_email" | "thread_forwarded",
  "tomador": "...",
  "cargo": "...",
  "motivo": "...",
  "requisitos": ["..."],
  "quantidade_vagas": N,
  "carga_horaria": "...",
  "local": "..."
}
```

## Atualizar CORPUS_REPORT.md

Adicione uma seção "## 7. Rodada 2 — RPs adicionais" listando os novos 14 RPs com a mesma tabela da seção 2 e anote:
- Quais tomadores novos foram cobertos (versus só INEP da rodada 1)
- Quantos vieram de anexo vs corpo vs thread
- Qualquer limitação encontrada

## Checklist final antes de encerrar

Reporte esta checklist preenchida:

- [ ] ≥14 novos PDFs em `raw\` (total ≥20 somando rodada 1)
- [ ] ≥14 novos PDFs em `anonimizado\`
- [ ] Nenhum PDF foi gerado via ReportLab, WeasyPrint, pdfkit ou similar — todos são print-to-PDF do browser OU anexo original baixado OU escaneado com redactions
- [ ] `_rp_data.json` ampliado com os 14 novos entries
- [ ] `CORPUS_REPORT.md` atualizado com seção 7
- [ ] Pelo menos 3 tomadores distintos novos (ex: TSE, AGU, Agro)
- [ ] Verificação visual: abri 3 PDFs aleatórios novos e confirmei zero vazamento de PII
- [ ] Tamanho médio de PDF entre 30KB e 500KB (ReportLab gera ~5KB — se algum estiver aí, é sintético e precisa refazer)

## Regras inegociáveis

- **Não gerar PDFs sintéticos.** Se precisar, recuse a RP e passe pra próxima.
- **Não fazer upload de nada pra API externa.** Tudo fica no filesystem local.
- **Se chegar a 14 com diversidade baixa**, pare e me avise antes de preencher com mais INEP.
- **Antes de começar**, confirme: "vou rodar as queries X, Y, Z, priorizando tomadores distintos. Vou salvar como print-to-PDF ou anexo original (nunca gerado). Prossigo?"
```

---

## O que mudou vs rodada 1

| Aspecto | Rodada 1 | Rodada 2 |
|---|---|---|
| Método de PDF | ReportLab gerou | **Print-to-PDF ou anexo original** (obrigatório) |
| Quantidade | 6 | +14 (total 20) |
| Tomadores | 2 (INEP ×5, Golgi ×1) | **≥3 novos exigidos** |
| Anonimização | PDFs regerados do zero | Redaction sobre o original (preserva layout) |
| Caminho | ❌ gestao-vagas_bmad-output | ✅ gestao-vagas\\_bmad-output |
| Ground truth | Criou novo `_rp_data.json` | Append ao existente |

Cole o prompt dentro do bloco de código acima no Cowork e me avise quando terminar pra rodar o gate H1 de verdade.
