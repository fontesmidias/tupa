"""Smoke test do MVP.C com OpenAI GPT-4o-mini contra 1 PDF do corpus.

Valida apenas que o pipeline funciona end-to-end:
  load .env → settings → openai_llm.extract_rp_from_pdf → ExtractionEnvelope.

NÃO é gate H1 — os PDFs do corpus são sintéticos (ReportLab). O resultado
serve só para confirmar conectividade, schema, custo e latência.

Uso:
  DJANGO_SETTINGS_MODULE=config.settings.dev .venv/Scripts/python.exe scripts/smoke_test_h1.py
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")

import django  # noqa: E402

django.setup()

from apps.ai_providers.providers.openai_llm import extract_rp_from_pdf  # noqa: E402

CORPUS_DIR = (
    Path(__file__).parent.parent
    / "_bmad-output"
    / "h1-corpus"
    / "anonimizado"
)


def main() -> int:
    pdfs = sorted(CORPUS_DIR.glob("*.pdf"))
    if not pdfs:
        print(f"❌ Nenhum PDF encontrado em {CORPUS_DIR}")
        return 1

    target = pdfs[0]
    print(f"[PDF] Smoke test com: {target.name}")
    print(f"      Tamanho: {target.stat().st_size} bytes")
    print()

    pdf_bytes = target.read_bytes()

    try:
        envelope = extract_rp_from_pdf(pdf_bytes, filename=target.name)
    except Exception as exc:
        print(f"[FAIL] {type(exc).__name__}: {exc}")
        return 2

    print("[OK] Pipeline funcionou")
    print(f"     model:     {envelope.stats.model_id}")
    print(f"     latencia:  {envelope.stats.latency_ms} ms")
    print(
        f"     tokens:    {envelope.stats.input_tokens} in / "
        f"{envelope.stats.output_tokens} out"
    )

    cost = (
        envelope.stats.input_tokens * 0.15
        + envelope.stats.output_tokens * 0.60
    ) / 1_000_000
    print(f"     custo:     ${cost:.5f}")
    print(f"     confidence:{envelope.result.confidence}")
    print()
    print("[RESULT] JSON extraido:")
    print(
        json.dumps(envelope.result.model_dump(), ensure_ascii=False, indent=2)
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
