def test_duplicate_approval(db_session, batch):
    from app.core.transitions import execute_transition
    from app.core.fsm import Event, State
    from app.models.violation import Violation
    from app.models.audit import AuditLog
    from datetime import datetime, timezone
    
    import pytest

    batch.current_state = State.AWAITING_APPROVAL.value
    db_session.commit()

    with pytest.raises(RuntimeError):
        execute_transition(
            db=db_session,
            batch=batch,
            event=Event.APPROVE_STEP,
            actor="supervisor",
            actor_role="SUPERVISOR",
            occurred_at=datetime.now(timezone.utc),
            approval_present=True,
        )

    db_session.refresh(batch)

    assert batch.current_state == State.VIOLATED.value
    assert db_session.query(Violation).count() == 1
    assert db_session.query(AuditLog).count() == 1
