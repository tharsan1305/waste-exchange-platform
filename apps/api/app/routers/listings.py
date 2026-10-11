import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc

from app.core.deps import get_current_user, require_approved_industry
from app.core.database import get_db
from app.services.audit import record_audit_log
from app.schemas.common import SuccessResponse
from app.schemas.listing import ListingCreateSchema
from app.models import WasteListing, Industry, WasteType

router = APIRouter(prefix="/listings", tags=["Waste Listings"])

@router.get("", response_model=SuccessResponse)
async def list_listings(
    category_id: Optional[str] = Query(None),
    waste_type_id: Optional[str] = Query(None),
    is_hazardous: Optional[bool] = Query(None),
    max_price: Optional[float] = Query(None),
    min_quantity: Optional[float] = Query(None),
    search_query: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Searches active listings using SQLAlchemy ORM with multi-dimensional criteria."""
    query = db.query(WasteListing).filter(WasteListing.status == "available")

    if waste_type_id:
        try:
            query = query.filter(WasteListing.waste_type_id == uuid.UUID(waste_type_id))
        except ValueError:
            pass
    if is_hazardous is not None:
        query = query.filter(WasteListing.is_hazardous == is_hazardous)
    if max_price:
        query = query.filter(WasteListing.price_per_unit <= max_price)
    if min_quantity:
        query = query.filter(WasteListing.quantity >= min_quantity)
    if search_query:
        q = f"%{search_query.lower()}%"
        query = query.filter(or_(
            WasteListing.title.ilike(q),
            WasteListing.description.ilike(q)
        ))

    items = query.order_by(desc(WasteListing.created_at)).limit(50).all()

    data = []
    for item in items:
        data.append({
            "id": str(item.id),
            "title": item.title,
            "description": item.description,
            "quantity": item.quantity,
            "unit": item.unit,
            "price_per_unit": item.price_per_unit,
            "currency": item.currency,
            "is_hazardous": item.is_hazardous,
            "batch_code": item.batch_code,
            "qr_path": item.qr_path,
            "status": item.status,
            "lat": item.lat,
            "lng": item.lng,
            "industry": {
                "name": item.industry.name if item.industry else "Verified Mill",
                "city": item.industry.city if item.industry else "Tamil Nadu",
                "trust_score": item.industry.trust_score if item.industry else 5.0
            } if item.industry else None,
            "waste_types": {
                "name": item.waste_type.name if item.waste_type else "Byproduct"
            } if item.waste_type else None
        })

    return SuccessResponse(data=data)

@router.post("", response_model=SuccessResponse, status_code=status.HTTP_201_CREATED)
async def create_listing(
    payload: ListingCreateSchema,
    current_user: Dict[str, Any] = Depends(require_approved_industry),
    db: Session = Depends(get_db)
):
    """
    Creates a new byproduct waste listing via SQLAlchemy.
    Only approved industries can publish. Hazardous items require PCB authorization.
    """
    industry = current_user.get("industry", {})
    industry_id_val = industry.get("id")

    if not industry_id_val:
        raise HTTPException(status_code=400, detail="User is not linked to an industry.")

    # Hazardous check: seller must have pcb_authorization_no
    if payload.is_hazardous and not industry.get("pcb_authorization_no"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Hazardous waste listings strictly require a verified PCB Authorization Number in your industry profile."
        )

    # Generate unique Batch Code & QR path
    batch_suffix = str(uuid.uuid4())[:8].upper()
    batch_code = f"BATCH-{datetime.now().strftime('%Y%m')}-{batch_suffix}"
    qr_path = f"qr-codes/{batch_code}.png"

    listing_id = uuid.uuid4()
    new_listing = WasteListing(
        id=listing_id,
        industry_id=uuid.UUID(str(industry_id_val)),
        waste_type_id=uuid.UUID(payload.waste_type_id),
        title=payload.title,
        description=payload.description,
        quantity=payload.quantity,
        unit=payload.unit,
        price_per_unit=payload.price_per_unit,
        currency=payload.currency,
        is_hazardous=payload.is_hazardous,
        hazard_class=payload.hazard_class,
        is_recurring=payload.is_recurring,
        recurrence=payload.recurrence,
        expires_at=payload.expires_at,
        status="available",
        batch_code=batch_code,
        qr_path=qr_path,
        lat=payload.lat,
        lng=payload.lng,
        quality_params=payload.quality_params
    )

    db.add(new_listing)
    db.commit()
    db.refresh(new_listing)

    await record_audit_log(
        action="CREATE_LISTING",
        entity_type="waste_listings",
        entity_id=str(listing_id),
        actor_user_id=current_user["id"],
        actor_role=current_user.get("role", "industry_admin"),
        after=payload.model_dump()
    )

    return SuccessResponse(
        message="Listing published successfully.",
        data={"listing_id": str(listing_id), "batch_code": batch_code, "qr_path": qr_path}
    )

@router.get("/{listing_id}", response_model=SuccessResponse)
async def get_listing_detail(listing_id: str, db: Session = Depends(get_db)):
    """Retrieves full specification details, quality test parameters, and seller credentials."""
    try:
        lid = uuid.UUID(listing_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid listing UUID.")

    item = db.query(WasteListing).filter(WasteListing.id == lid).first()
    if not item:
        raise HTTPException(status_code=404, detail="Listing not found.")

    return SuccessResponse(data={
        "id": str(item.id),
        "title": item.title,
        "description": item.description,
        "quantity": item.quantity,
        "unit": item.unit,
        "price_per_unit": item.price_per_unit,
        "is_hazardous": item.is_hazardous,
        "batch_code": item.batch_code,
        "qr_path": item.qr_path,
        "lat": item.lat,
        "lng": item.lng,
        "quality_params": item.quality_params,
        "status": item.status,
        "industry": {
            "id": str(item.industry.id) if item.industry else None,
            "name": item.industry.name if item.industry else None,
            "city": item.industry.city if item.industry else None,
            "trust_score": item.industry.trust_score if item.industry else 5.0,
            "verification_status": item.industry.verification_status if item.industry else "pending"
        } if item.industry else None,
        "waste_types": {
            "id": str(item.waste_type.id) if item.waste_type else None,
            "name": item.waste_type.name if item.waste_type else None
        } if item.waste_type else None
    })

@router.get("/passport/{batch_code}", response_model=SuccessResponse)
async def get_waste_passport(batch_code: str, db: Session = Depends(get_db)):
    """Public QR landing page endpoint: verifies origin and quality parameters."""
    item = db.query(WasteListing).filter(WasteListing.batch_code == batch_code).first()
    if not item:
        raise HTTPException(status_code=404, detail="Invalid waste passport batch code.")

    return SuccessResponse(data={
        "id": str(item.id),
        "title": item.title,
        "quantity": item.quantity,
        "unit": item.unit,
        "price_per_unit": item.price_per_unit,
        "batch_code": item.batch_code,
        "is_hazardous": item.is_hazardous,
        "quality_params": item.quality_params,
        "created_at": item.created_at.isoformat() if item.created_at else None,
        "industry": {
            "name": item.industry.name if item.industry else None,
            "city": item.industry.city if item.industry else None,
            "verification_status": item.industry.verification_status if item.industry else "pending",
            "trust_score": item.industry.trust_score if item.industry else 5.0
        } if item.industry else None,
        "waste_types": {
            "name": item.waste_type.name if item.waste_type else None
        } if item.waste_type else None
    })
