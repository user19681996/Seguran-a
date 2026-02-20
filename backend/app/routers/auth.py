import datetime, re
from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel, Field, EmailStr
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.security import hash_password, verify_password, make_token
from app.core.audit import write_audit
from app.db.session import SessionLocal
from app.db.models import Tenant, User, Role
from app.db.seed import ensure_seed

router = APIRouter(tags=["auth"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def slugify(name: str) -> str:
    s = name.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s or "tenant"

class RegisterCompanyIn(BaseModel):
    company_name: str = Field(min_length=2, max_length=120)
    country: str = Field(default="BR", min_length=2, max_length=2)
    admin_email: EmailStr
    admin_password: str = Field(min_length=8, max_length=64)

class LoginIn(BaseModel):
    tenant_slug: str
    email: EmailStr
    password: str

@router.post("/register_company")
def register_company(inp: RegisterCompanyIn, request: Request, db: Session = Depends(get_db)):
    ensure_seed(db)
    slug = slugify(inp.company_name)
    base = slug
    i = 1
    while db.execute(select(Tenant).where(Tenant.slug==slug)).scalar_one_or_none():
        i += 1
        slug = f"{base}-{i}"
    t = Tenant(name=inp.company_name, slug=slug, country=inp.country.upper(), plan="FREE", subscription_status="inactive", created_at=datetime.datetime.utcnow())
    db.add(t); db.flush()
    admin_role = db.execute(select(Role).where(Role.name=="admin")).scalar_one()
    u = User(tenant_id=t.id, email=inp.admin_email.lower(), password_hash=hash_password(inp.admin_password), role_id=admin_role.id, created_at=datetime.datetime.utcnow())
    db.add(u)
    write_audit(db, action="tenant.register", tenant_id=t.id, request=request, meta={"slug": slug})
    db.commit()
    return {"tenant_slug": slug, "message": "Company created. Please login."}

@router.post("/login")
def login(inp: LoginIn, request: Request, db: Session = Depends(get_db)):
    ensure_seed(db)
    t = db.execute(select(Tenant).where(Tenant.slug==inp.tenant_slug)).scalar_one_or_none()
    if not t:
        raise HTTPException(status_code=404, detail="Tenant not found")
    u = db.execute(select(User).where(User.tenant_id==t.id, User.email==inp.email.lower())).scalar_one_or_none()
    if not u or not verify_password(inp.password, u.password_hash):
        write_audit(db, action="auth.login_failed", tenant_id=t.id, request=request, meta={"email": inp.email.lower()})
        db.commit()
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = make_token({"user_id": u.id, "tenant_id": t.id, "tenant_slug": t.slug})
    write_audit(db, action="auth.login_ok", tenant_id=t.id, user_id=u.id, request=request, meta={})
    db.commit()
    return {"access_token": token}
