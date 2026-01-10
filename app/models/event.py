import uuid
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey
from sqlalchemy import Uuid as UUID, JSON as JSONB
from sqlalchemy import TIMESTAMP
from .base import Base
from .batch import Batch

from sqlalchemy import Index, text

class BatchEvent(Base):
    __tablename__ = "batch_events"

    event_id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    batch_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("batches.batch_id"))
    event_type: Mapped[str] = mapped_column(String, nullable=False)
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False, default=lambda: {})
    occurred_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow)

    batch: Mapped["Batch"] = relationship("Batch")

    __table_args__ = (
        Index(
            "one_approval_per_step",
            batch_id,
            text("(payload->>'step_id')"),
            unique=True,
            postgresql_where=text("event_type = 'approve_step'")
        ),
    )
