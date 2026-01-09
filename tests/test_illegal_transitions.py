import pytest
from datetime import datetime, timezone

from app.core.transitions import execute_transition
from app.core.fsm import Event
from app.models.violation import Violation


def test_invalid_transition_creates_violation(db_session, batch):
    with pytest.raises(RuntimeError):
        execute_transition(
            db=db_session,
            batch=batch,
            event=Event.APPROVE_STEP,
            actor="user",
            occurred_at=datetime.now(timezone.utc),
        )

    violations = db_session.query(Violation).all()
    assert len(violations) == 1
    assert violations[0].rule == "INVALID_FSM_TRANSITION"
