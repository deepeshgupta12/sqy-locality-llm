# src/generation/llm_writer.py
from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

from openai import OpenAI

from src.io.facts_minifier import minify_facts
from src.render.sections import build_sections, hero_block
from src.render.template import wrap_page


# ----------------------------- Utilities -----------------------------

def _ensure_dict(data: Any) -> Dict[str, Any]:
    """Return a dict. If given a JSON string, parse it; else fallback to {}."""
    if isinstance(data, dict):
        return data
    if isinstance(data, str):
        try:
            parsed = json.loads(data)
            return parsed if isinstance(parsed, dict) else {}
        except Exception:
            return {}
    return {}


def _extract_json(text: str) -> Dict[str, Any]:
    """Extract the largest JSON object from a model reply (handles code fences)."""
    if not text:
        return {}
    # Drop code fences if present
    if "```" in text:
        cleaned_parts: List[str] = []
        for chunk in text.split("```"):
            # Skip language tags like ```json
            if chunk.strip().lower().startswith(("json",)):
                # remove the first line (language tag) if present
                lines = chunk.splitlines()
                cleaned_parts.append("\n".join(lines[1:]) if len(lines) > 1 else "")
            else:
                cleaned_parts.append(chunk)
        text = "\n".join(cleaned_parts)
    # Find outermost braces
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end > start:
        candidate = text[start : end + 1]
        try:
            obj = json.loads(candidate)
            return obj if isinstance(obj, dict) else {}
        except Exception:
            pass
    # Last resort
    try:
        obj = json.loads(text)
        return obj if isinstance(obj, dict) else {}
    except Exception:
        return {}


# ----------------------------- Prompt -----------------------------

def _build_messages(facts: Dict[str, Any]) -> List[Dict[str, Any]]:
    """System + user messages with all constraints. Output must be STRICT JSON."""
    locality = facts.get("locality_name") or facts.get("locality") or "Locality"
    city = facts.get("city_name") or facts.get("city") or "City"

    schema_desc = """
Return a STRICT JSON object (no HTML, no commentary) with exactly these keys:

{
  "hero": {
    "summary": string,
    "chips": [ {"label": string, "value": string} ]
  },
  "overview": { "para": string },
  "why_live": { "para": string, "bullets": [string] },
  "why_invest": { "para": string, "bullets": [string] },
  "connectivity_lifestyle": { "para": string, "bullets": [string] },
  "indices": [ {"label": string, "rating": string, "meaning": string} ],
  "indices_footnote": string,
  "prices_rents_homes_nearby": { "para": string, "bullets": [string] },
  "quality_of_life": { "para": string, "bullets": [string] },
  "people_place": { "para": string, "bullets": [string] }
}
"""

    rules = f"""
CONTENT RULES (must follow all):

- Use ONLY numbers and locality specifics that appear in FACTS; do not invent anything.
- Simple language; avoid fancy words. No heavy real-estate jargon.
- If a technical term is unavoidable, briefly explain it inline once.
- No abbreviations. If you must show something like 2 BHK, write “two-bedroom (2 BHK)” once; thereafter use full words.
- Do NOT repeat the same fact across sections.
- Indices: put short explanations in each row's "meaning", and put the Square Yards exclusivity + definitions in "indices_footnote" ONCE.
- Nearby localities: describe up to five as prose in the merged prices/rents/homes/nearby section using only FACTS.
- Output STRICT JSON only; do not wrap in code fences.
- Headings are added later; you only return the JSON content.
"""

    system_msg = {
        "role": "system",
        "content": (
            "You are a careful, helpful writer for a real-estate portal. "
            "Write factual, human-friendly content based ONLY on the provided FACTS. "
            "Return STRICT JSON that matches the requested schema. No HTML."
        ),
    }

    user_msg = {
        "role": "user",
        "content": (
            f"Task: Write the locality overview sections for {locality}, {city}.\n\n"
            f"{rules}\n\nSCHEMA:\n{schema_desc}\n\n"
            f"FACTS (JSON; use only this data):\n{json.dumps(facts, ensure_ascii=False)}"
        ),
    }

    return [system_msg, user_msg]


# ----------------------------- LLM call -----------------------------

def generate_sections_json(facts: Dict[str, Any], model: Optional[str] = None) -> Dict[str, Any]:
    """
    Calls GPT-5 (or model override) to turn FACTS into sections JSON.
    - No 'max_tokens' (unsupported for your model); omit limits.
    - No 'temperature' (not supported in your setup).
    """
    # minify_facts may return a JSON string; normalize to dict
    compact_raw = minify_facts(facts)
    compact = _ensure_dict(compact_raw)
    if not compact:
        # Fallback to original facts if minifier returned something unexpected
        compact = _ensure_dict(facts)

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    use_model = model or os.getenv("LLM_MODEL", "gpt-5")

    messages = _build_messages(compact)

    resp = client.chat.completions.create(
        model=use_model,
        messages=messages,
        top_p=1,  # keep defaults that are accepted by your deployment
        # If you ever need a cap: max_completion_tokens=6000
    )
    content = resp.choices[0].message.content if resp and resp.choices else ""
    data = _extract_json(content)
    return data if isinstance(data, dict) else {}


# ----------------------------- HTML render -----------------------------

def render_sections_to_html(facts: Dict[str, Any], sections: Dict[str, Any]) -> str:
    """Render full HTML using the renderer modules."""
    hero = hero_block(facts, sections.get("hero") or {})
    body = build_sections(sections, facts)
    title = (
        sections.get("hero", {}).get("title")
        or f"{facts.get('locality_name','Locality')}, {facts.get('city_name','City')} Locality Overview"
    )
    return wrap_page(title, hero, body)