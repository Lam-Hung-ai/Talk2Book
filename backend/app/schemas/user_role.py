# app/schemas/user_role.py
from uuid import UUID

from pydantic import BaseModel


class UserRoleBase(BaseModel):
    user_id: str
    role_id: UUID


class UserRoleCreate(UserRoleBase):
    """Dùng nếu muốn tạo bản ghi mapping user-role trực tiếp (ít dùng trực tiếp)"""

    pass


class UserRoleRead(UserRoleBase):
    """Dùng cho response khi gán role cho user"""

    class Config:
        from_attributes = True
