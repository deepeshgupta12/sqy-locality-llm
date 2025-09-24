from __future__ import annotations
from typing import Any, Dict, List, Tuple
import html

# --------- small HTML helpers ----------
def _h(tag: str, text: str) -> str:
    return f"<{tag}>{html.escape(text)}</{tag}>"

def _p(text: str) -> str:
    return f"<p>{html.escape(str(text))}</p>"

def _section_anchor(title: str) -> str:
    aid = title.lower().replace(" ", "-").replace(",", "")
    return f'<a id="{aid}"></a>'

def _grid_table(headers: List[str], rows: List[List[str]]) -> str:
    thead = "<thead><tr>" + "".join(f"<th>{html.escape(h)}</th>" for h in headers) + "</tr></thead>"
    body_rows = []
    for r in rows:
        body_rows.append("<tr>" + "".join(f"<td>{html.escape(str(c))}</td>" for c in r) + "</tr>")
    tbody = "<tbody>" + "".join(body_rows) + "</tbody>"
    return f'<table class="grid">{thead}{tbody}</table>'

def _to_text(item: Any) -> str:
    if item is None:
        return ""
    if isinstance(item, (int, float)):
        return str(item)
    if isinstance(item, str):
        return item.strip()
    if isinstance(item, dict):
        if "label" in item and "value" in item:
            return f"{item.get('label','')}: {item.get('value','')}".strip(": ").strip()
        return ", ".join(f"{k}: {v}" for k, v in item.items())
    if isinstance(item, (list, tuple)):
        return ", ".join(_to_text(x) for x in item)
    return str(item)

def _list_to_ul(items: Any) -> str:
    if items is None:
        return ""
    if isinstance(items, str):
        items = [items]
    if isinstance(items, dict):
        items = [f"{k}: {v}" for k, v in items.items()]
    if not isinstance(items, (list, tuple)):
        items = [items]
    normalized: List[str] = []
    for x in items:
        t = _to_text(x)
        if t:
            normalized.append(t if t.endswith(".") else t + ".")
    if not normalized:
        return ""
    return "<ul>" + "".join(f"<li>{html.escape(li)}</li>" for li in normalized) + "</ul>"

def _split_label_value(s: str) -> Tuple[str, str]:
    for sep in [":", "—", "–", "-"]:
        if sep in s:
            left, right = s.split(sep, 1)
            return left.strip(), right.strip()
    return s.strip(), ""

def _normalize_kv_pairs(pairs: Any) -> List[Tuple[str, str]]:
    rows: List[Tuple[str, str]] = []
    if pairs is None:
        return rows
    if isinstance(pairs, dict):
        for k, v in pairs.items():
            k2, v2 = str(k).strip(), "" if v is None else str(v).strip()
            if k2 or v2:
                rows.append((k2, v2))
        return rows
    if isinstance(pairs, (list, tuple)):
        for it in pairs:
            if it is None:
                continue
            if isinstance(it, dict):
                if "label" in it and "value" in it:
                    lab = "" if it.get("label") is None else str(it.get("label")).strip()
                    val = "" if it.get("value") is None else str(it.get("value")).strip()
                    if lab or val:
                        rows.append((lab, val))
                else:
                    rows.append(_split_label_value(_to_text(it)))
            elif isinstance(it, (list, tuple)) and len(it) >= 2:
                lab = "" if it[0] is None else str(it[0]).strip()
                val = "" if it[1] is None else str(it[1]).strip()
                if lab or val:
                    rows.append((lab, val))
            elif isinstance(it, (int, float)):
                rows.append((str(it), ""))
            elif isinstance(it, str):
                lab, val = _split_label_value(it)
                if lab or val:
                    rows.append((lab, val))
            else:
                s = _to_text(it)
                if s:
                    lab, val = _split_label_value(s)
                    rows.append((lab, val))
    return rows

def _kv_pairs_to_table(pairs: Any) -> str:
    rows = _normalize_kv_pairs(pairs)
    if not rows:
        return ""
    trs = []
    for k, v in rows:
        trs.append(f"<tr><th>{html.escape(str(k))}</th><td>{html.escape(str(v))}</td></tr>")
    return f'<table class="kv"><tbody>{"".join(trs)}</tbody></table>'

