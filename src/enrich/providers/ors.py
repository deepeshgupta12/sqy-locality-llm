import os
from typing import Optional
import openrouteservice

def _client() -> openrouteservice.Client:
    key = os.getenv("OPENROUTESERVICE_API_KEY")
    if not key:
        raise RuntimeError("OPENROUTESERVICE_API_KEY not set")
    return openrouteservice.Client(key=key)

def travel_time_minutes(origin_lat: float, origin_lng: float, dest_lat: float, dest_lng: float) -> Optional[float]:
    """
    Returns driving time in minutes using ORS directions (no live traffic).
    """
    try:
        client = _client()
        # ORS expects coordinates as [lon, lat]
        coords = ((origin_lng, origin_lat), (dest_lng, dest_lat))
        res = client.directions(coords, profile='driving-car', format='json')
        secs = res["routes"][0]["summary"]["duration"]
        return round(secs / 60.0, 1)
    except Exception:
        return None
