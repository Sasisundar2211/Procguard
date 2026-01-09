from datetime import datetime, timezone
import pytest

from app.core.transitions import execute_transition
from app.core.fsm import Event
from app.models.violation import Violation


def test_terminal_state_is_final(db_session, completed_batch):
    """
    Attempt: COMPLETED → progress_step
    Expectation: violation + hard failure
    """

    with pytest.raises(RuntimeError):
        execute_transition(
            db=db_session,
            batch=completed_batch,
            event=Event.PROGRESS_STEP,
            actor="tester",
            actor_role="OPERATOR",
            occurred_at=datetime.now(timezone.utc),
        )

    violations = db_session.query(Violation).all()
    assert len(violations) == 1
    assert violations[0].rule == "TERMINAL_STATE_MUTATION"
