from typing import Optional, Dict, Any
from app.core.database import get_supabase_client
from app.core.logging import logger

async def record_audit_log(
    action: str,
    entity_type: str,
    entity_id: Optional[str] = None,
    actor_user_id: Optional[str] = None,
    actor_role: Optional[str] = None,
    ip: str = "127.0.0.1",
    user_agent: Optional[str] = None,
    before: Optional[Dict[str, Any]] = None,
    after: Optional[Dict[str, Any]] = None
) -> None:
    """
    Appends an immutable entry to the audit_logs table.
    Ensures non-repudiation for security, administrative actions, and contract events.
    """
    try:
        supabase = get_supabase_client()
        supabase.table("audit_logs").insert({
            "action": action,
            "entity_type": entity_type,
            "entity_id": str(entity_id) if entity_id else None,
            "actor_user_id": str(actor_user_id) if actor_user_id else None,
            "actor_role": actor_role,
            "ip": ip,
            "user_agent": user_agent,
            "before": before,
            "after": after
        }).execute()
    except Exception as e:
        logger.error(f"Failed to record audit log: {str(e)}")
