import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from .core.config import settings
from .core.logging import configure_logging
from .core import rate_limit
from .db.session import init_db
from .api.v1.routes.auth import router as auth_router
from .api.v1.routes.metrics import router as metrics_router
from .api.v1.routes.runs import router as runs_router
from .api.v1.routes.analysis import router as analysis_router
from .api.v1.routes.mitigations import router as mitigations_router
from .api.v1.routes.audit import router as audit_router

configure_logging()

app = FastAPI(title="RegimeShift Sentinel", version="1.0.0", openapi_url="/api/v1/openapi.json")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def enforce_rate_limit(request: Request, call_next):
    if request.url.path.startswith("/api/v1"):
        client_ip = request.client.host if request.client else "unknown"
        key = f"ip:{client_ip}"
        if rate_limit.rate_limiter and not rate_limit.rate_limiter.allow(key):
            return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded"})
    return await call_next(request)

# API v1 routers
app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"]) 
app.include_router(metrics_router, prefix="/api/v1", tags=["metrics"]) 
app.include_router(runs_router, prefix="/api/v1", tags=["runs"]) 
app.include_router(analysis_router, prefix="/api/v1", tags=["analysis"]) 
app.include_router(mitigations_router, prefix="/api/v1", tags=["mitigations"]) 
app.include_router(audit_router, prefix="/api/v1", tags=["audit"]) 


@app.on_event("startup")
async def on_startup():
    if settings.ENV == "test" or os.getenv("RSS_SKIP_STARTUP") == "1":
        return
    rate_limit.init_rate_limiter()
    await init_db()

@app.get("/healthz")
def healthcheck():
    return {"status": "ok"}


@app.get("/api/v1")
def api_root():
    return {
        "status": "ok",
        "openapi": "/api/v1/openapi.json",
        "docs": "/docs",
    }
