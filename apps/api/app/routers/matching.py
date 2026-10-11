from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, List
from app.core.deps import get_current_user
from app.core.database import get_supabase_client
from app.services.matching import compute_match_score
from app.schemas.common import SuccessResponse

router = APIRouter(prefix="/matching", tags=["Rule-Based Matching Engine"])

@router.get("/listings/{listing_id}", response_model=SuccessResponse)
async def get_matches_for_listing(listing_id: str):
    """
    Computes top candidate industrial buyers for a given listing using the
    rule-based deterministic algorithm. Returns scores from 0 to 100 with breakdown.
    """
    supabase = get_supabase_client()

    # 1. Fetch listing
    list_res = supabase.table("waste_listings").select("*").eq("id", listing_id).execute()
    if not list_res.data:
        raise HTTPException(status_code=404, detail="Listing not found.")
    listing = list_res.data[0]

    # 2. Fetch usage rules for this waste type
    rules_res = supabase.table("waste_usage_rules").select("*").eq("waste_type_id", listing["waste_type_id"]).execute()
    usage_rules = rules_res.data or []

    # 3. Fetch candidate industries (excluding the seller)
    cand_res = supabase.table("industries").select("*").eq("verification_status", "approved").neq("id", listing["industry_id"]).execute()
    candidates = cand_res.data or []

    # 4. Score all candidates
    matches: List[Dict[str, Any]] = []
    for cand in candidates:
        score_data = compute_match_score(listing, cand, usage_rules)
        matches.append(score_data)

    # Sort descending by match score
    matches.sort(key=lambda x: x["total_match_score"], reverse=True)

    return SuccessResponse(
        message="Top matching industrial facilities computed.",
        data={
            "listing_id": listing_id,
            "waste_type_id": listing["waste_type_id"],
            "total_candidates_analyzed": len(candidates),
            "top_matches": matches[:10]
        }
    )

@router.get("/recommendations", response_model=SuccessResponse)
async def get_buyer_recommendations(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Recommends active byproduct listings tailored to the current authenticated
    industry's manufacturing processes.
    """
    industry = current_user.get("industry")
    if not industry:
        return SuccessResponse(data=[])

    industry_type = industry.get("industry_type", "")
    supabase = get_supabase_client()

    # Find waste types used by this industry type
    rules_res = supabase.table("waste_usage_rules").select("waste_type_id").ilike("industry_type", f"%{industry_type}%").execute()
    waste_type_ids = [r["waste_type_id"] for r in (rules_res.data or [])]

    if not waste_type_ids:
        # Fallback to recent available listings
        fallback_res = supabase.table("waste_listings").select("*, waste_types(name), industries(name, city)").eq("status", "available").limit(6).execute()
        return SuccessResponse(data=fallback_res.data or [])

    rec_res = supabase.table("waste_listings").select("*, waste_types(name), industries(name, city)").eq("status", "available").in_("waste_type_id", waste_type_ids).limit(10).execute()

    return SuccessResponse(data=rec_res.data or [])
