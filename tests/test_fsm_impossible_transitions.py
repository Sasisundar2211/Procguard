import pytest
from app.core.transitions import execute_transition
from app.core.fsm import Event
from app.models.violation import Violation
from datetime import datetime, timezone


def test_invalid_transition_creates_violation(db_session, batch):
    """
    Attempt: CREATED → approve_step (illegal)
    Expectation: violation + exception
    """

    with pytest.raises(RuntimeError):
        execute_transition(
            db=db_session,
            batch=batch,
            event=Event.APPROVE_STEP,
            actor="tester",
            occurred_at=datetime.now(timezone.utc),
        )

    violations = db_session.query(Violation).all()
    assert len(violations) == 1
    assert violations[0].rule == "INVALID_FSM_TRANSITION"
