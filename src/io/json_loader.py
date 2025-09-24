from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union


def _dig(root: Dict[str, Any], *keys: str, default: Any = None) -> Any:
    """Safe nested getter: _dig(obj, 'a','b','c', default=None)."""
    cur: Any = root
    for k in keys:
        if not isinstance(cur, dict) or k not in cur:
            return default
        cur = cur[k]
    return cur


def _get_lat_lng(payload: Dict[str, Any]) -> Tuple[Optional[float], Optional[float]]:
    # Try localityOverviewData first
    lat = _dig(payload, "data", "localityOverviewData", "latitude")
    lng = _dig(payload, "data", "localityOverviewData", "longitude")
    if lat is not None and lng is not None:
        try:
            return float(lat), float(lng)
        except Exception:
            pass

    # Fallback to localityData sublocality coords
    lat = _dig(payload, "data", "localityData", "sublocalityLatitude")
    lng = _dig(payload, "data", "localityData", "sublocalityLongitude")
    if lat is not None and lng is not None:
        try:
            return float(lat), float(lng)
        except Exception:
            pass

    return None, None


def _normalize_rent_value(val: Optional[Any]) -> Optional[int]:
    """
    SquareYards 'rentalRate' often appears as an integer like 42 meaning ₹42k.
    If it's < 1000, treat as thousands per month. If it's a string like '₹ 42.6 K', parse the number.
    Returns an integer monthly INR.
    """
    if val is None:
        return None
    if isinstance(val, (int, float)):
        if val < 1000:
            return int(round(float(val) * 1000))
        return int(val)
    if isinstance(val, str):
        s = val.lower().replace("₹", "").replace(",", "").strip()
        # Handle cases like '42.6 k' or '1 l' (lakhs)
        if "l" in s:  # lakh
            num = "".join(ch for ch in s if (ch.isdigit() or ch == ".")) or "0"
            return int(float(num) * 100000)
        if "k" in s:
            num = "".join(ch for ch in s if (ch.isdigit() or ch == ".")) or "0"
            return int(float(num) * 1000)
        # plain number string
        try:
            n = float(s)
            if n < 1000:
                return int(round(n * 1000))
            return int(round(n))
        except Exception:
            return None
    return None


def _rental_distribution(payload: Dict[str, Any]) -> Dict[str, int]:
    """
    Build a 'avg_rent_by_bhk' mapping from rentalDistribution list.
    """
    out: Dict[str, int] = {}
    items = _dig(payload, "data", "localityOverviewData", "insightRates", "rentalDistribution", default=[])
    if isinstance(items, list):
        for it in items:
            unit = it.get("unitType")
            avg = it.get("avgRate")
            if unit:
                out[unit] = _normalize_rent_value(avg) or 0
    return out


def _nearby_localities(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    items = _dig(payload, "nearByLocalities", default=[]) or _dig(payload, "data", "nearByLocalities", default=[])
    if not isinstance(items, list):
        return out
    for it in items:
        try:
            name = it.get("subLocalityName") or it.get("name")
            if not name:
                continue
            sale = it.get("sale", {}) or {}
            rent = it.get("rent", {}) or {}
            metrics = it.get("metrics", {}) or {}
            sale_rank = _dig(metrics, "sale", "rank")
            data = {
                "name": name,
                "rank_in_city": sale_rank,
                "typical_price_psf": sale.get("avgPricePerSqFt"),
                "avg_rent_psf": rent.get("avgPricePerSqFt"),
                "sale_count": sale.get("count"),
                "rent_count": rent.get("count"),
                "url": it.get("url"),
            }
            out.append(data)
        except Exception:
            # be forgiving of partial/odd shapes
            continue
    return out


def _interlinking(payload: Dict[str, Any]) -> Dict[str, List[Dict[str, str]]]:
    """
    Derive interlinking from sale/rent quick links and unit/property type lists.
    """
    def _links(arr: Optional[List[Dict[str, Any]]]) -> List[Dict[str, str]]:
        out: List[Dict[str, str]] = []
        if isinstance(arr, list):
            for x in arr:
                label = x.get("label")
                url = x.get("url")
                if label and url:
                    out.append({"label": label, "href": f"/{url.lstrip('/')}"})
        return out

    sale_footer = _dig(payload, "data", "saleListingFooter", default={})
    rent_footer = _dig(payload, "data", "rentListingFooter", default={})

    primary = _links(sale_footer.get("unitType")) + _links(rent_footer.get("unitType"))
    secondary = _links(_dig(payload, "data", "localityOverviewData", "quickLinks"))
    developer = []  # not present in this JSON; keep empty to avoid repeats

    return {"primary": primary, "secondary": secondary, "developer": developer}


def load_squareyards_json(path: Union[str, Path]) -> Dict[str, Any]:
    """
    Normalize the SquareYards-style JSON (as in whitefield.json) into a flat dict
    with the keys our renderer and inspector expect. Works even if some subtrees
    are missing; values will simply be omitted.
    """
    path = Path(path)
    payload: Dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))

    loc = _dig(payload, "data", "localityOverviewData", default={}) or {}
    if not loc:
        # Some dumps place the tree under top-level
        loc = payload.get("localityOverviewData", {}) or {}

    name = loc.get("name")
    city = loc.get("cityName") or _dig(payload, "data", "localityData", "cityName")
    micromarket = loc.get("dotcomLocationName") or _dig(payload, "data", "localityData", "dotcomLocationName")
    lat, lng = _get_lat_lng(payload)

    # Core counts
    sale_count = loc.get("saleCount")
    rent_count = loc.get("rentCount")
    total_listings = loc.get("totallistings") or loc.get("total")

    # Pricing
    avg_psf = _dig(payload, "data", "localityOverviewData", "insightRates", "avgRate")
    avg_rent = _normalize_rent_value(_dig(payload, "data", "localityOverviewData", "insightRates", "rentalRate"))

    # Ratings
    overall_rating = _dig(payload, "data", "localityOverviewData", "ratingReviewData", "AvgRating")
    review_count = _dig(payload, "data", "localityOverviewData", "ratingReviewData", "ReviewCount")
    rank_in_city = loc.get("rank")

    # Pros / cons from ratingReview (if present)
    pros = _dig(payload, "ratingReview", "good", default=[])
    cons = _dig(payload, "ratingReview", "bad", default=[])

    result: Dict[str, Any] = {
        "locality_name": name,
        "city_name": city,
        "micromarket_name": micromarket,
        "latitude": lat,
        "longitude": lng,
        "locality_rank_in_city": rank_in_city,
        "sale_property_count": sale_count,
        "rent_property_count": rent_count,
        "totallistings": total_listings,
        "avg_sale_price_psf": avg_psf,
        "avg_rent_price": avg_rent,  # monthly INR
        "avg_rent_by_bhk": _rental_distribution(payload),
        "overall_rating": overall_rating,
        "total_review_count": review_count,
        "pros": [{"label": p.get("Name"), "score": p.get("Percentage")} for p in pros if isinstance(p, dict)],
        "cons": [{"label": c.get("Name"), "score": c.get("Percentage")} for c in cons if isinstance(c, dict)],
        "nearby_localities": _nearby_localities(payload),
        "interlinking": _interlinking(payload),
        # Keep raw subtree for anything else downstream may want
        "_raw": payload,
    }
    return result