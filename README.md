SQY Locality LLM — SEO/AEO Locality Overview Generator

Generate human-friendly, factual, non-repetitive locality overview pages for Square Yards from a single source of truth (FACTS JSON). The engine produces beautified HTML that follows SEO and Answers-Engine (AEO) best practices and is easy for first-time buyers and investors to read.

⸻

What this engine does
	•	Writes only from your facts (JSON).
No invented numbers, dates, places, or claims. If a value is missing, it’s simply omitted without placeholders.
	•	Plain language (no jargon).
When a technical term is unavoidable, it is explained inline once (for example, “months of inventory — if no new homes come up for sale, how many months the current stock would take to sell at the recent pace”).
	•	No abbreviations.
If an abbreviation must appear (for example, 2 BHK), the first mention is always the full form (“two-bedroom (2 BHK)”), and full words are used thereafter.
	•	SEO/AEO-friendly structure: clear headings, scannable bullets, sensible tables, stable anchors, and internal links. No filler. No repetition.
	•	Merged market section: Pricing Trends + Rental Market + Housing Mix + Nearby Localities appear together as a single, coherent block.
	•	Indices are explained with a single footnote (Lifestyle, Livability, Connectivity, Education & Health) and clearly marked as Square Yards exclusive.
	•	Optional web enrichment using SERP API for qualitative culture/demographics/geography lines. Numbers still come only from your JSON.
	•	Deterministic fallbacks with safe defaults and graceful omissions if a field is not present.

Not included by design in final output: Top Developers, News & Updates, a standalone FAQ block, and a Disclaimer section. FAQs are woven into relevant sections when they add unique value.

⸻

Inputs & Outputs

Input — FACTS JSON (source of truth)
	•	Located in data/<slug>.json (for example, data/whitefield.json).
	•	Contains all numeric and textual fields used for copy, indices, interlinking, and nearby comparisons.
	•	No CSVs are used anywhere.

Output — Sections JSON + HTML
	•	The LLM returns a strict Sections JSON (never raw prose).
	•	The renderer converts Sections JSON to beautified, responsive HTML at out/<slug>/index.html.
	•	A normalized input snapshot is written to out/<slug>/normalized.json for auditability.

⸻

Project structure
sqy-locality-llm/
├─ data/                      # FACTS JSON files (your source of truth)
├─ out/                       # Generated HTML + normalized snapshots
├─ src/
│  ├─ config/
│  │  └─ __init__.py          # loads .env / environment variables
│  ├─ generation/
│  │  ├─ run.py               # CLI entry point
│  │  ├─ llm_writer.py        # messages → LLM → Sections JSON (with validation)
│  │  └─ facts_minifier.py    # compacts large FACTS for token safety
│  ├─ enrich/
│  │  └─ web_enrich.py        # optional SERP enrichment (qualitative only)
│  ├─ io/
│  │  ├─ json_loader.py       # loads & normalizes FACTS JSON
│  │  └─ inspect_json.py      # pretty-prints and sanity-checks FACTS
│  └─ render/
│     └─ sections.py          # turns Sections JSON into HTML
├─ .env                        # your secrets (NOT committed)
├─ .env.example                # template (safe to commit)
├─ requirements.txt
└─ README.md

Setup
	1.	Python - Use Python 3.10+ (macOS or Linux recommended).
	2.	Create and activate a virtual environment
  python -m venv .venv
  source .venv/bin/activate
  3.	Install dependencies
  pip install -r requirements.txt
  4. Environment
	  •	Copy .env.example to .env and set:
        OPENAI_API_KEY=sk-********************************
        SERPAPI_KEY=**************************************
        LLM_MODEL=gpt-5
  	•	Keep .env private. It’s ignored by .gitignore.

Run the generator
Generate a page (example: Whitefield): python -m src.generation.run --in data/whitefield.json --out out/whitefield --serp
	•	--serp turns on web enrichment (qualitative culture/demographics/geography lines only).
	•	Open the HTML (macOS):
    open out/whitefield/index.html
  •	Inspect the normalized snapshot:
    python -m src.io.inspect_json --in data/whitefield.json


Writing rules (enforced by the LLM prompt)
	•	Use only numbers from FACTS for locality specifics (prices, rents, counts, ranks, indices, nearby metrics).
Web enrichment never injects numeric claims.
	•	Simple, persona-friendly language. Avoid jargon. Explain a term one time if it is essential.
	•	No abbreviations beyond the first expanded mention.
	•	No repetition across sections. A fact appears once unless context demands it.
	•	Merge market content into one section: Pricing Trends + Rental Market + Housing Mix + Nearby Localities.
	•	Indices section must:
	•	Use human names (Lifestyle, Livability, Connectivity, Education & Health).
	•	Include a single footnote:
“Indices are Square Yards exclusive. Lifestyle is based on nearby amenities and quality of life factors; Livability reflects quality of housing, safety, and environment; Connectivity reflects proximity to transport and infrastructure; Education & Health reflects availability and proximity of schools and healthcare.”
	•	People, Culture and Place must cover, in natural language and without speculation: demographics, geography, language, type of neighbourhood, wealth/income tendencies, employment context, environment, physical and mental health context, education, recreation and leisure time, social belonging, religious beliefs, safety, security, and freedom.
If a specific figure is not in FACTS, describe it qualitatively and neutrally.

⸻

LLM behavior and limits
	•	Primary model: GPT-5. No temperature, no max_tokens (uses max_completion_tokens if applicable).
	•	Fallbacks: If your account limits are exceeded, the engine safely minifies FACTS and retries on a lightweight model.
	•	Token safety: Large FACTS are compacted by facts_minifier.py to respect your token-per-minute and context limits.

The engine never prints prompts or model names into page content.

Troubleshooting
	•	Model parameter errors
Some models reject temperature or max_tokens. The engine uses no temperature and switches to max_completion_tokens when required.
	•	Token/RPM limits
If you hit rate or token caps, the engine automatically compacts FACTS and retries on a smaller model.
	•	Import errors in VS Code (Pylance)
Make sure your interpreter is the project venv (.venv/bin/python) via Command Palette → Python: Select Interpreter.
	•	SERP enrichment disabled
Remove --serp, or set a valid SERPAPI_KEY in .env.





MIT License

Copyright (c) 2025 Deepesh Kumar Gupta

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the “Software”), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
  

  
