from pydantic import BaseModel, Field, EmailStr
from typing import Optional

class IndustryCreateSchema(BaseModel):
    name: str = Field(..., min_length=2, max_length=200)
    gst_number: str = Field(..., pattern=r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$')
    license_number: Optional[str] = None
    industry_type: str = Field(..., min_length=2, max_length=100)
    address: str = Field(..., min_length=5)
    city: str = Field(..., min_length=2)
    state: str = Field(default="Tamil Nadu")
    pincode: str = Field(..., min_length=6, max_length=6)
    lat: float = Field(..., ge=-90.0, le=90.0)
    lng: float = Field(..., ge=-180.0, le=180.0)
    contact_email: EmailStr
    contact_phone: str = Field(..., min_length=10)
    pcb_authorization_no: Optional[str] = None

class IndustryVerificationSchema(BaseModel):
    status: str = Field(..., pattern=r'^(approved|rejected|suspended)$')
    rejection_reason: Optional[str] = None
