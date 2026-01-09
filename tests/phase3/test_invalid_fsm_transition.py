from datetime import datetime, timezone
import pytest

from app.core.transitions import execute_transition
from app.core.fsm import Event, State
from app.models.violation import Violation
from app.models.audit import AuditLog


def test_invalid_fsm_transition(db_session, batch):
    # CREATED → approve_step is illegal
    with pytest.raises(RuntimeError):
        execute_transition(
            db=db_session,
            batch=batch,
            event=Event.APPROVE_STEP,
            actor="tester",
            occurred_at=datetime.now(timezone.utc),
        )

    db_session.refresh(batch)

    assert batch.current_state == State.VIOLATED.value

    assert db_session.query(Violation).count() == 1
    assert db_session.query(AuditLog).count() == 1