# --------- main renderer ----------
def build_page_from_llm(facts: Dict[str, Any], s: Dict[str, Any]) -> str:
    name = (facts.get("locality_name") or facts.get("locality_city_name") or "Locality")
    city = (facts.get("city_name") or facts.get("locality_city_name") or "City")

    head = f"""
<!doctype html><html lang='en'><head>
<meta charset='utf-8'/>
<title>{html.escape(s.get('hero_title') or f"{name}, {city} Locality Overview")}</title>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<style>
body{{font-family:system-ui,-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;line-height:1.6;color:#111;padding:24px;max-width:960px;margin:0 auto;}}
h1{{font-size:28px;margin:0 0 8px;}}
h2{{font-size:22px;margin:28px 0 8px;}}
h3{{font-size:18px;margin:22px 0 6px;}}
.kv{{border-collapse:collapse;width:100%;margin:8px 0 16px}}
.kv th{{background:#fafafa;text-align:left;padding:8px;border:1px solid #eee;width:32%}}
.kv td{{padding:8px;border:1px solid #eee}}
.grid{{border-collapse:collapse;width:100%;margin:8px 0 16px}}
.grid th,.grid td{{border:1px solid #eee;padding:8px}}
ul{{padding-left:20px}}
.hero-badges{{display:flex;flex-wrap:wrap;gap:12px;margin:8px 0 16px}}
.badge{{background:#f5f5f7;border:1px solid #eee;border-radius:999px;padding:6px 10px;font-size:14px}}
.nav{{display:flex;flex-wrap:wrap;gap:12px;margin:12px 0 12px}}
.nav a{{font-size:14px;text-decoration:none;color:#0366d6}}
.small{{color:#555;font-size:14px}}
hr{{border:none;border-top:1px solid #eee;margin:24px 0}}
blockquote{{background:#f9fafb;border-left:4px solid #e5e7eb;margin:12px 0;padding:8px 12px}}
section{{margin-bottom:8px}}
</style>
</head><body>"""

    parts: List[str] = []
    parts.append(head)
    parts.append(_p("Home › Localities"))

    # Hero
    parts.append(_h("h1", s.get("hero_title") or f"{name}, {city} Locality Overview: Connectivity, homes, lifestyle and nearby areas"))
    if s.get("hero_intro"): parts.append(_p(s["hero_intro"]))
    badges = s.get("badges") or []
    if badges:
        parts.append('<div class="hero-badges">' + "".join(f'<span class="badge">{html.escape(_to_text(b))}</span>' for b in badges) + "</div>")

    # Nav (no removed sections)
    nav_items = [
        f"At a glance",
        f"About {name}, {city}",
        f"Why live in {name}, {city}?",
        f"Getting around in {name}, {city}",
        f"Lifestyle in {name}, {city}",
        f"Quality of life in {name}, {city}",
        f"Homes, prices and nearby areas in {name}, {city}",
        f"People and location of {name}, {city}",
    ]
    parts.append('<div class="nav">' + " • ".join(f'<a href="#{t.lower().replace(" ","-").replace(",","")}">{html.escape(t)}</a>' for t in nav_items) + "</div>")

    # At a glance
    parts.append(_section_anchor("At a glance"))
    parts.append(_h("h2","At a glance"))
    at_gl = _kv_pairs_to_table(s.get("at_a_glance") or [])
    if not at_gl and s.get("at_a_glance") is not None:
        at_gl = _list_to_ul(s.get("at_a_glance"))
    parts.append(at_gl)

    # Overview
    parts.append(_section_anchor(f"About {name}, {city}"))
    parts.append(_h("h2", f"About {name}, {city}"))
    if s.get("overview"): parts.append(_p(s["overview"]))

    # Why live here
    parts.append(_section_anchor(f"Why live in {name}, {city}?"))
    parts.append(_h("h2", f"Why live in {name}, {city}?"))
    parts.append(_list_to_ul(s.get("why_live") or []))

    # Connectivity
    parts.append(_section_anchor(f"Getting around in {name}, {city}"))
    parts.append(_h("h2", f"Getting around in {name}, {city}"))
    parts.append(_list_to_ul(s.get("connectivity") or []))

    # Lifestyle
    parts.append(_section_anchor(f"Lifestyle in {name}, {city}"))
    parts.append(_h("h2", f"Lifestyle in {name}, {city}"))
    parts.append(_list_to_ul(s.get("lifestyle") or []))

    # Quality of life (indices)
    parts.append(_section_anchor(f"Quality of life in {name}, {city}"))
    parts.append(_h("h2", f"Quality of life in {name}, {city}"))
    if s.get("indices_intro"): parts.append(_p(s["indices_intro"]))
    # indices table: Name | Rating | What it means
    idx = s.get("indices") or []
    if idx:
        headers = ["Index (Square Yards exclusive)","Rating/5","What it means"]
        rows: List[List[str]] = []
        for it in idx:
            if isinstance(it, dict):
                rows.append([
                    it.get("name",""),
                    str(it.get("rating","")),
                    it.get("explain",""),
                ])
        parts.append(_grid_table(headers, rows))

    # Homes + Prices + Nearby (merged)
    parts.append(_section_anchor(f"Homes, prices and nearby areas in {name}, {city}"))
    parts.append(_h("h2", f"Homes, prices and nearby areas in {name}, {city}"))
    hp = s.get("homes_prices_nearby") or {}
    if hp.get("intro"): parts.append(_p(hp["intro"]))
    if hp.get("price_points"):
        parts.append(_h("h3","Prices and trends"))
        parts.append(_list_to_ul(hp.get("price_points")))
    if hp.get("rent_points"):
        parts.append(_h("h3","Rent and tenant demand"))
        parts.append(_list_to_ul(hp.get("rent_points")))
    if hp.get("housing_points"):
        parts.append(_h("h3","Homes and formats"))
        parts.append(_list_to_ul(hp.get("housing_points")))
    nb = hp.get("nearby_table") or []
    if nb:
        parts.append(_h("h3","Nearby localities to compare"))
        headers = ["Rank","Locality","Rating","Typical price (per square feet)","Average monthly rent","For sale","For rent","New projects","Best for"]
        rows: List[List[str]] = []
        for r in nb:
            if isinstance(r, dict):
                rows.append([
                    r.get("rank",""),
                    r.get("locality",""),
                    r.get("rating",""),
                    r.get("typical_price_psf",""),
                    r.get("avg_monthly_rent",""),
                    r.get("for_sale",""),
                    r.get("for_rent",""),
                    r.get("new_projects",""),
                    r.get("best_for",""),
                ])
        parts.append(_grid_table(headers, rows))

    # People and location
    parts.append(_section_anchor(f"People and location of {name}, {city}"))
    parts.append(_h("h2", f"People and location of {name}, {city}"))
    for para in (s.get("people_location") or []):
        parts.append(_p(_to_text(para)))

    # Done
    parts.append("</body></html>")
    return "".join(parts)
