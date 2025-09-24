import os, requests, math
from typing import Dict, Any, List, Tuple

OVERPASS = os.getenv("OVERPASS_ENDPOINT", "https://overpass-api.de/api/interpreter")

def _poly_from_geojson(boundary: Dict[str, Any]) -> str:
    # GeoJSON ring is [[lng, lat], ...]; Overpass wants "lat lon" pairs
    coords = boundary["coordinates"][0]
    return " ".join([f"{lat} {lng}" for lng, lat in coords])

def _haversine_km(a: Tuple[float,float], b: Tuple[float,float]) -> float:
    R=6371.0
    la1,lo1=a; la2,lo2=b
    p1=math.radians(la1); p2=math.radians(la2)
    dphi=math.radians(la2-la1); dl=math.radians(lo2-lo1)
    h=math.sin(dphi/2)**2+math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2*R*math.asin(min(1,math.sqrt(h)))

def _fetch(q: str) -> Dict[str, Any]:
    r = requests.post(OVERPASS, data={"data": q}, timeout=60)
    r.raise_for_status()
    return r.json()

def _amenity_query(poly: str, keys: List[str]) -> str:
    ors = "".join([
        f'node["amenity"="{k}"](poly:"{poly}");'
        f'way["amenity"="{k}"](poly:"{poly}");'
        f'relation["amenity"="{k}"](poly:"{poly}");'
        for k in keys
    ])
    return f"[out:json][timeout:60];({ors});out center 30;"

def get_pois(boundary: Dict[str, Any], centroid_lnglat: Tuple[float,float], keys: List[str], limit:int=5) -> List[Dict[str,Any]]:
    # centroid_lnglat = (lng, lat)
    poly = _poly_from_geojson(boundary)
    data = _fetch(_amenity_query(poly, keys))
    els = data.get("elements", [])
    pois=[]
    for el in els:
        tags = el.get("tags",{})
        name = tags.get("name")
        lat = el.get("lat") or el.get("center",{}).get("lat")
        lon = el.get("lon") or el.get("center",{}).get("lon")
        if not name or lat is None or lon is None:
            continue
        d = _haversine_km((centroid_lnglat[1], centroid_lnglat[0]), (lat, lon))
        pois.append({"name": name, "distance_km": round(d,2)})
    pois.sort(key=lambda x: x["distance_km"])
    return pois[:limit]
