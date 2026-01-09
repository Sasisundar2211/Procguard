from app.enforcement.validators import (
    validate_step_order,
    validate_missing_steps,
    validate_actor_roles,
    validate_unexpected_steps,
    validate_duplicates
)

def run_enforcement(
    sop_steps,
    execution_events,
    role_map
):
    """
    Runs deterministic enforcement.
    Returns first violation found (fail-fast).
    """

    validators = [
        validate_unexpected_steps,
        lambda s, e: validate_duplicates(e),
        validate_missing_steps,
        validate_step_order,
        lambda s, e: validate_actor_roles(s, e, role_map)
    ]

    for validator in validators:
        violation = validator(sop_steps, execution_events)
        if violation:
            return violation

    return None
