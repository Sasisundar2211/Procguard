from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api import batches, events, procedures, audit_timeline # Removed audit_logs
from app.database import engine, Base
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="ProcGuard API",
    description="Immutable Procedure Enforcement",
    version="1.0.0"
)
# Register Routers
app.include_router(batches.router, prefix="/batches", tags=["batches"])
app.include_router(events.router, prefix="/batches", tags=["events"]) #/batches/{id}/events
app.include_router(procedures.router, prefix="/procedures", tags=["procedures"])
from app.api import audit
app.include_router(audit.router)
app.include_router(audit_timeline.router, prefix="/api/batch-timeline", tags=["audit"]) # New Route

from app.api import violations
app.include_router(violations.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",   # local Next.js
        "https://procguard-ui.azurestaticapps.net"  # prod
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["Authorization", "Content-Type", "X-Actor-Id", "X-Actor-Role"],
)

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
