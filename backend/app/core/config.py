import os

def _get(name: str, default: str = "") -> str:
    v = os.getenv(name, default)
    return v.strip() if isinstance(v, str) else v

ENV = _get("ENV", "dev")
APP_HOST = _get("APP_HOST", "0.0.0.0")
APP_PORT = int(_get("APP_PORT", "8000"))

DATABASE_URL = _get("DATABASE_URL", "postgresql+psycopg://orion:orion@localhost:5432/orion")

JWT_SECRET = _get("JWT_SECRET", "CHANGE_ME_DEV_SECRET")
ACCESS_TTL_MIN = int(_get("ACCESS_TTL_MIN", "120"))

RATE_LIMIT_PER_MINUTE = int(_get("RATE_LIMIT_PER_MINUTE", "120"))
RATE_LIMIT_BURST = int(_get("RATE_LIMIT_BURST", "60"))

CORS_ORIGINS = [x.strip() for x in _get("CORS_ORIGINS", "http://localhost:8080").split(",") if x.strip()]
