from datetime import datetime
from uuid import UUID

from app.models.user import UserStatus
from pydantic import BaseModel, EmailStr, Field

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