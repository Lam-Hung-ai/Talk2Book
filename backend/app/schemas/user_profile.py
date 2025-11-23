from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.user_profile import Gender


class UserProfileRead(BaseModel):
    id: UUID
    user_id: UUID
    full_name: str
    gender: Gender | None
    birthday: date | None
    nationality: str | None
    avatar_url: str | None
    address: str | None
    updated_at: datetime

class UserProfileCreate(BaseModel):
    user_id: UUID
    full_name: str = Field(..., min_length=1)
    gender: Gender | None = None
    birthday: date | None = None
    nationality: str | None = Field(default=None, max_length=2)
    avatar_url: str | None = None
    address: str | None = None

class UserProfileUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=1)
    gender: Gender | None = None
    birthday: date | None = None
    nationality: str | None = Field(default=None, max_length=2)
    avatar_url: str | None = None
    address: str | None = None
