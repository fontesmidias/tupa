"""Recomputa similaridade semântica (embeddings) para os 3 prompts (v1/v2/v3).

Lê os smoke_results_vN.json, gera embeddings text-embedding-3-small para
cada `descricao_vaga` extraído + cada `descricao_vaga_esperada` curado,
calcula cosine similarity, e produz uma tabela comparativa contra a métrica
SequenceMatcher.

Custo estimado: ~6 RPs × (1 truth + 3 versões) = 24 embeddings de textos
curtos (~80 tokens cada) = ~2k tokens × $0.02/1M = ~$0.00004. Desprezível.

Uso:
  .venv/Scripts/python.exe scripts/rescore_with_embeddings.py
"""

from __future__ import annotations

import json
import math
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")

import django  # noqa: E402

django.setup()

from django.conf import settings  # noqa: E402

CORPUS = ROOT / "_bmad-output" / "h1-corpus"
EMBED_MODEL = "text-embedding-3-small"

# Limiares para classificação semântica (calibração inicial — pode ajustar
# após análise humana das comparações concretas).
SEM_THRESHOLD_MATCH = 0.90
SEM_THRESHOLD_PARCIAL = 0.75


def cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    return dot / (na * nb) if na and nb else 0.0


def classify_sem(sim: float) -> str:
    if sim >= SEM_THRESHOLD_MATCH:
        return "match"
    if sim >= SEM_THRESHOLD_PARCIAL:
        return "parcial"
    return "divergente"


def main() -> int:
    from openai import OpenAI

    api_key = getattr(settings, "OPENAI_API_KEY", "") or ""
    if not api_key:
        print("OPENAI_API_KEY ausente.")
        return 1
    client = OpenAI(api_key=api_key, timeout=30)

    truth_data = json.loads((CORPUS / "_rp_data.json").read_text(encoding="utf-8"))
    truth_map = {x["id"]: x.get("descricao_vaga_esperada") or "" for x in truth_data["rps_extracted"]}

    versions = {}
    for v in ("v1", "v2", "v3"):
        path = CORPUS / f"smoke_results_{v}.json"
        if not path.exists():
            print(f"  [skip] {path.name} não existe")
            continue
        versions[v] = {x["rp_id"]: x for x in json.loads(path.read_text(encoding="utf-8"))}

    # Coleta todos os textos a embarcar (deduplicado).
    texts: list[str] = []
    keys: dict[str, int] = {}

    def register(text: str) -> int:
        text = (text or "").strip()
        if not text:
            return -1
        if text in keys:
            return keys[text]
        idx = len(texts)
        texts.append(text)
        keys[text] = idx
        return idx

    rp_ids = sorted(set().union(*[set(d.keys()) for d in versions.values()]))
    plan = []
    for rid in rp_ids:
        truth_idx = register(truth_map.get(rid, ""))
        per_version = {}
        for vname, vmap in versions.items():
            extracted = (vmap.get(rid, {}).get("extracted", {}) or {}).get("descricao_vaga", "")
            per_version[vname] = register(extracted)
        plan.append({"rp_id": rid, "truth_idx": truth_idx, "versions": per_version})

    print(f"Gerando embeddings para {len(texts)} textos únicos...")
    resp = client.embeddings.create(model=EMBED_MODEL, input=texts)
    vectors = [item.embedding for item in resp.data]
    used_tokens = resp.usage.total_tokens
    cost = used_tokens / 1_000_000 * 0.02
    print(f"  ok: {used_tokens} tokens, custo ${cost:.6f}\n")

    # Tabela comparativa
    print(f"{'RP':<4} {'truth_len':<10} ", end="")
    for v in versions:
        print(f"{v+' SeqM':<11} {v+' Sem':<11} ", end="")
    print()

    rows = []
    for entry in plan:
        rid = entry["rp_id"]
        ti = entry["truth_idx"]
        if ti < 0:
            continue
        truth_vec = vectors[ti]
        truth_text = texts[ti]
        row = {"rp_id": rid, "truth_chars": len(truth_text), "versions": {}}
        print(f"{rid:<4} {len(truth_text):<10} ", end="")
        for v in versions:
            ei = entry["versions"][v]
            seqm_sim = versions[v][rid]["field_results"]["descricao_vaga"]["sim"]
            if ei < 0:
                sem = 0.0
            else:
                sem = cosine(truth_vec, vectors[ei])
            row["versions"][v] = {
                "seqm_sim": seqm_sim,
                "seqm_status": versions[v][rid]["field_results"]["descricao_vaga"]["status"],
                "sem_sim": round(sem, 4),
                "sem_status": classify_sem(sem),
            }
            print(f"{seqm_sim:<11.3f} {sem:<11.3f} ", end="")
        print()
        rows.append(row)

    # Recalcula match% global usando métrica semântica (substituindo só o campo descricao_vaga)
    print("\n=== Match% por versão (recalculado com semantic em descricao_vaga) ===")
    print(f"{'RP':<4} ", end="")
    for v in versions:
        print(f"{v+' seqm':<10} {v+' sem':<10} ", end="")
    print()

    summary = {v: {"seqm_sum": 0, "sem_sum": 0, "n": 0} for v in versions}
    for entry in plan:
        rid = entry["rp_id"]
        if entry["truth_idx"] < 0:
            continue
        print(f"{rid:<4} ", end="")
        for v in versions:
            base = versions[v][rid]
            fr = base["field_results"]
            # Recompute match_pct: para descricao_vaga usa status semantic; resto igual
            sem_status = next(r for r in rows if r["rp_id"] == rid)["versions"][v]["sem_status"]
            statuses = [
                fr["titulo"]["status"],
                fr["tomador"]["status"],
                fr["motivo"]["status"],
                sem_status,
                fr["requisitos"]["status"],
            ]
            valid = [s for s in statuses if s != "no_truth"]
            score_sem = sum(1 if s == "match" else 0.5 if s == "parcial" else 0 for s in valid)
            sem_pct = score_sem / len(valid) if valid else 0
            seqm_pct = base["match_pct"]
            print(f"{seqm_pct*100:<10.0f} {sem_pct*100:<10.0f} ", end="")
            summary[v]["seqm_sum"] += seqm_pct
            summary[v]["sem_sum"] += sem_pct
            summary[v]["n"] += 1
        print()

    print("\n=== Médias ===")
    for v, s in summary.items():
        if s["n"]:
            print(f"  {v}: seqm={s['seqm_sum']/s['n']*100:.1f}%  sem={s['sem_sum']/s['n']*100:.1f}%")

    # Persist
    out = {
        "model": EMBED_MODEL,
        "thresholds": {"match": SEM_THRESHOLD_MATCH, "parcial": SEM_THRESHOLD_PARCIAL},
        "embedding_tokens": used_tokens,
        "embedding_cost_usd": round(cost, 6),
        "rows": rows,
        "summary": {
            v: {
                "match_pct_seqm_avg": round(s["seqm_sum"] / s["n"] * 100, 2) if s["n"] else 0,
                "match_pct_sem_avg": round(s["sem_sum"] / s["n"] * 100, 2) if s["n"] else 0,
            }
            for v, s in summary.items()
        },
    }
    out_path = CORPUS / "semantic_rescore.json"
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nOK rescore: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
