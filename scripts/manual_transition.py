from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.core.transitions import execute_transition
from app.core.fsm import Event
from app.security.roles import Role
from app.models.batch import Batch

db: Session = SessionLocal()

batch = db.query(Batch).filter_by(
    batch_id="33333333-3333-3333-3333-333333333333"
).one()

execute_transition(
    db=db,
    batch=batch,
    event=Event.START_BATCH,
    actor="operator_1",
    actor_role=Role.OPERATOR.value,
    occurred_at=datetime.now(timezone.utc),
)

print("Transition executed successfully.")
