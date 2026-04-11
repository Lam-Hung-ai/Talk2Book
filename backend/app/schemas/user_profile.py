from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel

from app.models.enums import GenderType


class UserProfileBase(BaseModel):
    full_name: str | None = None
    gender: GenderType | None = None
    birthday: date | None = None
    nationality: str | None = None
    avatar_url: str | None = None
    address: str | None = None


class UserProfileCreate(UserProfileBase):
    user_id: str


class UserProfileUpdate(UserProfileBase):
    pass


class UserProfileRead(UserProfileBase):
    id: UUID
    user_id: str
    updated_at: datetime | None = None
