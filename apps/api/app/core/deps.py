from typing import Dict, Any, Optional
from fastapi import Depends, HTTPException, status, Header
from app.core.security import verify_jwt_token
from app.core.database import get_supabase_client
from app.core.config import settings

async def get_current_user(authorization: Optional[str] = Header(None)) -> Dict[str, Any]:
    """
    Extracts and validates Supabase JWT token from the Authorization header.
    Returns user payload along with loaded profile and industry details.
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing."
        )

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization scheme. Use 'Bearer <token>'."
        )

    # In test/dev environments with mock secret
    payload = verify_jwt_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token."
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Malformed token: missing subject claim."
        )

    # Fetch profile & industry context from Supabase
    try:
        supabase = get_supabase_client()
        res = supabase.table("profiles").select("*, industries(*)").eq("id", user_id).execute()
        if res.data and len(res.data) > 0:
            profile = res.data[0]
            industry = profile.get("industries")
            return {
                "id": user_id,
                "email": payload.get("email", ""),
                "role": profile.get("role", "industry_admin"),
                "profile": profile,
                "industry": industry,
                "aal": payload.get("aal", "aal1")
            }
    except Exception:
        pass

    # Fallback to token payload data if offline / initial setup
    return {
        "id": user_id,
        "email": payload.get("email", ""),
        "role": payload.get("user_metadata", {}).get("role", "industry_admin"),
        "profile": {
            "id": user_id,
            "full_name": payload.get("user_metadata", {}).get("full_name", "Demo User"),
            "role": payload.get("user_metadata", {}).get("role", "industry_admin"),
            "industry_id": payload.get("user_metadata", {}).get("industry_id")
        },
        "industry": payload.get("user_metadata", {}).get("industry"),
        "aal": payload.get("aal", "aal1")
    }

def require_role(*required_roles: str):
    """Dependency factory checking that user holds at least one required role (admin, seller, buyer, etc.)."""
    roles_list = set()
    for r in required_roles:
        if isinstance(r, (list, tuple)):
            roles_list.update(r)
        else:
            roles_list.add(r)

    async def role_checker(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
        user_role = current_user.get("role", "")
        # Match direct role or map seller/buyer aliases
        matched = (
            user_role in roles_list
            or user_role == "admin"
            or ("seller" in roles_list and user_role in ("seller", "industry_admin"))
            or ("buyer" in roles_list and user_role in ("buyer", "industry_staff", "industry_admin"))
        )
        if not matched:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: Required role in {list(roles_list)}, current role is '{user_role}'."
            )
        return current_user
    return role_checker

async def require_approved_industry(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """Dependency checking that the user's industry is formally approved."""
    if current_user.get("role") == "admin":
        return current_user

    industry = current_user.get("industry")
    if not industry:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No industry profile associated with this account. Complete onboarding first."
        )

    verification_status = industry.get("verification_status")
    if verification_status != "approved":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Industry verification status is '{verification_status}'. Must be 'approved' to perform this action."
        )

    return current_user

async def require_mfa_for_admin(current_user: Dict[str, Any] = Depends(require_role("admin"))) -> Dict[str, Any]:
    """Ensures administrators have an active AAL2 (MFA verified) session."""
    if current_user.get("aal") != "aal2" and settings.ENVIRONMENT == "production":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrative actions require multi-factor authentication (AAL2)."
        )
    return current_user
