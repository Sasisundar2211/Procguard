from datetime import datetime
import uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, ForeignKey, Integer
from sqlalchemy import Uuid as UUID
from .base import Base
from .procedure import Procedure


class Batch(Base):
    __tablename__ = "batches"

    batch_id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    procedure_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("procedures.procedure_id"))
    procedure_version: Mapped[int] = mapped_column(Integer, nullable=False)

    current_state: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    procedure: Mapped["Procedure"] = relationship("Procedure")
