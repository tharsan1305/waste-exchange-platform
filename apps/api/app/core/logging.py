import uuid
import time
import logging
from datetime import datetime, timezone
from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.config import settings

logger = logging.getLogger("waste_exchange")
logging.basicConfig(
    level=logging.INFO,
    format='{"timestamp":"%(asctime)s", "level":"%(levelname)s", "message":"%(message)s"}'
)

class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id
        start_time = time.time()

        try:
            response: Response = await call_next(request)
        except Exception as exc:
            logger.error(f'Unhandled Exception: {str(exc)} | Request ID: {request_id}', exc_info=True)
            return JSONResponse(
                status_code=500,
                content={
                    "error": {
                        "code": "INTERNAL_SERVER_ERROR",
                        "message": "An unexpected system error occurred. Please contact support.",
                        "request_id": request_id,
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
                }
            )

        duration = (time.time() - start_time) * 1000
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time-Ms"] = f"{duration:.2f}"

        # Security Headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        if settings.ENVIRONMENT == "production":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        return response

async def http_exception_handler(request: Request, exc: HTTPException):
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": "REQUEST_ERROR",
                "message": exc.detail,
                "request_id": request_id,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        }
    )
