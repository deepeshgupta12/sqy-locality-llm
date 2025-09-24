# src/render/sections.py
from __future__ import annotations
from html import escape as h
from typing import Any, Dict, List, Optional

from src.utils.text import fmt_int, fmt_currency_inr, join_list  # if any of these aren’t used in your build, keep import for future chips


def _chip(label: str, value: str) -> str:
    return f"<div class='chip'><b>{h(label)}</b>: {h(value)}</div>"


def _chips(items: List[Dict[str, str]]) -> str:
    if not items:
        return ""
    html = "".join(
        _chip(str(it.get("label", "")), str(it.get("value", "")))
        for it in items
        if isinstance(it, dict)
    )
    return f"<div class='chips'>{html}</div>"


def _h2(title: str, anchor: str) -> str:
    return f"<h2 id='{h(anchor)}'>{h(title)}</h2>"


def _p(text: Optional[str]) -> str:
    if not text:
        return ""
    return f"<p>{h(text)}</p>"


def _ul(items: List[str]) -> str:
    if not items:
        return ""
    return "<ul>" + "".join(f"<li>{h(x)}</li>" for x in items if x) + "</ul>"


def hero_block(facts: Dict[str, Any], hero: Dict[str, Any]) -> str:
    loc = facts.get("locality_name") or facts.get("locality") or "Locality"
    city = facts.get("city_name") or facts.get("city") or "City"
    heading = f"{h(loc)}, {h(city)} Locality Overview: Connectivity, homes, lifestyle and nearby areas"
    summary = hero.get("summary") or ""
    chips_html = _chips(hero.get("chips") or [])
    return f"""
<section class='hero'>
  <div class='hero-inner'>
    <h1>{heading}</h1>
    <p class='summary'>{h(summary)}</p>
    {chips_html}
    <nav class='pills'>
      <a href="#overview">Overview</a>
      <span>•</span>
      <a href="#why-live">Why live</a>
      <span>•</span>
      <a href="#why-invest">Why invest</a>
      <span>•</span>
      <a href="#conn-life">Connectivity & lifestyle</a>
      <span>•</span>
      <a href="#indices">Locality scorecard</a>
      <span>•</span>
      <a href="#prices-rents">Prices, rents, homes & nearby</a>
      <span>•</span>
      <a href="#qol">Quality of life</a>
      <span>•</span>
      <a href="#people">People & place</a>
    </nav>
  </div>
</section>
"""


def _section_para_bullets(anchor: str, title: str, para: str, bullets: List[str]) -> str:
    return (
        f"<section id='{h(anchor)}'>"
        f"{_h2(title, anchor)}"
        f"{_p(para)}"
        f"{_ul(bullets)}"
        f"</section>"
    )


def build_sections(sections: Dict[str, Any], facts: Dict[str, Any]) -> str:
    pieces: List[str] = []

    # Overview (long paragraph only)
    pieces.append(
        f"<section id='overview'>{_h2('Overview', 'overview')}{_p((sections.get('overview') or {}).get('para'))}</section>"
    )

    loc = facts.get("locality_name") or facts.get("locality") or "Locality"
    city = facts.get("city_name") or facts.get("city") or "City"

    wl = sections.get("why_live") or {}
    pieces.append(
        _section_para_bullets("why-live", f"Why live in {loc}, {city}?", wl.get("para", ""), wl.get("bullets") or [])
    )

    wi = sections.get("why_invest") or {}
    pieces.append(
        _section_para_bullets("why-invest", f"Why invest in {loc}, {city}?", wi.get("para", ""), wi.get("bullets") or [])
    )

    cl = sections.get("connectivity_lifestyle") or {}
    pieces.append(
        _section_para_bullets("conn-life", "Connectivity & lifestyle", cl.get("para", ""), cl.get("bullets") or [])
    )

    # Locality scorecard (indices) with asterisk footnote (no backslashes in f-string expressions)
    idx_rows = ""
    for row in sections.get("indices") or []:
        label = h(str(row.get("label", "")))
        rating = h(str(row.get("rating", "")))
        meaning = h(str(row.get("meaning", "")))
        idx_rows += f"<tr><td>{label}</td><td>{rating}</td><td>{meaning}</td></tr>"
    idx_html = (
        "<table class='kv'><thead><tr>"
        "<th>Index</th><th>Rating</th><th>What it means</th>"
        "</tr></thead><tbody>"
        f"{idx_rows}</tbody></table>"
    )
    foot = sections.get("indices_footnote") or ""
    foot_html = f'<p class="footnote">* {h(foot)}</p>' if foot else ""
    pieces.append(
        f"<section id='indices'>{_h2('Locality scorecard', 'indices')}{idx_html}{foot_html}</section>"
    )

    pr = sections.get("prices_rents_homes_nearby") or {}
    pieces.append(
        _section_para_bullets("prices-rents", "Prices, rents, homes & nearby", pr.get("para", ""), pr.get("bullets") or [])
    )

    qol = sections.get("quality_of_life") or {}
    pieces.append(
        _section_para_bullets("qol", "Quality of life", qol.get("para", ""), qol.get("bullets") or [])
    )

    ppl = sections.get("people_place") or {}
    pieces.append(
        _section_para_bullets("people", "People & place", ppl.get("para", ""), ppl.get("bullets") or [])
    )

    return "\n".join(pieces)