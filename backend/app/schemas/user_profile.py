from datetime import date, datetime
from uuid import UUID

from app.models.user_profile import Gender
from app.schemas.user import UserRead
from pydantic import BaseModel, Field


class ProfileCreate(BaseModel):
    full_name: str
    gender: Gender | None = None
    birthday: date | None = None
    nationality: str | None = Field(default=None, min_length=2, max_length=2)
    avatar_url: str | None = None
    address: str | None = None

class ProfileRead(ProfileCreate):
    id: UUID
    user_id: UUID
    updated_at: datetime

class RoleCreate(BaseModel):
    code: str

class RoleRead(BaseModel):
    id: UUID
    code: str

class UserWithRoles(UserRead):
    roles: list[RoleRead] = []