from datetime import datetime, timezone
from app.core.transitions import execute_transition
from app.core.fsm import Event
from app.security.roles import Role

def test_read_only_roles_do_not_emit_events(db_session, batch):
    from app.models.event import BatchEvent

    events_before = db_session.query(BatchEvent).count()

    try:
        execute_transition(
            db=db_session,
            batch=batch,
            event=Event.START_BATCH,
            actor="auditor",
            actor_role=Role.AUDITOR.value,
            occurred_at=datetime.now(timezone.utc),
        )
    except PermissionError:
        pass

    events_after = db_session.query(BatchEvent).count()
    assert events_before == events_after
