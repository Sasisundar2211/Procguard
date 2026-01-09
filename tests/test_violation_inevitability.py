from datetime import datetime, timezone

from app.core.transitions import execute_transition
from app.core.fsm import Event, State
from app.models.violation import Violation


def test_progress_without_approval_is_inevitable(db_session, batch):
    """
    Attempt: progress_step without required approval
    Expectation: immediate violation + state forced to VIOLATED
    """

    batch.current_state = State.IN_PROGRESS.value
    db_session.commit()

    import pytest
    with pytest.raises(RuntimeError):
        execute_transition(
            db=db_session,
            batch=batch,
            event=Event.PROGRESS_STEP,
            actor="tester",
            actor_role="OPERATOR",
            occurred_at=datetime.now(timezone.utc),
            approval_required=True,
            approval_present=False,
        )

    db_session.refresh(batch)

    assert batch.current_state == State.VIOLATED.value

    violations = db_session.query(Violation).all()
    assert len(violations) == 1
    assert violations[0].rule == "PROGRESS_WITHOUT_APPROVAL"
