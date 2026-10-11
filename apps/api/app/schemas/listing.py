from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class ListingCreateSchema(BaseModel):
    waste_type_id: str
    title: str = Field(..., min_length=5, max_length=200)
    description: str = Field(..., min_length=10)
    quantity: float = Field(..., gt=0.0)
    unit: str = Field(default="ton", pattern=r'^(kg|ton)$')
    price_per_unit: float = Field(default=0.0, ge=0.0)
    currency: str = Field(default="INR")
    is_hazardous: bool = Field(default=False)
    hazard_class: Optional[str] = None
    is_recurring: bool = Field(default=False)
    recurrence: Optional[str] = Field(default=None, pattern=r'^(weekly|monthly|quarterly)?$')
    expires_at: datetime
    lat: float = Field(..., ge=-90.0, le=90.0)
    lng: float = Field(..., ge=-180.0, le=180.0)
    quality_params: Dict[str, Any] = Field(default_factory=dict)
    images: List[str] = Field(default_factory=list)
