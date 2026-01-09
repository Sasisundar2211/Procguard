from datetime import datetime
from pydantic import BaseModel, ConfigDict
from uuid import UUID
from typing import Optional, Any

class AuditLogResponse(BaseModel):
    id: UUID
    created_at: datetime
    source: str
    project_id: str
    event_type: str
    user_id: str
    client_id: str
    payload: dict[str, Any]
    
    # Extended fields
    actor: Optional[str] = None
    action: Optional[str] = None
    result: Optional[str] = None
    batch_id: Optional[UUID] = None
    violation_id: Optional[UUID] = None

    model_config = ConfigDict(from_attributes=True)
