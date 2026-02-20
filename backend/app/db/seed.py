import datetime
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db.models import Tenant, Role, Permission, RolePermission, User
from app.core.security import hash_password

DEFAULT_PERMS = [
    ("events:read", "Read events"),
    ("events:write", "Create events"),
    ("admin:tenants:read", "List tenants (master)"),
    ("admin:tenants:write", "Update tenant plan (master)"),
    ("audit:read", "Read audit logs"),
]

ROLE_MAP = {
    "user": ["events:read"],
    "admin": ["events:read", "events:write", "audit:read"],
    "master": ["events:read", "events:write", "audit:read", "admin:tenants:read", "admin:tenants:write"],
}

def ensure_seed(db: Session):
    roles = {}
    for rname in ["user","admin","master"]:
        r = db.execute(select(Role).where(Role.name==rname)).scalar_one_or_none()
        if not r:
            r = Role(name=rname, description=f"{rname} role")
            db.add(r); db.flush()
        roles[rname] = r

    perms = {}
    for code, desc in DEFAULT_PERMS:
        p = db.execute(select(Permission).where(Permission.code==code)).scalar_one_or_none()
        if not p:
            p = Permission(code=code, description=desc)
            db.add(p); db.flush()
        perms[code] = p

    for rname, codes in ROLE_MAP.items():
        r = roles[rname]
        for code in codes:
            p = perms[code]
            rp = db.execute(select(RolePermission).where(RolePermission.role_id==r.id, RolePermission.permission_id==p.id)).scalar_one_or_none()
            if not rp:
                db.add(RolePermission(role_id=r.id, permission_id=p.id))

    t = db.execute(select(Tenant).where(Tenant.slug=="orion-master")).scalar_one_or_none()
    if not t:
        t = Tenant(name="ORION Master", slug="orion-master", country="BR", plan="ENT", subscription_status="active", created_at=datetime.datetime.utcnow())
        db.add(t); db.flush()

    u = db.execute(select(User).where(User.tenant_id==t.id, User.email=="master@orion.local")).scalar_one_or_none()
    if not u:
        u = User(tenant_id=t.id, email="master@orion.local", password_hash=hash_password("admin123!"), role_id=roles["master"].id, created_at=datetime.datetime.utcnow())
        db.add(u)

    db.commit()
