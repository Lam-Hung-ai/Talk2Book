from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field


class RoleEnum(str, Enum):
    admin = "admin"
    partner = "partner"
    user = "user"

class RoleBase(BaseModel):
    code: str = Field(..., min_length=1, description="Mã role, ví dụ: admin, user, partner")


class RoleCreate(RoleBase):
    """Dùng khi tạo role mới"""
    pass


class RoleUpdate(BaseModel):
    """Dùng khi update role"""
    code: str | None = Field(default=None, min_length=1)


class RoleRead(BaseModel):
    """Dùng cho response"""
    id: UUID
    code: str
