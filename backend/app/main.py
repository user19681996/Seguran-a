from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from app.core.config import CORS_ORIGINS
from app.core.rate_limit import check_rate_limit
from app.db.session import ping_db, SessionLocal
from app.db.seed import ensure_seed
from app.routers import auth, events, admin, audit

app = FastAPI(title="ORION FASE 7 Production")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    ping_db()
    db = SessionLocal()
    try:
        ensure_seed(db)
    finally:
        db.close()

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    ip = request.headers.get("x-forwarded-for", "").split(",")[0].strip() or (request.client.host if request.client else "unknown")
    key = f"{ip}:{request.method}:{request.url.path}"
    ok, retry_after = check_rate_limit(key)
    if not ok:
        return JSONResponse({"detail": "Rate limit exceeded", "retry_after": retry_after}, status_code=429, headers={"Retry-After": str(retry_after)})
    return await call_next(request)

@app.get("/")
def root():
    return {"status": "ok", "service": "ORION FASE 7 Production"}

app.include_router(auth.router, prefix="/auth")
app.include_router(events.router, prefix="/api")
app.include_router(admin.router)
app.include_router(audit.router)
