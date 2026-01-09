from datetime import datetime, timezone

from app.core.transitions import execute_transition
from app.core.fsm import Event, State
from app.models.violation import Violation
from app.models.audit import AuditLog


import pytest

def test_procedure_version_mismatch(db_session, batch):
    with pytest.raises(RuntimeError):
        execute_transition(
            db=db_session,
            batch=batch,
            event=Event.START_BATCH,
            actor="tester",
            actor_role="OPERATOR",
            occurred_at=datetime.now(timezone.utc),
            procedure_version=999,  # ← mismatch injected HERE
        )

    db_session.refresh(batch)

    assert batch.current_state == State.VIOLATED.value
    assert db_session.query(Violation).count() == 1
    assert db_session.query(AuditLog).count() == 1
