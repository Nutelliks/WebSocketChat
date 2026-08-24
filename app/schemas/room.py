from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class RoomCreate(BaseModel):
    name: str = Field(min_length=3, max_length=100)
    is_private: bool = False

class RoomRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    is_private: bool
    created_by_id: UUID
    created_at: datetime
    is_member: bool = False