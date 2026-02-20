import datetime
from fastapi import APIRouter, Depends, Request, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.rbac import get_db, require_perm
from app.core.audit import write_audit
from app.db.models import Event, Tenant

PLAN_LIMITS = {"FREE": 100, "PRO": 1000, "ENT": 1000000}
router = APIRouter(tags=["events"])

class EventIn(BaseModel):
    severity: str = Field(default="MEDIUM")
    message: str = Field(min_length=3, max_length=300)

@router.get("/me")
def me(user_ctx=Depends(require_perm("events:read"))):
    payload, u = user_ctx
    return {"user_id": payload["user_id"], "tenant_id": payload["tenant_id"], "tenant_slug": payload.get("tenant_slug","")}

@router.get("/usage")
def usage(user_ctx=Depends(require_perm("events:read")), db: Session = Depends(get_db)):
    payload, u = user_ctx
    t = db.get(Tenant, payload["tenant_id"])
    if not t:
        raise HTTPException(status_code=404, detail="Tenant not found")
    start = datetime.datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    used = db.execute(select(Event).where(Event.tenant_id==t.id, Event.created_at>=start)).scalars().all()
    return {"plan": t.plan, "month_used": len(used), "month_limit": PLAN_LIMITS.get(t.plan, 100)}

@router.post("/events")
def create_event(inp: EventIn, request: Request, user_ctx=Depends(require_perm("events:write")), db: Session = Depends(get_db)):
    payload, u = user_ctx
    t = db.get(Tenant, payload["tenant_id"])
    if not t:
        raise HTTPException(status_code=404, detail="Tenant not found")
    start = datetime.datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    used = db.execute(select(Event).where(Event.tenant_id==t.id, Event.created_at>=start)).scalars().all()
    limit = PLAN_LIMITS.get(t.plan, 100)
    if len(used) >= limit:
        raise HTTPException(status_code=402, detail="Plan limit reached. Upgrade required.")
    e = Event(tenant_id=t.id, severity=inp.severity.upper(), message=inp.message, created_at=datetime.datetime.utcnow())
    db.add(e)
    write_audit(db, action="events.create", tenant_id=t.id, user_id=u.id, request=request, meta={"severity": inp.severity})
    db.commit()
    return {"ok": True}

@router.get("/events")
def list_events(user_ctx=Depends(require_perm("events:read")), db: Session = Depends(get_db)):
    payload, u = user_ctx
    rows = db.execute(select(Event).where(Event.tenant_id==payload["tenant_id"]).order_by(Event.id.desc()).limit(50)).scalars().all()
    return {"items": [{"id": r.id, "severity": r.severity, "message": r.message, "created_at": r.created_at.isoformat()} for r in rows]}
