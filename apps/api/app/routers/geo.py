from fastapi import APIRouter, Query
from app.services.geo import calculate_transport_estimate, haversine_distance
from app.core.database import get_supabase_client
from app.schemas.common import SuccessResponse

router = APIRouter(prefix="/geo", tags=["Geospatial & Logistics"])

@router.get("/transport-estimate", response_model=SuccessResponse)
async def get_transport_estimate(
    from_lat: float = Query(...),
    from_lng: float = Query(...),
    to_lat: float = Query(...),
    to_lng: float = Query(...),
    tons: float = Query(..., gt=0.0)
):
    """Calculates haulage distance, transit duration, and INR freight estimate."""
    estimate = await calculate_transport_estimate(from_lat, from_lng, to_lat, to_lng, tons)
    return SuccessResponse(data=estimate)

@router.get("/nearby-industries", response_model=SuccessResponse)
async def get_nearby_industries(
    lat: float = Query(...),
    lng: float = Query(...),
    radius_km: float = Query(100.0, gt=0.0)
):
    """Finds verified manufacturing facilities within a given kilometer radius."""
    supabase = get_supabase_client()
    res = supabase.table("industries").select("id, name, industry_type, city, lat, lng, trust_score").eq("verification_status", "approved").execute()
    industries = res.data or []

    nearby = []
    for ind in industries:
        dist = haversine_distance(lat, lng, ind["lat"], ind["lng"])
        if dist <= radius_km:
            ind["distance_km"] = dist
            nearby.append(ind)

    nearby.sort(key=lambda x: x["distance_km"])
    return SuccessResponse(data=nearby)
