# src/config/env.py
from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

_DOTENV_LOADED = False

def _fallback_parse_dotenv(dotenv_path: Path) -> None:
    # Very small parser for KEY=VALUE lines (no quotes, no exports).
    for line in dotenv_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        k = k.strip()
        v = v.strip().strip("'").strip('"')
        os.environ.setdefault(k, v)

def load_env(explicit_path: Optional[str] = None) -> None:
    """
    Loads .env from project root (or explicit_path) once per process.
    Uses python-dotenv if installed, otherwise a tiny fallback parser.
    """
    global _DOTENV_LOADED
    if _DOTENV_LOADED:
        return

    root = Path(explicit_path) if explicit_path else Path(__file__).resolve().parents[2]
    dotenv_path = root / ".env"
    if dotenv_path.exists():
        try:
            # Try python-dotenv if available
            from dotenv import load_dotenv  # type: ignore
            load_dotenv(dotenv_path=dotenv_path, override=False)
        except Exception:
            _fallback_parse_dotenv(dotenv_path)

    _DOTENV_LOADED = True