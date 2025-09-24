# src/generation/text.py
from __future__ import annotations
from typing import Iterable, List, Optional

def fmt_int(x: Optional[int]) -> Optional[str]:
    if x is None:
        return None
    return f"{x:,}"

def fmt_currency_inr(v: Optional[float]) -> Optional[str]:
    if v is None:
        return None
    # expects monthly rent or totals
    return f"₹{int(round(v, 0)):,}"

def fmt_price_psf(v: Optional[float]) -> Optional[str]:
    if v is None:
        return None
    return f"₹{int(round(v,0)):,} / sq ft"

def fmt_range_psf(r: Optional[dict]) -> Optional[str]:
    if not r:
        return None
    mn = r.get("min")
    mx = r.get("max")
    if mn is None or mx is None:
        return None
    return f"₹{int(round(mn,0)):,}–₹{int(round(mx,0)):,} / sq ft"

def join_list(items: Iterable[str], sep: str = ", ") -> str:
    clean = [i.strip() for i in items if i and i.strip()]
    if not clean:
        return ""
    if len(clean) == 1:
        return clean[0]
    return sep.join(clean[:-1]) + " and " + clean[-1]

def fmt_km(v: Optional[float]) -> Optional[str]:
    if v is None:
        return None
    return f"{v:.1f} km"