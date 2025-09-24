# src/generation/run.py
from __future__ import annotations

import argparse
import json
import os
from typing import Any, Dict

from config.env import load_env
from src.generation.llm_writer import generate_sections_json, render_sections_to_html
from src.enrich.web_enrich import enrich_culture_demo_geo  # optional SERP enrichment

load_env()


def _load_json(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _ensure_dir(p: str) -> None:
    os.makedirs(p, exist_ok=True)


def main() -> None:
    ap = argparse.ArgumentParser(description="Generate locality overview page (HTML) using GPT-5 and JSON facts.")
    ap.add_argument("--in", dest="inp", required=True, help="Path to facts JSON (e.g., data/whitefield.json)")
    ap.add_argument("--out", dest="outdir", required=True, help="Output directory (e.g., out/whitefield)")
    ap.add_argument("--serp", action="store_true", help="Enrich culture/demographics/geography using SERPAPI_KEY")
    ap.add_argument("--model", default=os.getenv("LLM_MODEL", "gpt-5"), help="LLM model (default gpt-5)")
    args = ap.parse_args()

    print(f"Loading JSON: {args.inp}")
    facts = _load_json(args.inp)

    if args.serp:
        try:
            facts = enrich_culture_demo_geo(facts)
        except Exception as e:
            print(f"[warn] SERP enrichment skipped: {e}")

    # 1) Ask GPT-5 for section JSON
    sections = generate_sections_json(facts, model=args.model)

    # 2) Render to HTML
    html = render_sections_to_html(facts, sections)

    # 3) Write files
    _ensure_dir(args.outdir)
    out_html = os.path.join(args.outdir, "index.html")
    with open(out_html, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Generated: {out_html}")

    # Optional: write normalized snapshot
    with open(os.path.join(args.outdir, "normalized.json"), "w", encoding="utf-8") as f:
        json.dump(sections, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()