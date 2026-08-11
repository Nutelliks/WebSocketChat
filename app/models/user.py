from uuid import UUID, uuid4
from datetime import datetime, timezone

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, func

from ..core.db.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(
        primary_key=True, 
        default=uuid4, 
    )

    username: Mapped[str] = mapped_column(
        String, 
        unique=True, 
        nullable=False
    )

    email: Mapped[str] = mapped_column(
        String, 
        unique=True, 
        index=True,
        nullable=False
    )

    hashed_password: Mapped[str] = mapped_column(
        String, 
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now()
    )

    rooms: Mapped[list["Room"]] = relationship(
        back_populates="creator"
    )
