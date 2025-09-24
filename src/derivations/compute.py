import json, math
from typing import Dict, Any, List
from pathlib import Path

def load_json(path: str) -> dict:
    return json.loads(Path(path).read_text())

def compute_months_of_inventory(data: Dict[str, Any]) -> float:
    if data.get("months_of_inventory") is not None:
        return float(data["months_of_inventory"])
    absorption_90d = max(0, int(data.get("absorption_90d", 0)))
    if absorption_90d < 9:
        return float("nan")
    monthly_abs = absorption_90d / 3.0
    if monthly_abs <= 0:
        return float("nan")
    return round(data.get("sale_property_count", 0) / monthly_abs, 1)

def blended_gross_yield_pct(data: Dict[str, Any], typical_area_cfg: Dict[str, Dict[str, float]]) -> float:
    city = data["city_name"]
    areas = typical_area_cfg.get(city, {})
    counts = data.get("bhk_type_property_count", {})
    total_units = sum(counts.values()) or 1
    weighted_area = 0.0
    for bhk, cnt in counts.items():
        a = areas.get(bhk, 1000.0)
        weighted_area += a * cnt
    avg_area = weighted_area / total_units
    implied_price = data["avg_sale_price_psf"] * avg_area
    annual_rent = data["avg_rent_price"] * 12.0
    gross_yield = (annual_rent / implied_price) * 100.0 if implied_price > 0 else 0.0
    return round(gross_yield, 2)

def build_default_interlinks(data: Dict[str, Any]) -> Dict[str, Any]:
    city_slug = data["city_name"].lower().replace(" ", "-")
    loc_slug = data["slug"]
    primary = [
        {"label": f"Flats for Sale in {data['locality_name']}", "href": f"/{loc_slug}/flats-for-sale"},
        {"label": f"Rent in {data['locality_name']}", "href": f"/{loc_slug}/apartments-for-rent"}
    ]
    secondary = [{"label": n["name"], "href": f"/{city_slug}/{n['name'].lower().replace(' ', '-') }"} for n in data.get("nearby_localities", [])[:3]]
    dev_links = []
    for dev in data.get("popular_developers", [])[:2]:
        dev_links.append({"label": f"{dev['name']} in {data['city_name']}", "href": f"/developers/{dev['name'].lower()}/{city_slug}"})
    return {"primary": primary, "secondary": secondary, "developer": dev_links}

# ---------- City-aware display names ----------
def normalize_property_terms(city: str, property_types: List[str]) -> Dict[str, str]:
    norm = {}
    for t in property_types:
        if city.lower() in {"bengaluru","bangalore"} and t.lower() == "builder floor":
            norm[t] = "independent house / small standalone floor"
        else:
            norm[t] = t
    return norm

# ---------- Plain-English glossary for unavoidable terms ----------
def build_layman_glossary(data: Dict[str, Any]) -> Dict[str, str]:
    sale = int(data.get("sale_property_count", 0))
    abs90 = int(data.get("absorption_90d", 0))
    monthly_abs = abs90/3.0 if abs90 else 0
    moi = compute_months_of_inventory(data)
    return {
        "months_of_inventory": (
            f"Months of inventory (~{moi}): if no new homes came up for sale, today’s stock would take about {moi} months "
            f"to sell at the recent pace of roughly {round(monthly_abs)} homes per month (based on the last 90 days)."
        ),
        "gross_rental_yield": "Gross rental yield: annual rent divided by the home’s purchase price (before maintenance or taxes).",
        "registered_rate": "Registered rate: average price recorded in government registrations over the chosen period.",
        "demand_supply": "Demand and supply: how many buyers are looking versus how many homes are listed."
    }

def derive_all(data: Dict[str, Any], speed_cfg: Dict[str, Any], area_cfg: Dict[str, Any]) -> Dict[str, Any]:
    out = dict(data)
    out["months_of_inventory"] = compute_months_of_inventory(out)
    out["blended_gross_yield_pct"] = blended_gross_yield_pct(out, area_cfg)
    out["interlinking"] = build_default_interlinks(out)
    out["property_type_display_names"] = normalize_property_terms(out["city_name"], out.get("property_types", []))
    out["narrative_glossary"] = build_layman_glossary(out)
    out["hero_stats_helper"] = {
        "rank_in_city": f"{out.get('locality_rank_in_city')}/{out.get('overall_city_locality_count')}",
        "typical_price_psf": out.get("price_percentiles_psf", {}).get("p50"),
        "price_change_3m_pct": out.get("asking_price_change_pct_3m"),
        "avg_rent_monthly": out.get("avg_rent_price")
    }
    return out
