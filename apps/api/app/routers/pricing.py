from fastapi import APIRouter, Query
from typing import Optional
from app.core.database import get_supabase_client
from app.services.pricing import calculate_pricing_suggestions
from app.schemas.common import SuccessResponse

router = APIRouter(prefix="/pricing", tags=["Pricing Intelligence"])

@router.get("/suggest", response_model=SuccessResponse)
async def suggest_price(
    waste_type_id: str = Query(...),
    quantity: float = Query(10.0, gt=0.0)
):
    """
    Computes fair market pricing bands from completed transaction records.
    Provides median, average, and a recommended price range.
    """
    supabase = get_supabase_client()
    # Fetch historical completed deals for this waste type
    deals_res = supabase.table("deals").select("agreed_price_per_unit, waste_listings!inner(waste_type_id)").eq("stage", "completed").eq("waste_listings.waste_type_id", waste_type_id).execute()

    past_prices = [float(d["agreed_price_per_unit"]) for d in (deals_res.data or [])]
    suggestion = calculate_pricing_suggestions(past_prices)

    return SuccessResponse(data=suggestion)
