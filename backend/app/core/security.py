import datetime
from typing import Dict, Any
import jwt
from passlib.context import CryptContext
from app.core.config import JWT_SECRET, ACCESS_TTL_MIN

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(pw: str) -> str:
    return pwd_context.hash(pw)

def verify_password(pw: str, pw_hash: str) -> bool:
    return pwd_context.verify(pw, pw_hash)

def make_token(payload: Dict[str, Any]) -> str:
    exp = datetime.datetime.utcnow() + datetime.timedelta(minutes=ACCESS_TTL_MIN)
    p = dict(payload)
    p["exp"] = exp
    return jwt.encode(p, JWT_SECRET, algorithm="HS256")

def decode_token(token: str) -> Dict[str, Any]:
    return jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
