"""Smoke test em lote — Opção A do HANDOFF.md.

Roda extract_rp_from_pdf nos 6 PDFs sintéticos do corpus rodada 1, compara
campo-a-campo contra _rp_data.json (ground truth), classifica match/parcial/
divergente, e gera SMOKE_REPORT.md + smoke_results.json.

Uso:
  .venv/Scripts/python.exe scripts/smoke_test_h1_batch.py
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
import unicodedata
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")

import django  # noqa: E402

django.setup()

from apps.ai_providers.providers.openai_llm import extract_rp_from_pdf  # noqa: E402

CORPUS_DIR = ROOT / "_bmad-output" / "h1-corpus"
ANON_DIR = CORPUS_DIR / "anonimizado"
GROUND_TRUTH = CORPUS_DIR / "_rp_data.json"
REPORT_MD = CORPUS_DIR / "SMOKE_REPORT.md"
RESULTS_JSON = CORPUS_DIR / "smoke_results.json"

# Pricing GPT-4o-mini (USD por 1M tokens)
PRICE_IN = 0.15
PRICE_OUT = 0.60

SIM_THRESHOLD = 0.6


def normalize(s: str) -> str:
    if not s:
        return ""
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    s = s.lower()
    s = re.sub(r"\s+", " ", s).strip()
    s = re.sub(r"[^\w\s]", "", s)
    return s


def similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, normalize(a), normalize(b)).ratio()


def classify_field(extracted: str, truth: str) -> tuple[str, float]:
    """Retorna (status, similaridade)."""
    if not truth:
        return ("no_truth", 0.0)
    if not extracted:
        return ("divergente", 0.0)
    sim = similarity(extracted, truth)
    if sim >= 0.95:
        return ("match", sim)
    if sim >= SIM_THRESHOLD:
        return ("parcial", sim)
    return ("divergente", sim)


def classify_list(extracted: list[str], truth: list[str]) -> dict:
    """Compara listas item-a-item via melhor-match cosseno por similaridade."""
    if not truth:
        return {
            "status": "no_truth",
            "extracted_count": len(extracted),
            "truth_count": 0,
            "items": [],
        }
    if not extracted:
        return {
            "status": "divergente",
            "extracted_count": 0,
            "truth_count": len(truth),
            "items": [{"truth": t, "best_match": None, "sim": 0.0, "status": "missing"} for t in truth],
        }
    items = []
    matched_truth = 0
    for t in truth:
        best_sim = 0.0
        best_ext = None
        for e in extracted:
            sim = similarity(e, t)
            if sim > best_sim:
                best_sim = sim
                best_ext = e
        if best_sim >= 0.95:
            status = "match"
            matched_truth += 1
        elif best_sim >= SIM_THRESHOLD:
            status = "parcial"
            matched_truth += 0.5
        else:
            status = "missing"
        items.append({"truth": t, "best_match": best_ext, "sim": round(best_sim, 3), "status": status})
    pct = matched_truth / len(truth)
    if pct >= 0.95:
        overall = "match"
    elif pct >= SIM_THRESHOLD:
        overall = "parcial"
    else:
        overall = "divergente"
    return {
        "status": overall,
        "extracted_count": len(extracted),
        "truth_count": len(truth),
        "match_ratio": round(pct, 3),
        "items": items,
    }


def get_truth_for_pdf(filename: str, ground: list[dict]) -> dict | None:
    """rp-01-... → id=1, rp-02 → id=2, etc."""
    m = re.match(r"rp-(\d+)-", filename)
    if not m:
        return None
    rp_id = int(m.group(1))
    for entry in ground:
        if entry.get("id") == rp_id:
            return entry
    return None


def truth_requisitos(truth: dict) -> list[str]:
    """Ground truth usa 'requisitos' ou 'requisitos_atividades' (id=5)."""
    return truth.get("requisitos") or truth.get("requisitos_atividades") or []


def run_one(pdf_path: Path, truth: dict) -> dict:
    pdf_bytes = pdf_path.read_bytes()
    t0 = time.perf_counter()
    error = None
    envelope = None
    try:
        envelope = extract_rp_from_pdf(pdf_bytes, filename=pdf_path.name)
    except Exception as exc:
        error = f"{type(exc).__name__}: {exc}"
    elapsed_ms = int((time.perf_counter() - t0) * 1000)

    if error:
        return {
            "file": pdf_path.name,
            "rp_id": truth.get("id"),
            "parsed_ok": False,
            "error": error,
            "latency_ms": elapsed_ms,
        }

    res = envelope.result
    cost = (envelope.stats.input_tokens * PRICE_IN + envelope.stats.output_tokens * PRICE_OUT) / 1_000_000

    truth_titulo = truth.get("cargo", "")
    truth_tomador = truth.get("tomador", "")
    truth_motivo = truth.get("motivo", "")
    truth_descricao = truth.get("descricao_vaga_esperada") or truth.get("body_text", "")
    truth_reqs = truth_requisitos(truth)

    titulo_status, titulo_sim = classify_field(res.titulo, truth_titulo)
    tomador_status, tomador_sim = classify_field(res.tomador, truth_tomador)
    motivo_status, motivo_sim = classify_field(res.motivo, truth_motivo)
    descricao_status, descricao_sim = classify_field(res.descricao_vaga, truth_descricao)
    reqs_classification = classify_list(list(res.requisitos), truth_reqs)

    field_statuses = [titulo_status, tomador_status, motivo_status, descricao_status, reqs_classification["status"]]
    valid = [s for s in field_statuses if s != "no_truth"]
    score = 0.0
    for s in valid:
        if s == "match":
            score += 1
        elif s == "parcial":
            score += 0.5
    match_pct = score / len(valid) if valid else 0.0

    return {
        "file": pdf_path.name,
        "rp_id": truth.get("id"),
        "parsed_ok": True,
        "latency_ms": envelope.stats.latency_ms,
        "input_tokens": envelope.stats.input_tokens,
        "output_tokens": envelope.stats.output_tokens,
        "cost_usd": round(cost, 6),
        "model": envelope.stats.model_id,
        "confidence_llm": res.confidence,
        "match_pct": round(match_pct, 3),
        "extracted": {
            "titulo": res.titulo,
            "tomador": res.tomador,
            "motivo": res.motivo,
            "descricao_vaga": res.descricao_vaga,
            "requisitos": list(res.requisitos),
        },
        "truth": {
            "titulo": truth_titulo,
            "tomador": truth_tomador,
            "motivo": truth_motivo,
            "descricao_vaga_preview": truth_descricao[:200],
            "requisitos": truth_reqs,
        },
        "field_results": {
            "titulo": {"status": titulo_status, "sim": round(titulo_sim, 3)},
            "tomador": {"status": tomador_status, "sim": round(tomador_sim, 3)},
            "motivo": {"status": motivo_status, "sim": round(motivo_sim, 3)},
            "descricao_vaga": {"status": descricao_status, "sim": round(descricao_sim, 3)},
            "requisitos": reqs_classification,
        },
    }


def render_report(results: list[dict]) -> str:
    lines = []
    lines.append("# Smoke Test em Lote — H1 Rodada 1 (sintética)")
    lines.append("")
    lines.append(f"Provider: OpenAI GPT-4o-mini · PDFs: {len(results)} · Corpus: `_bmad-output/h1-corpus/anonimizado/`")
    lines.append("")
    lines.append("## Tabela comparativa")
    lines.append("")
    lines.append("| Arquivo | parsed_ok | Latência (ms) | Tokens in/out | Custo (USD) | Confidence LLM | Match% | titulo | tomador | motivo | descricao | requisitos |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|---|---|")
    total_cost = 0.0
    total_lat = 0
    for r in results:
        if not r.get("parsed_ok"):
            lines.append(f"| {r['file']} | ❌ | {r['latency_ms']} | — | — | — | — | — | — | — | — | — |")
            continue
        fr = r["field_results"]
        total_cost += r["cost_usd"]
        total_lat += r["latency_ms"]
        lines.append(
            f"| {r['file']} | ✅ | {r['latency_ms']} | "
            f"{r['input_tokens']}/{r['output_tokens']} | "
            f"${r['cost_usd']:.5f} | {r['confidence_llm']:.2f} | "
            f"{r['match_pct']*100:.0f}% | "
            f"{fr['titulo']['status']} ({fr['titulo']['sim']:.2f}) | "
            f"{fr['tomador']['status']} ({fr['tomador']['sim']:.2f}) | "
            f"{fr['motivo']['status']} ({fr['motivo']['sim']:.2f}) | "
            f"{fr['descricao_vaga']['status']} ({fr['descricao_vaga']['sim']:.2f}) | "
            f"{fr['requisitos']['status']} ({fr['requisitos'].get('match_ratio', 0):.2f}, "
            f"{fr['requisitos']['extracted_count']}/{fr['requisitos']['truth_count']}) |"
        )
    lines.append("")
    lines.append(f"**Totais:** custo ${total_cost:.5f} · latência somada {total_lat} ms")
    lines.append("")
    lines.append("## Divergências e parciais por RP")
    lines.append("")
    div_idx = 0
    for r in results:
        if not r.get("parsed_ok"):
            lines.append(f"### {r['file']} — ❌ FAILED: `{r.get('error')}`")
            lines.append("")
            continue
        fr = r["field_results"]
        flagged = []
        for fname in ("titulo", "tomador", "motivo", "descricao_vaga"):
            st = fr[fname]["status"]
            if st in ("parcial", "divergente"):
                flagged.append((fname, st, fr[fname]["sim"]))
        reqs_st = fr["requisitos"]["status"]
        if reqs_st in ("parcial", "divergente"):
            flagged.append(("requisitos", reqs_st, fr["requisitos"].get("match_ratio", 0)))
        if not flagged:
            lines.append(f"### {r['file']} (RP #{r['rp_id']}) — ✅ tudo match")
            lines.append("")
            continue
        lines.append(f"### {r['file']} (RP #{r['rp_id']}) — confidence LLM: {r['confidence_llm']:.2f}")
        lines.append("")
        for fname, st, sim in flagged:
            div_idx += 1
            lines.append(f"**#{div_idx}. campo `{fname}` — {st}** (sim/ratio: {sim:.2f})")
            lines.append("")
            if fname == "requisitos":
                lines.append(f"- Ground truth ({fr['requisitos']['truth_count']} itens):")
                for t in r["truth"]["requisitos"]:
                    lines.append(f"  - {t}")
                lines.append(f"- LLM extraiu ({fr['requisitos']['extracted_count']} itens):")
                for e in r["extracted"]["requisitos"]:
                    lines.append(f"  - {e}")
                lines.append("")
                lines.append("- Item-a-item (truth → melhor match):")
                for it in fr["requisitos"]["items"]:
                    bm = it["best_match"] or "—"
                    lines.append(f"  - [{it['status']} {it['sim']}] `{it['truth']}` → `{bm}`")
            else:
                truth_val = r["truth"].get(fname) or r["truth"].get(f"{fname}_preview", "")
                lines.append(f"- Ground truth: `{truth_val}`")
                lines.append(f"- LLM extraiu: `{r['extracted'][fname]}`")
            lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Pergunta para revisão humana (Bruno)")
    lines.append("")
    lines.append("Para cada divergência ou parcial listada acima, classifique como:")
    lines.append("")
    lines.append("- **(a) erro de prompt** — ajustamos para v2")
    lines.append("- **(b) limitação do sintético** — ignorar até rodada 2 com originais")
    lines.append("- **(c) erro do LLM** — registrar como falha real")
    lines.append("")
    lines.append("Respostas serão salvas em `HUMAN_FEEDBACK.md`.")
    return "\n".join(lines)


def main() -> int:
    pdfs = sorted(ANON_DIR.glob("rp-*.pdf"))
    if not pdfs:
        print(f"❌ Nenhum PDF em {ANON_DIR}")
        return 1
    ground_data = json.loads(GROUND_TRUTH.read_text(encoding="utf-8"))
    ground = ground_data["rps_extracted"]

    results: list[dict] = []
    for pdf in pdfs:
        truth = get_truth_for_pdf(pdf.name, ground)
        if not truth:
            print(f"⚠ sem ground truth para {pdf.name}")
            continue
        print(f"[{pdf.name}] extraindo...", flush=True)
        r = run_one(pdf, truth)
        if r.get("parsed_ok"):
            print(
                f"  ok · {r['latency_ms']}ms · ${r['cost_usd']:.5f} · "
                f"conf={r['confidence_llm']:.2f} · match={r['match_pct']*100:.0f}%"
            )
        else:
            print(f"  FAIL · {r.get('error')}")
        results.append(r)

    RESULTS_JSON.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    REPORT_MD.write_text(render_report(results), encoding="utf-8")
    print()
    print(f"OK Relatorio: {REPORT_MD}")
    print(f"OK JSON bruto: {RESULTS_JSON}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
