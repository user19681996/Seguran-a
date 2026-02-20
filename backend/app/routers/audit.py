from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.rbac import get_db, require_perm
from app.db.models import AuditLog

router = APIRouter(prefix="/audit", tags=["audit"])

@router.get("/logs")
def logs(user_ctx=Depends(require_perm("audit:read")), db: Session = Depends(get_db)):
    rows = db.execute(select(AuditLog).order_by(AuditLog.id.desc()).limit(100)).scalars().all()
    return {"items": [{
        "id": r.id,
        "tenant_id": r.tenant_id,
        "user_id": r.user_id,
        "action": r.action,
        "ip": r.ip,
        "user_agent": r.user_agent,
        "meta": r.meta,
        "created_at": r.created_at.isoformat()
    } for r in rows]}
