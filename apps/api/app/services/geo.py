import math
from typing import Dict, Any
import httpx
from app.core.config import settings

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Computes great-circle distance between two GPS points in kilometers.
    """
    r = 6371.0  # Earth's mean radius in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(r * c, 2)

async def calculate_transport_estimate(
    from_lat: float, from_lng: float,
    to_lat: float, to_lng: float,
    quantity_tons: float
) -> Dict[str, Any]:
    """
    Estimates distance, estimated duration, and haulage freight cost in INR.
    Tries OSRM public demo endpoint first; falls back gracefully to Haversine.
    """
    distance_km = haversine_distance(from_lat, from_lng, to_lat, to_lng)
    duration_minutes = (distance_km / 40.0) * 60.0  # Assuming 40 km/h avg commercial truck speed

    # Try OSRM if accessible
    try:
        url = f"{settings.OSRM_ENDPOINT}/route/v1/driving/{from_lng},{from_lat};{to_lng},{to_lat}?overview=false"
        async with httpx.AsyncClient(timeout=2.0) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("routes"):
                    route = data["routes"][0]
                    distance_km = round(route["distance"] / 1000.0, 2)
                    duration_minutes = round(route["duration"] / 60.0, 1)
    except Exception:
        pass  # Fall back to Haversine straight-line distance

    # Transport cost formula: Base Fare + (Distance km * Per-km-ton Rate * Tons)
    variable_cost = distance_km * settings.PER_KM_TON_RATE * max(quantity_tons, 1.0)
    total_cost_inr = round(settings.BASE_TRANSPORT_FARE + variable_cost, 2)

    return {
        "distance_km": distance_km,
        "estimated_duration_hours": round(duration_minutes / 60.0, 2),
        "quantity_tons": quantity_tons,
        "base_fare_inr": settings.BASE_TRANSPORT_FARE,
        "per_km_ton_rate_inr": settings.PER_KM_TON_RATE,
        "total_estimated_freight_inr": total_cost_inr
    }
