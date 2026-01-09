# app/core/fsm.py

from enum import Enum
from typing import Dict, Tuple


class State(str, Enum):
    CREATED = "CREATED"
    IN_PROGRESS = "IN_PROGRESS"
    AWAITING_APPROVAL = "AWAITING_APPROVAL"
    APPROVED = "APPROVED"
    COMPLETED = "COMPLETED"
    VIOLATED = "VIOLATED"
    REJECTED = "REJECTED"


class Event(str, Enum):
    START_BATCH = "start_batch"
    REQUEST_APPROVAL = "request_approval"
    APPROVE_STEP = "approve_step"
    PROGRESS_STEP = "progress_step"
    REJECT_BATCH = "reject_batch"


ALLOWED_TRANSITIONS: Dict[Tuple[State, Event], State] = {
    (State.CREATED, Event.START_BATCH): State.IN_PROGRESS,

    (State.IN_PROGRESS, Event.REQUEST_APPROVAL): State.AWAITING_APPROVAL,

    (State.AWAITING_APPROVAL, Event.APPROVE_STEP): State.APPROVED,

    (State.APPROVED, Event.PROGRESS_STEP): State.IN_PROGRESS,

    (State.IN_PROGRESS, Event.PROGRESS_STEP): State.COMPLETED,

    (State.CREATED, Event.REJECT_BATCH): State.REJECTED,
    (State.IN_PROGRESS, Event.REJECT_BATCH): State.REJECTED,
}
