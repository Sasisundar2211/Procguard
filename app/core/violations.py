from app.core.fsm import State, Event
from typing import Dict, Tuple


def invalid_fsm_transition(
    current: State,
    event: Event,
    allowed_transitions: Dict[Tuple[State, Event], State],
) -> bool:
    return (current, event) not in allowed_transitions


def terminal_state_mutation(current: State) -> bool:
    return current in {
        State.COMPLETED,
        State.VIOLATED,
        State.REJECTED,
    }


def progress_without_approval(
    event: Event,
    approval_required: bool,
    approval_present: bool,
) -> bool:
    return (
        event == Event.PROGRESS_STEP
        and approval_required
        and not approval_present
    )


def approval_after_progress(
    event: Event,
    already_progressed: bool,
) -> bool:
    return event == Event.APPROVE_STEP and already_progressed


def duplicate_approval(
    approval_present: bool,
) -> bool:
    return approval_present


def unauthorized_approval(
    actor_role: str,
) -> bool:
    return actor_role != "SUPERVISOR"


def procedure_version_mismatch(
    batch_version: int,
    procedure_version: int,
) -> bool:
    return batch_version != procedure_version
