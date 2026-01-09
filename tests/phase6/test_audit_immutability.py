import pytest
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timezone

from app.models.audit import AuditLog


def test_audit_log_cannot_be_modified(db_session, batch):
    audit = AuditLog(
        batch_id=batch.batch_id,
        expected_state="CREATED",
        action="start_batch",
        actual_state="IN_PROGRESS",
        actor="user1",
        timestamp=datetime.now(timezone.utc),
        project="Test Project",
        client="Test Client",
        agent="Test Agent",
        result="SUCCESS"
    )

    db_session.add(audit)
    db_session.commit()

    audit.actor = "hacker"

    with pytest.raises(Exception):
        db_session.commit()
