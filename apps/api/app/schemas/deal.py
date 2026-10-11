from pydantic import BaseModel, Field
from typing import Optional

class RequestCreateSchema(BaseModel):
    listing_id: str
    quantity: float = Field(..., gt=0.0)
    offered_price: float = Field(..., ge=0.0)
    message: Optional[str] = None

class DealStageUpdateSchema(BaseModel):
    to_stage: str = Field(..., pattern=r'^(agreed|payment_confirmed|pickup_scheduled|delivered|completed|cancelled|disputed)$')
    note: Optional[str] = None
    vehicle_number: Optional[str] = None
    transporter_name: Optional[str] = None
    transporter_pcb_auth_no: Optional[str] = None
