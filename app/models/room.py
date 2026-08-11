from uuid import UUID, uuid4
from datetime import datetime, timezone

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Boolean, DateTime, ForeignKey, func

from ..core.db.base import Base


class Room(Base):
    __tablename__ = "rooms"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )

    name: Mapped[str] = mapped_column(
        String,
        nullable=False,
        unique=True
    )

    is_private: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )

    password_hash: Mapped[str | None] = mapped_column(
        String,
        nullable=True
    )

    created_by_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now()
    )

    creator: Mapped["User"] = relationship(
        back_populates="rooms",
        cascade="all, delete-orphan"
    )
