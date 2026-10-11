from fastapi import APIRouter, Depends
from typing import Dict, Any
from app.core.deps import get_current_user, require_role
from app.core.database import get_supabase_client
from app.schemas.common import SuccessResponse

router = APIRouter(prefix="/dashboard", tags=["Dashboards & Analytics"])

@router.get("/industry", response_model=SuccessResponse)
async def get_industry_dashboard(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Returns ESG KPIs and transaction summaries for the authenticated company."""
    industry_id = current_user.get("industry", {}).get("id")
    supabase = get_supabase_client()

    # Query completed deals for this industry
    deals_res = supabase.table("deals").select("*").eq("stage", "completed").or_(f"seller_industry_id.eq.{industry_id},buyer_industry_id.eq.{industry_id}").execute()
    deals = deals_res.data or []

    total_co2_kg = sum(float(d.get("co2_saved_kg", 0)) for d in deals)
    total_landfill_kg = sum(float(d.get("landfill_diverted_kg", 0)) for d in deals)
    total_savings_inr = sum(float(d.get("money_saved", 0)) for d in deals)
    total_volume_tons = sum(float(d.get("quantity", 0)) for d in deals)

    return SuccessResponse(data={
        "total_deals_completed": len(deals),
        "total_waste_diverted_tonnes": round(total_landfill_kg / 1000.0, 2),
        "total_co2_saved_tonnes": round(total_co2_kg / 1000.0, 2),
        "total_money_saved_inr": total_savings_inr,
        "total_volume_tons": total_volume_tons,
        "recent_deals": deals[:5]
    })

@router.get("/admin", response_model=SuccessResponse)
async def get_admin_dashboard(admin_user: Dict[str, Any] = Depends(require_role("admin"))):
    """(Admin Only) Platform-wide operations dashboard: verifications, fraud flags, disputes."""
    supabase = get_supabase_client()

    pending_ind = supabase.table("industries").select("id", count="exact").eq("verification_status", "pending").execute()
    open_complaints = supabase.table("complaints").select("id", count="exact").eq("status", "open").execute()
    fraud_flags = supabase.table("fraud_flags").select("id", count="exact").eq("status", "open").execute()

    return SuccessResponse(data={
        "pending_verifications_count": pending_ind.count or 0,
        "open_disputes_count": open_complaints.count or 0,
        "active_fraud_alerts_count": fraud_flags.count or 0
    })
