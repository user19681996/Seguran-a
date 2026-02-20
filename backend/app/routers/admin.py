from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.rbac import get_db, require_perm
from app.core.audit import write_audit
from app.db.models import Tenant

router = APIRouter(prefix="/admin", tags=["admin"])

class UpdatePlanIn(BaseModel):
    tenant_id: int
    plan: str = Field(pattern="^(FREE|PRO|ENT)$")
    subscription_status: str = Field(default="active")

@router.get("/tenants")
def tenants(user_ctx=Depends(require_perm("admin:tenants:read")), db: Session = Depends(get_db)):
    rows = db.execute(select(Tenant).order_by(Tenant.id.desc()).limit(200)).scalars().all()
    return {"items": [{"id": t.id, "name": t.name, "slug": t.slug, "country": t.country, "plan": t.plan, "subscription_status": t.subscription_status} for t in rows]}

@router.post("/tenant_plan")
def update_plan(inp: UpdatePlanIn, request: Request, user_ctx=Depends(require_perm("admin:tenants:write")), db: Session = Depends(get_db)):
    payload, u = user_ctx
    t = db.get(Tenant, inp.tenant_id)
    if not t:
        raise HTTPException(status_code=404, detail="Tenant not found")
    t.plan = inp.plan
    t.subscription_status = inp.subscription_status
    write_audit(db, action="admin.tenant_plan_update", tenant_id=t.id, user_id=u.id, request=request, meta={"plan": inp.plan})
    db.commit()
    return {"ok": True}
