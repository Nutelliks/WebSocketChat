from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import CurrentUser
from app.core.db import get_db
from app.schemas.room import RoomCreate, RoomRead
from app.services import room_service

router = APIRouter(prefix="/rooms", tags=["rooms"])


def _to_room_read(item: room_service.RoomWithMembership) -> RoomRead:
    return RoomRead.model_validate(item.room).model_copy(
        update={"is_member": item.is_member}
    )


@router.post("", response_model=RoomRead, status_code=status.HTTP_201_CREATED)
async def create_room(
    room_in: RoomCreate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> RoomRead:
    room = await room_service.create_room(db, current_user, room_in)
    return RoomRead.model_validate(room).model_copy(update={"is_member": True})


@router.get("", response_model=list[RoomRead])
async def list_rooms(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
) -> list[RoomRead]:
    rooms = await room_service.list_rooms(db, current_user.id, skip=skip, limit=limit)
    return [_to_room_read(item) for item in rooms]
