from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os

from app.api import batches, events, procedures, audit_timeline, compliance
from app.api import regulatory_audit as audit, violations, opa, dashboard, execution_routes, evidence
from app.core.database import engine, init_db
from app.models.base import Base
from contextlib import asynccontextmanager
from app.core.database import SessionLocal
from app.core.audit import write_audit_log
from app.core.circuit_breaker import circuit_breaker

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Step 0: Ensure database schema exists (Auto-Migration)
    # This imports all models and creates tables if they don't exist.
    init_db()

    # Step 5: Guarantee a log exists (System Boot)
    db = SessionLocal()
    try:
        write_audit_log(
            db=db,
            action="SYSTEM_BOOT",
            actor="system",
            metadata={"version": "1.0.0"}
        )
    finally:
        db.close()
    yield

app = FastAPI(
    title="ProcGuard API",
    description="Immutable Procedure Enforcement",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/")
def root():
    return {"message": "ProcGuard API is running. Access /docs for API documentation."}

# PHASE 2 - FIX: Add CORS middleware FIRST (ORDER MATTERS)
ALLOWED_ORIGINS = os.getenv(
    "CORS_ALLOWED_ORIGINS",
    "http://localhost:3000,http://127.0.0.1:3000,https://procguard-ui.azurestaticapps.net"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=[
        "Authorization", 
        "Content-Type", 
        "X-Actor-Id", 
        "X-Actor-Role",
        "X-Request-ID",
        "X-Trace-ID",
        "X-Correlation-ID"
    ],
)

# Register Routers (AFTER Middleware)
app.include_router(batches.router, prefix="/batches", tags=["batches"])
app.include_router(events.router, prefix="/batches", tags=["events"])
app.include_router(procedures.router, prefix="/procedures", tags=["procedures"])
app.include_router(audit.router)
app.include_router(audit_timeline.router, prefix="/batches", tags=["timeline"]) 
app.include_router(compliance.router, prefix="/compliance", tags=["compliance"])
app.include_router(violations.router)
app.include_router(opa.router, prefix="/opa", tags=["opa"])
app.include_router(dashboard.router)
app.include_router(execution_routes.router)
app.include_router(evidence.router, tags=["evidence"])

# Exception Handler for global safety
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error", "error": str(exc)},
    )

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/system/health")
def system_health_check():
    """
    Global System Health & Circuit Status.
    """
    return circuit_breaker.get_health_status()

from sqlalchemy.orm import Session
from fastapi import Depends
from app.api.deps import get_db

@app.get("/system/sync/state")
def get_sync_state(db: Session = Depends(get_db)):
    """
    Authoritative Sync Checkpoint State.
    Eliminates "Unknown" states.
    """
    from app.core.sync import sync_manager
    checkpoint = sync_manager.get_latest_checkpoint(db, "audit_events")
    
    return {
        "status": "synchronized" if checkpoint else "bootstrapping",
        "last_checkpoint": {
            "id": str(checkpoint.id),
            "last_event_id": str(checkpoint.last_event_id),
            "committed_at": checkpoint.committed_at.isoformat(),
            "snapshot_version": checkpoint.snapshot_version
        } if checkpoint else None
    }
