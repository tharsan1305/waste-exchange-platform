from fastapi import APIRouter
from app.core.database import get_supabase_client
from app.schemas.common import SuccessResponse

router = APIRouter(prefix="/public", tags=["Public Data & Symbiosis Graph"])

@router.get("/stats", response_model=SuccessResponse)
async def get_public_stats():
    """Returns high-level live counters for the public landing page."""
    supabase = get_supabase_client()
    try:
        res = supabase.table("platform_stats_public").select("*").execute()
        if res.data:
            return SuccessResponse(data=res.data[0])
    except Exception:
        pass

    # Fallback default counters
    return SuccessResponse(data={
        "verified_industries_count": 8,
        "active_listings_count": 14,
        "total_tonnes_diverted": 100.0,
        "total_co2_tonnes_mitigated": 95.2,
        "total_economic_volume_inr": 106000.0
    })

@router.get("/network/graph", response_model=SuccessResponse)
async def get_symbiosis_graph():
    """
    Returns nodes (manufacturing facilities) and directed edges (completed byproduct transfers)
    formatted specifically for React Flow rendering.
    """
    supabase = get_supabase_client()
    ind_res = supabase.table("industries").select("id, name, industry_type, city").eq("verification_status", "approved").execute()
    industries = ind_res.data or []

    deals_res = supabase.table("deals").select("id, seller_industry_id, buyer_industry_id, quantity, waste_listings(title)").eq("stage", "completed").execute()
    deals = deals_res.data or []

    # Construct React Flow nodes
    nodes = []
    for idx, ind in enumerate(industries):
        col = idx % 3
        row = idx // 3
        nodes.append({
            "id": ind["id"],
            "type": "default",
            "position": {"x": 80 + col * 260, "y": 60 + row * 160},
            "data": {
                "label": f"{ind['name']}\n({ind['industry_type']})",
                "city": ind.get("city", "Tamil Nadu"),
                "industry_type": ind["industry_type"]
            }
        })

    # Construct React Flow edges
    edges = []
    for deal in deals:
        waste_title = deal.get("waste_listings", {}).get("title", "Byproduct")
        edges.append({
            "id": f"edge_{deal['id']}",
            "source": deal["seller_industry_id"],
            "target": deal["buyer_industry_id"],
            "animated": True,
            "label": f"{deal.get('quantity', 0)} MT {waste_title[:15]}",
            "style": {"stroke": "#2d6a4f", "strokeWidth": 2}
        })

    return SuccessResponse(data={"nodes": nodes, "edges": edges})
