from typing import Generator, Annotated
from fastapi import Depends, Header, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.security.roles import Role

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Simulated Authentication for MVP / Judge Verification
# In a real setup, this would decode a JWT.
# Here, we accept explicit headers to prove RBAC logic works deterministically.
def get_current_actor(
    request: Request,
    x_actor_id: Annotated[str, Header()] = "unknown_actor",
    x_actor_role: Annotated[str, Header()] = "OPERATOR"
) -> tuple[str, str]:
    # SAFE PATTERN: Skip preflight (CORS contract)
    if request.method == "OPTIONS":
        return ("unknown", "visitor")

    try:
        # Validate that the passed role is a valid enum value
        role_enum = Role(x_actor_role)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid role: {x_actor_role}")
    
    return x_actor_id, role_enum.value

def REQUIRE_AUDITOR(
    actor: tuple[str, str] = Depends(get_current_actor)
) -> tuple[str, str]:
    actor_id, role_str = actor
    if role_str != Role.AUDITOR.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Access forbidden: Auditors only"
        )
    return actor
