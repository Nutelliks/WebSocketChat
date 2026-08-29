from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.room import Room
from app.models.room_member import RoomMember
from app.models.user import User
from app.schemas.room import RoomCreate


@dataclass(frozen=True, slots=True)
class RoomWithMembership:
    room: Room
    is_member: bool


async def create_room(db: AsyncSession, owner: User, room_in: RoomCreate) -> Room:
    room = Room(
        name=room_in.name,
        is_private=room_in.is_private,
        created_by_id=owner.id,
    )
    db.add(room)
    await db.flush()

    membership = RoomMember(room_id=room.id, user_id=owner.id)
    db.add(membership)

    await db.commit()
    await db.refresh(room)
    return room


async def list_rooms(
    db: AsyncSession,
    current_user_id: UUID,
    skip: int = 0,
    limit: int = 50,
) -> list[RoomWithMembership]:
    membership_subq = (
        select(RoomMember.room_id)
        .where(RoomMember.user_id == current_user_id)
        .scalar_subquery()
    )

    stmt = (
        select(Room)
        .where(or_(Room.is_private.is_(False), Room.id.in_(membership_subq)))
        .order_by(Room.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    rooms = list(result.scalars().all())

    if not rooms:
        return []

    room_ids = [room.id for room in rooms]
    member_stmt = select(RoomMember.room_id).where(
        RoomMember.user_id == current_user_id,
        RoomMember.room_id.in_(room_ids),
    )
    member_result = await db.execute(member_stmt)
    member_room_ids = set(member_result.scalars().all())

    return [
        RoomWithMembership(room=room, is_member=room.id in member_room_ids)
        for room in rooms
    ]


async def get_room_by_id(db: AsyncSession, room_id: UUID) -> Room | None:
    return await db.get(Room, room_id)


async def is_room_member(db: AsyncSession, room_id: UUID, user_id: UUID) -> bool:
    stmt = select(RoomMember.room_id).where(
        RoomMember.room_id == room_id, RoomMember.user_id == user_id
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none() is not None
