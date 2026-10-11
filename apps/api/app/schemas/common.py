from pydantic import BaseModel, Field
from typing import Optional, Any

class SuccessResponse(BaseModel):
    success: bool = True
    message: str = "Operation completed successfully."
    data: Optional[Any] = None

class ErrorDetail(BaseModel):
    code: str
    message: str
    request_id: Optional[str] = None
    timestamp: str

class ErrorResponse(BaseModel):
    error: ErrorDetail
