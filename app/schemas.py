from pydantic import BaseModel, UUID4, Field, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Dict, Any, Optional, List
from app.core.fsm import State
import enum

class TimelineStatus(str, enum.Enum):
    ON_TIME = "ON_TIME"
    OVER_TIME = "OVER_TIME"
    DEVIATION = "DEVIATION"
    LIR = "LIR"
    AT_RISK = "AT_RISK"
    RESOLVED_DELAY = "RESOLVED_DELAY"
    EMPTY = "EMPTY"
    GRAY_GHOST = "GRAY_GHOST"

class BoardStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    DEPRECATED = "DEPRECATED"
    DELETED = "DELETED"

class BatchCreateRequest(BaseModel):
    batch_id: UUID
    procedure_id: UUID
    procedure_version: int

class EventRequest(BaseModel):
    event: str  # Renamed from event_type
    step_id: Optional[str] = None # Added step_id
    # payload: Dict[str, Any]  <-- REMOVED. Forbidden.

class BatchResponse(BaseModel):
    batch_id: UUID
    procedure_id: UUID
    procedure_version: int
    current_state: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class ProcedureStepResponse(BaseModel):
    step_id: UUID
    step_order: int
    step_name: str
    requires_approval: bool
    approver_role: Optional[str]

    model_config = ConfigDict(from_attributes=True)


class ProcedureResponse(BaseModel):
    procedure_id: UUID
    version: int
    name: str
    description: Optional[str]
    steps: List[ProcedureStepResponse]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ErrorResponse(BaseModel):
    detail: str

# Timeline Schemas (Strict Audit Grade)
class Marker(BaseModel):
    type: str
    day: int
    seq: int

class StageTimeline(BaseModel):
    stage_id: str
    label: str
    expected_window: tuple[int, int]
    actual_window: tuple[Optional[int], Optional[int]]
    status: str # ON_TIME, OVER_TIME, AT_RISK, NOT_STARTED
    markers: list[Marker]

class BatchTimelineResponse(BaseModel):
    batch_id: UUID
    procedure_id: UUID
    procedure_version: int
    time_axis: dict # {unit: ..., range: ...}
    stages: list[StageTimeline]
    legend_counts: dict
    delay_buckets: list[dict]
    delayed_batches: list[dict]

    model_config = ConfigDict(from_attributes=True)

# -----------------------------------------------------------------------------
# AUDIT-SPECIFIC SCHEMAS (Batch Timeline Audit)
# -----------------------------------------------------------------------------

class AuditStage(BaseModel):
    name: str
    cells: List[TimelineStatus] 
    markers: List[Dict[str, Any]]

class AuditDelayedBatch(BaseModel):
    batch_id: str
    display_id: str
    usp: str
    dsp: str
    start_date: str
    estimated_end: str
    lead_time: int
    eos_status: str # ON_TIME, DEVIATION, EOS
    deviation_id: Optional[UUID] = None
    violation_id: Optional[UUID] = None
    comments: str

class DeviationResponse(BaseModel):
    id: UUID
    stage: str
    deviation_type: str
    approved_by: str
    approved_at: datetime
    valid_from_day: int
    valid_until_day: int
    resolved_at: Optional[datetime] = None
    superseded_by_lir: bool = False

    model_config = ConfigDict(from_attributes=True)

class AuditTimelineResponse(BaseModel):
    batch_id: str
    procedure_id: str
    procedure_version: int
    stages: List[AuditStage]
    distribution: Dict[str, Any]
    delayed_batches: List[AuditDelayedBatch]
    deviations: List[DeviationResponse] = []
    lirs: List[Dict[str, Any]] = []
    
    # Resilience & Authority Layer (ARCH-2026-SYNC-001)
    mode: str = "live" # live, degraded
    last_successful_sync: Optional[datetime] = None
    sync_status: str = "synchronized" # synchronized, bootstrapping, paused

class BoardBase(BaseModel):
    title: str
    description: Optional[str] = None
    color: str = "bg-slate-500"
    href: str = "/boards"
    primary_label: Optional[str] = None
    secondary_label: Optional[str] = None

class BoardCreate(BaseModel):
    title: str
    description: Optional[str] = None
    color: str = "bg-slate-500"
    href: str = "/boards"
    client_mutation_id: Optional[UUID] = None # Idempotency

class BoardResponse(BoardBase):
    id: UUID
    is_system: bool
    status: BoardStatus
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
