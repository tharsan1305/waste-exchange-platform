from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.core.rate_limit import limiter
from app.core.logging import RequestContextMiddleware, http_exception_handler

# Routers
from app.routers import (
    auth,
    industries,
    listings,
    matching,
    deals,
    geo,
    pricing,
    dashboard,
    public
)

app = FastAPI(
    title="Waste Exchange Platform API",
    description="Secure B2B Industrial Symbiosis & Byproduct Marketplace API",
    version="1.0.0",
    docs_url="/docs" if settings.ENVIRONMENT == "development" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT == "development" else None
)

# Attach SlowAPI Rate Limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_exception_handler(HTTPException, http_exception_handler)

# Custom Middlewares
app.add_middleware(RequestContextMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Versioned API Routers
api_v1_prefix = "/api/v1"
app.include_router(auth.router, prefix=api_v1_prefix)
app.include_router(industries.router, prefix=api_v1_prefix)
app.include_router(listings.router, prefix=api_v1_prefix)
app.include_router(matching.router, prefix=api_v1_prefix)
app.include_router(deals.router, prefix=api_v1_prefix)
app.include_router(geo.router, prefix=api_v1_prefix)
app.include_router(pricing.router, prefix=api_v1_prefix)
app.include_router(dashboard.router, prefix=api_v1_prefix)
app.include_router(public.router, prefix=api_v1_prefix)

@app.get("/health", tags=["Health"])
async def health_check():
    """Liveness probe endpoint."""
    return {"status": "healthy", "service": "waste-exchange-api", "version": "1.0.0"}

@app.get("/", tags=["Root"])
async def root():
    return {
        "platform": "Waste Exchange Platform",
        "tagline": "One Industry's Waste is Another Industry's Raw Material",
        "docs": "/docs" if settings.ENVIRONMENT == "development" else "Disabled in production"
    }
