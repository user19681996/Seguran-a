from typing import Set
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import decode_token
from app.db.session import SessionLocal
from app.db.models import RolePermission, Permission, User

security = HTTPBearer()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def current_user(creds: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    try:
        payload = decode_token(creds.credentials)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")
    u = db.get(User, int(payload.get("user_id", 0)))
    if not u:
        raise HTTPException(status_code=401, detail="User not found")
    return payload, u

def permissions_for_role(db: Session, role_id: int) -> Set[str]:
    stmt = (
        select(Permission.code)
        .join(RolePermission, RolePermission.permission_id == Permission.id)
        .where(RolePermission.role_id == role_id)
    )
    return set([r[0] for r in db.execute(stmt).all()])

def require_perm(code: str):
    def _inner(user_ctx=Depends(current_user), db: Session = Depends(get_db)):
        payload, u = user_ctx
        perms = permissions_for_role(db, u.role_id)
        if code not in perms:
            raise HTTPException(status_code=403, detail=f"Missing permission: {code}")
        return payload, u
    return _inner
