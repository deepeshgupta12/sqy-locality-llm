# src/io/facts_minifier.py
from __future__ import annotations

import json
from typing import Any, Dict, List


def _limit_list(xs: List[Any], n: int) -> List[Any]:
    if not isinstance(xs, list):
        return xs
    if n <= 0:
        return []
    return xs[:n]


def _trim_value(v: Any) -> Any:
    # Keep numbers/bools/None as-is
    if isinstance(v, (int, float)) or v is None or isinstance(v, bool):
        return v
    # Short strings as-is; long strings truncated
    if isinstance(v, str):
        return v if len(v) <= 1200 else v[:1200] + "…"
    # Lists trimmed shallowly
    if isinstance(v, list):
        # keep first 8 items generally
        return [_trim_value(x) for x in _limit_list(v, 8)]
    # Dicts shallowly trimmed
    if isinstance(v, dict):
        out: Dict[str, Any] = {}
        for k, val in v.items():
            out[k] = _trim_value(val)
        return out
    return v


def _compact_nearby(nearest: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    # Keep top 5 nearby, keep only commonly-used keys
    keep_keys = {
        "name",
        "rank_in_city",
        "rating",
        "typical_price_psf",
        "average_rent",
        "for_sale",
        "for_rent",
        "best_for",
    }
    out: List[Dict[str, Any]] = []
    for row in _limit_list(nearest or [], 5):
        if not isinstance(row, dict):
            continue
        slim = {k: row.get(k) for k in keep_keys if k in row}
        out.append(slim)
    return out


def _compact_facts(facts: Dict[str, Any]) -> Dict[str, Any]:
    """
    Light compaction that is safe for the LLM prompt.
    """
    f = dict(facts or {})

    # Trim heavy arrays/shapes if present
    # Nearby localities to top 5
    if isinstance(f.get("nearby_localities"), list):
        f["nearby_localities"] = _compact_nearby(f["nearby_localities"])

    # If there is a nested 'rental_breakup' / 'demand_supply' etc., trim lists
    for k in [
        "at_a_glance",
        "indices",
        "pricing",
        "rental",
        "housing_mix",
        "connectivity",
        "lifestyle",
        "culture_demo_geo",
        "demand_supply",
    ]:
        if isinstance(f.get(k), list):
            f[k] = _limit_list(f[k], 12)

    # Shallow trim values to keep tokens low
    slim: Dict[str, Any] = {}
    for k, v in f.items():
        slim[k] = _trim_value(v)

    return slim


def minify_facts(facts: Dict[str, Any], max_chars: int = 16000) -> str:
    """
    Returns a compact JSON string representation of `facts` that stays
    under ~max_chars where practical (best-effort).
    """
    # First pass compaction
    compact_dict = _compact_facts(facts)
    s = json.dumps(compact_dict, ensure_ascii=False, separators=(",", ":"))
    if len(s) <= max_chars:
        return s

    # Second pass: aggressively reduce list lengths
    aggressive = dict(compact_dict)
    for key in list(aggressive.keys()):
        v = aggressive[key]
        if isinstance(v, list):
            aggressive[key] = _limit_list(v, 5)
    s2 = json.dumps(aggressive, ensure_ascii=False, separators=(",", ":"))
    if len(s2) <= max_chars:
        return s2

    # Final pass: drop least-crucial large fields if still over budget
    drop_order = [
        "news",
        "links",
        "projects",
        "raw_listings",
        "demand_supply",
        "culture_demo_geo",
        "lifestyle",
        "connectivity",
    ]
    final = dict(aggressive)
    for k in drop_order:
        if len(json.dumps(final, ensure_ascii=False)) <= max_chars:
            break
        if k in final:
            final.pop(k, None)
    return json.dumps(final, ensure_ascii=False, separators=(",", ":"))