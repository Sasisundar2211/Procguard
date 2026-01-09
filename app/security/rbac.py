from app.security.roles import Role
from app.core.fsm import Event


def authorize_event(
    *,
    role: Role,
    event: Event,
) -> None:
    """
    Raises PermissionError if role is not allowed.
    """
    if role == Role.OPERATOR:
        if event not in {Event.START_BATCH, Event.PROGRESS_STEP, Event.REQUEST_APPROVAL}:
            raise PermissionError("Operator can only perform operational actions")
        return

    if role == Role.SUPERVISOR:
        if event not in {
            Event.APPROVE_STEP,
            Event.REJECT_BATCH,
        }:
            raise PermissionError("Supervisor cannot perform this action")
        return

    if role == Role.AUDITOR:
        raise PermissionError("Auditor is read-only")

    # If role is unknown or not handled (should not happen with Enums)
    raise PermissionError("Unknown role permission")
