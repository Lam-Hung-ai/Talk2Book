# app/schemas/user.py
from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.models.enums import GenderType, UserStatus


class UserRead(BaseModel):
    id: UUID
    email: str
    phone: str
    status: UserStatus
    created_at: datetime

class UserCreate(BaseModel):
    email: EmailStr
    phone: str = Field(max_length=32)
    password: str = Field(min_length=6)

class UserUpdate(BaseModel):
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=32)
    password: str | None = Field(default=None, min_length=6)
    status: UserStatus | None = None

class AllUserInfor(BaseModel):
    user_id: UUID
    email: str
    phone: str
    status: UserStatus
    created_at: datetime

    full_name: str | None = None
    gender: GenderType | None = None
    birthday: date | None = None
    nationality: str | None = None
    avatar_url: str | None = None
    address: str | None = None
    updated_at: datetime | None = None

    roles: list[str]
