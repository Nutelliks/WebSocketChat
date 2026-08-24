from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class RoomMember(Base):
    __tablename__ = "room_members"

    room_id: Mapped[UUID] = mapped_column(
        ForeignKey("rooms.id", ondelete="CASCADE"),
        primary_key=True,
    )

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
    )

    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
    )

    room: Mapped["Room"] = relationship(back_populates="memberships")
    user: Mapped["User"] = relationship(back_populates="room_memberships")

    def __repr__(self):
        return f"<RoomMember room_id={self.room_id} user_id={self.user_id}>"


from app.models.room import Room  # noqa: E402
from app.models.user import User  # noqa: E402
