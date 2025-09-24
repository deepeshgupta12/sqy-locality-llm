# src/config.py
from __future__ import annotations
import os

# Read keys from environment. (Use: export OPENAI_API_KEY=... ; export SERPAPI_KEY=...)
OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY")
SERPAPI_KEY: str | None = os.getenv("SERPAPI_KEY")

# Default model. You can override with --model flag at runtime.
LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-5")

def require_openai():
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY is not set in environment.")
    return OPENAI_API_KEY

def get_serp_key() -> str | None:
    return SERPAPI_KEY