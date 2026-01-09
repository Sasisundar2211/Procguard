from datetime import datetime, timezone
from app.core.transitions import execute_transition
from app.core.fsm import Event
from app.models.audit import AuditLog


def test_exactly_one_audit_on_success(db_session, batch):
    audits_before = db_session.query(AuditLog).count()

    execute_transition(
        db=db_session,
        batch=batch,
        event=Event.START_BATCH,
        actor="user1",
        actor_role="OPERATOR",
        occurred_at=datetime.now(timezone.utc),
    )

    audits_after = db_session.query(AuditLog).count()
    assert audits_after - audits_before == 1
def test_exactly_one_audit_on_violation(db_session, batch):
    audits_before = db_session.query(AuditLog).count()

    try:
        execute_transition(
            db=db_session,
            batch=batch,
            event=Event.PROGRESS_STEP,
            actor="user1",
            actor_role="OPERATOR",
            occurred_at=datetime.now(timezone.utc),
            approval_required=True,
            approval_present=False,
        )
    except Exception:
        pass

    audits_after = db_session.query(AuditLog).count()
    assert audits_after - audits_before == 1
