# app/schemas/user.py — aligned with Better Auth user + app profile
from datetime import date, datetime

from pydantic import BaseModel, EmailStr

from app.models.enums import GenderType


class UserRead(BaseModel):
    id: str
    name: str
    email: str
    email_verified: bool
    image: str | None
    created_at: datetime
    updated_at: datetime


class UserUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    email_verified: bool | None = None
    image: str | None = None


class AllUserInfor(BaseModel):
    user_id: str
    name: str
    email: str
    email_verified: bool
    image: str | None
    created_at: datetime
    updated_at: datetime

    gender: GenderType | None = None
    birthday: date | None = None
    nationality: str | None = None
    address: str | None = None
    profile_updated_at: datetime | None = None

    roles: list[str]
