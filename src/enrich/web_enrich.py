# src/enrich/web_enrich.py
from __future__ import annotations

import os
import re
from typing import Any, Dict, List

import requests

from config.env import load_env
load_env()

GOOGLE_ENDPOINT = "https://serpapi.com/search.json"


def _clean(text: str) -> str:
    t = re.sub(r"\s+", " ", text or "").strip()
    return t


def _serp(q: str, location: str = "Bengaluru, India", num: int = 5) -> Dict[str, Any]:
    key = os.getenv("SERPAPI_KEY")
    if not key:
        raise RuntimeError("SERPAPI_KEY not set")
    params = {"engine": "google", "q": q, "location": location, "num": num, "api_key": key}
    r = requests.get(GOOGLE_ENDPOINT, params=params, timeout=20)
    r.raise_for_status()
    return r.json()


def _bullets_from_serp(res: Dict[str, Any], max_items: int = 6) -> List[str]:
    out: List[str] = []
    for it in (res.get("organic_results") or [])[:max_items]:
        title = _clean(it.get("title") or "")
        snippet = _clean(it.get("snippet") or "")
        if title and snippet:
            out.append(f"{title}: {snippet}")
        elif title:
            out.append(title)
    return out


def enrich_culture_demo_geo(facts: Dict[str, Any]) -> Dict[str, Any]:
    """
    Adds simple culture/demographics/geography bullets using public search.
    Keeps it generic and safe—no invented numbers.
    """
    loc = facts.get("locality_name") or facts.get("locality") or "this locality"
    city = facts.get("city_name") or facts.get("city") or "the city"

    q = f"{loc} {city} culture demographics geography key facts"
    try:
        res = _serp(q)
        bullets = _bullets_from_serp(res, max_items=5)
        if bullets:
            cdg = facts.get("culture_demo_geo") or {}
            cdg_bullets = (cdg.get("bullets") or []) + bullets
            facts["culture_demo_geo"] = {"bullets": cdg_bullets[:8]}
    except Exception:
        # silent failure: enrichment is optional
        pass
    return facts