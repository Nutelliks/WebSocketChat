from uuid import UUID, uuid4
from datetime import datetime, timezone

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, ForeignKey, Index, func

from .base import Base


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )

    room_id: Mapped[UUID] = mapped_column(
        ForeignKey("rooms.id", ondelete="CASCASE"),
        nullable=False,
    )

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    content: Mapped[str] = mapped_column(String(2000), nullable=False)

    file_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
    )

    room: Mapped["Room"] = relationship(back_populates="messages")

    user: Mapped["User"] = relationship(back_populates="messages")

    __table_args__ = (Index("ix_messages_room_id_created_at", "room_id", "created_at"),)

    def __repr__(self):
        return f"Message id={self.id} room_id={self.room_id} user_id={self.user_id}"


from app.models.room import Room  # noqa: E402
from app.models.user import User  # noqa: E402
