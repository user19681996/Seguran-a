import json
from fastapi import Request
from sqlalchemy.orm import Session
from app.db.models import AuditLog

def write_audit(db: Session, *, action: str, tenant_id=None, user_id=None, request: Request=None, meta=None):
    ip = ""
    ua = ""
    if request is not None:
        ip = request.headers.get("x-forwarded-for", "").split(",")[0].strip() or (request.client.host if request.client else "")
        ua = (request.headers.get("user-agent","") or "")[:255]
    db.add(AuditLog(
        tenant_id=tenant_id,
        user_id=user_id,
        action=action,
        ip=ip,
        user_agent=ua,
        meta=json.dumps(meta or {}),
    ))
