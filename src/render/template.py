# src/generation/template.py
from __future__ import annotations

from typing import Any

CSS = """
:root { --ink:#0b1426; --muted:#64748b; --chip:#eef2ff; --chiptext:#0b1426; --blue:#1e40af; }
* { box-sizing: border-box; }
body { font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif; color: var(--ink); margin: 0; }
section { padding: 24px 20px; max-width: 1000px; margin: 0 auto; }
.hero { background: #1e3a8a; color: white; padding: 36px 20px; }
.hero .title { font-weight: 800; font-size: 28px; line-height: 1.2; }
.hero .subtitle { margin-top: 8px; font-size: 16px; opacity: .95; }
.chips { margin-top: 16px; display:flex; gap:10px; flex-wrap:wrap; }
.chip { background: var(--chip); color: var(--chiptext); padding: 8px 10px; border-radius: 999px; font-size: 13px; }
nav.tabs { margin-top: 18px; display:flex; gap:10px; flex-wrap:wrap; }
nav.tabs a { color: #e0e7ff; text-decoration: none; background: rgba(255,255,255,.12); padding: 6px 10px; border-radius: 999px; font-size: 13px; }
h2 { font-size: 22px; margin: 0 0 10px; }
p { color: var(--ink); font-size: 15px; line-height:1.6; margin: 10px 0; }
ul { margin: 10px 0 0 18px; padding: 0; }
li { margin: 6px 0; }
table.kv { width: 100%; border-collapse: collapse; margin-top: 10px; }
.kv th, .kv td { border: 1px solid #e5e7eb; padding: 10px; text-align: left; font-size: 14px; }
.kv thead { background: #f8fafc; }
.note { color: var(--muted); font-size: 13px; margin-top: 8px; }
footer { color: var(--muted); font-size: 13px; padding: 30px 20px; max-width: 1000px; margin: 0 auto; }
"""

def wrap_page(title: str, hero_html: str, body_html: str) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width,initial-scale=1" />
<title>{title}</title>
<style>{CSS}</style>
</head>
<body>
{hero_html}
{body_html}
<footer>Content is compiled from the provided facts and public sources. Verify current details before making any decision.</footer>
</body>
</html>"""