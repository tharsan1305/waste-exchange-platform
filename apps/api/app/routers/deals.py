from fastapi import APIRouter, Depends, HTTPException, Response, status
from typing import Dict, Any, List
from app.core.deps import get_current_user
from app.core.database import get_supabase_client
from app.core.security import mask_contact_info
from app.services.audit import record_audit_log
from app.services.carbon import compute_esg_impact
from app.services.manifest import generate_deal_manifest_pdf
from app.schemas.common import SuccessResponse
from app.schemas.deal import DealStageUpdateSchema

router = APIRouter(prefix="/deals", tags=["Deals & Manifests"])

ALLOWED_TRANSITIONS = {
    "negotiation": ["agreed", "cancelled"],
    "agreed": ["payment_confirmed", "cancelled"],
    "payment_confirmed": ["pickup_scheduled", "disputed"],
    "pickup_scheduled": ["delivered", "disputed"],
    "delivered": ["completed", "disputed"],
    "disputed": ["agreed", "cancelled"],
    "completed": [],
    "cancelled": []
}

@router.get("", response_model=SuccessResponse)
async def list_deals(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Lists all contracts where current industry is buyer or seller."""
    industry_id = current_user.get("industry", {}).get("id")
    supabase = get_supabase_client()

    query = supabase.table("deals").select(
        "*, seller:seller_industry_id(name, city), buyer:buyer_industry_id(name, city), waste_listings(title, waste_types(name))"
    )
    if current_user.get("role") != "admin" and industry_id:
        query = query.or_(f"seller_industry_id.eq.{industry_id},buyer_industry_id.eq.{industry_id}")

    res = query.order("created_at", desc=True).execute()
    return SuccessResponse(data=res.data or [])

@router.get("/{deal_id}", response_model=SuccessResponse)
async def get_deal_detail(deal_id: str, current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Returns full contract details. Counterparty phone and email are unmasked
    ONLY IF deal stage is 'agreed' or beyond.
    """
    industry_id = current_user.get("industry", {}).get("id")
    supabase = get_supabase_client()

    res = supabase.table("deals").select(
        "*, seller:seller_industry_id(*), buyer:buyer_industry_id(*), waste_listings(*)"
    ).eq("id", deal_id).execute()

    if not res.data:
        raise HTTPException(status_code=404, detail="Deal not found.")

    deal = res.data[0]
    is_admin = current_user.get("role") == "admin"
    is_participant = (deal["seller_industry_id"] == industry_id) or (deal["buyer_industry_id"] == industry_id)

    if not is_admin and not is_participant:
        raise HTTPException(status_code=403, detail="Access denied to this contract.")

    # Data Masking: Hide counterparty phone/email during negotiation stage
    is_revealed = deal["stage"] in ["agreed", "payment_confirmed", "pickup_scheduled", "delivered", "completed"]
    if not is_revealed and not is_admin:
        if deal.get("seller"):
            p, e = mask_contact_info(deal["seller"]["contact_phone"], deal["seller"]["contact_email"])
            deal["seller"]["contact_phone"] = p
            deal["seller"]["contact_email"] = e
        if deal.get("buyer"):
            p, e = mask_contact_info(deal["buyer"]["contact_phone"], deal["buyer"]["contact_email"])
            deal["buyer"]["contact_phone"] = p
            deal["buyer"]["contact_email"] = e

    return SuccessResponse(data=deal)

@router.put("/{deal_id}/stage", response_model=SuccessResponse)
async def transition_deal_stage(
    deal_id: str,
    payload: DealStageUpdateSchema,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Strict stage state machine transition.
    Computes ESG impact metrics when stage transitions to 'completed'.
    """
    supabase = get_supabase_client()
    deal_res = supabase.table("deals").select("*, waste_listings(waste_type_id)").eq("id", deal_id).execute()
    if not deal_res.data:
        raise HTTPException(status_code=404, detail="Deal not found.")

    deal = deal_res.data[0]
    current_stage = deal["stage"]
    allowed = ALLOWED_TRANSITIONS.get(current_stage, [])

    if payload.to_stage not in allowed and current_user.get("role") != "admin":
        raise HTTPException(
            status_code=400,
            detail=f"Illegal stage transition from '{current_stage}' to '{payload.to_stage}'. Allowed: {allowed}"
        )

    update_payload: Dict[str, Any] = {"stage": payload.to_stage}
    if payload.vehicle_number:
        update_payload["vehicle_number"] = payload.vehicle_number
    if payload.transporter_name:
        update_payload["transporter_name"] = payload.transporter_name
    if payload.transporter_pcb_auth_no:
        update_payload["transporter_pcb_auth_no"] = payload.transporter_pcb_auth_no

    # On completed: calculate and record verified ESG metrics
    if payload.to_stage == "completed":
        quantity = float(deal.get("quantity", 0.0))
        agreed_price = float(deal.get("agreed_price_per_unit", 0.0))
        waste_type_id = deal.get("waste_listings", {}).get("waste_type_id")

        # Fetch emission factor
        factor = 850.0  # Default fallback kg CO2/ton
        if waste_type_id:
            ef_res = supabase.table("emission_factors").select("kg_co2e_avoided_per_ton").eq("waste_type_id", waste_type_id).execute()
            if ef_res.data:
                factor = float(ef_res.data[0]["kg_co2e_avoided_per_ton"])

        esg = compute_esg_impact(quantity, factor, agreed_price_per_ton=agreed_price)
        update_payload["co2_saved_kg"] = esg["co2_saved_kg"]
        update_payload["landfill_diverted_kg"] = esg["landfill_diverted_kg"]
        update_payload["money_saved"] = esg["buyer_savings_inr"]

    supabase.table("deals").update(update_payload).eq("id", deal_id).execute()

    # Record stage history
    supabase.table("deal_stage_history").insert({
        "deal_id": deal_id,
        "from_stage": current_stage,
        "to_stage": payload.to_stage,
        "changed_by": current_user["id"],
        "note": payload.note
    }).execute()

    await record_audit_log(
        action=f"DEAL_STAGE_{payload.to_stage.upper()}",
        entity_type="deals",
        entity_id=deal_id,
        actor_user_id=current_user["id"],
        actor_role=current_user["role"],
        after=update_payload
    )

    return SuccessResponse(
        message=f"Deal transitioned to '{payload.to_stage}'.",
        data={"deal_id": deal_id, "stage": payload.to_stage}
    )

@router.get("/{deal_id}/manifest")
async def get_or_generate_manifest(deal_id: str, current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Generates or retrieves the cryptographic e-Challan consignment manifest PDF
    with embedded QR code and SHA-256 fingerprint.
    """
    supabase = get_supabase_client()
    res = supabase.table("deals").select(
        "*, seller:seller_industry_id(*), buyer:buyer_industry_id(*), waste_listings(title, batch_code, is_hazardous)"
    ).eq("id", deal_id).execute()

    if not res.data:
        raise HTTPException(status_code=404, detail="Deal not found.")

    deal = res.data[0]
    manifest_input = {
        "id": deal["id"],
        "stage": deal["stage"],
        "batch_code": deal.get("waste_listings", {}).get("batch_code", "BATCH-GEN"),
        "waste_name": deal.get("waste_listings", {}).get("title", "Industrial Byproduct"),
        "is_hazardous": deal.get("waste_listings", {}).get("is_hazardous", False),
        "quantity": deal["quantity"],
        "agreed_price_per_unit": deal["agreed_price_per_unit"],
        "total_amount": deal["total_amount"],
        "vehicle_number": deal.get("vehicle_number", "TN-ASSIGNED-TRANS"),
        "transporter_name": deal.get("transporter_name", "Authorized Roadways"),
        "transporter_pcb_auth_no": deal.get("transporter_pcb_auth_no", "PCB/TN/TRANS/01"),
        "seller": deal.get("seller", {}),
        "buyer": deal.get("buyer", {})
    }

    pdf_bytes, sha256_hash = generate_deal_manifest_pdf(manifest_input)

    # Store manifest hash in DB if not already present
    supabase.table("manifests").upsert({
        "deal_id": deal_id,
        "pdf_path": f"manifests/{deal_id}.pdf",
        "sha256_hash": sha256_hash
    }, on_conflict="deal_id").execute()

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"inline; filename=manifest_{deal_id[:8]}.pdf",
            "X-Document-SHA256": sha256_hash
        }
    )
