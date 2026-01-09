import enum
import uuid
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, Text, Boolean, Enum
from sqlalchemy import Uuid as UUID
from .base import Base

class BoardStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    DEPRECATED = "DEPRECATED"
    DELETED = "DELETED"

class Board(Base):
    __tablename__ = "boards"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    color: Mapped[str] = mapped_column(String, nullable=False, default="bg-slate-500")
    href: Mapped[str] = mapped_column(String, nullable=False, default="/boards")
    primary_label: Mapped[str] = mapped_column(String, nullable=True)
    secondary_label: Mapped[str] = mapped_column(String, nullable=True)
    is_system: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    status: Mapped[BoardStatus] = mapped_column(Enum(BoardStatus), nullable=False, default=BoardStatus.ACTIVE)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    @property
    def is_active(self) -> bool:
        return self.status == BoardStatus.ACTIVE
