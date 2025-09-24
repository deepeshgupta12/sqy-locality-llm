# src/utils/settings.py
from __future__ import annotations
import os
from typing import Optional
try:
    # optional; if python-dotenv is not installed this will just no-op
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except Exception:
    pass

OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
SERPAPI_KEY: Optional[str] = os.getenv("SERPAPI_KEY")

def require_openai_key() -> str:
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY not set")
    return OPENAI_API_KEY

def get_serp_key() -> Optional[str]:
    return SERPAPI_KEY