from pydantic import BaseModel, UUID4, Field, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Dict, Any, Optional, List
from app.core.fsm import State

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
    cells: List[str] # List of 70 status strings: "ON_TIME", "OVER_TIME", "EMPTY", "GRAY" etc.
    markers: List[Dict[str, Any]] # Optional: To handle markers if not in cells? 
    # Request example just showed cells. But markers are needed.
    # User Request: "cells": ["OVER_TIME", ...].
    # But UI has markers. I will include markers in the response or embed them in cells? 
    # Embedded in cells is hard("OVER_TIME|MARKER:21"). 
    # Better to have a separate list or rich cell objects.
    # BUT "Response Shape (NO OPTIONAL FIELDS)" showed:
    # "stages": [{ "name": "...", "cells": [...] }]
    # I will assume 'cells' might contain marker info OR I add 'markers' field and update logic. 
    # Or, to be "pixel-faithful", I'll move the marker logic to backend too? 
    # Step 1.1 says: "stages": [...] with "cells". 
    # I'll add "markers" to AuditStage to be safe, so frontend can render them.

class AuditDelayedBatch(BaseModel):
    batch: int
    usp: str
    dsp: str
    start_date: str
    estimated_end: str
    lead_time: int
    eos: bool
    comments: str

class AuditTimelineResponse(BaseModel):
    batch_id: str
    procedure_id: str
    procedure_version: int
    stages: List[AuditStage]
    distribution: Dict[str, Any]
    delayed_batches: List[AuditDelayedBatch]
