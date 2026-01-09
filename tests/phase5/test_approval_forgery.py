import pytest
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timezone

from app.models.event import BatchEvent


def test_duplicate_approval_rejected_by_db(db_session, batch):
    event1 = BatchEvent(
        batch_id=batch.batch_id,
        event_type="approve_step",
        payload={"step_id": "step-1"},
        occurred_at=datetime.now(timezone.utc),
    )

    event2 = BatchEvent(
        batch_id=batch.batch_id,
        event_type="approve_step",
        payload={"step_id": "step-1"},
        occurred_at=datetime.now(timezone.utc),
    )

    db_session.add(event1)
    db_session.commit()

    db_session.add(event2)
    with pytest.raises(IntegrityError):
        db_session.commit()
