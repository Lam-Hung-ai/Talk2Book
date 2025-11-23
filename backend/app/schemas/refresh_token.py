# app/schemas/refresh_token.py
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class RefreshTokenBase(BaseModel):
    user_id: UUID
    refresh_token: str
    revoked: bool = False
    expires_at: datetime


class RefreshTokenCreate(RefreshTokenBase):
    """
    Dùng khi tạo refresh token mới
    """
    pass


class RefreshTokenUpdate(BaseModel):
    """
    Dùng khi update trạng thái token (revoke, gia hạn, ...)
    """
    revoked: bool | None = None
    expires_at: datetime | None = None


class RefreshTokenRead(BaseModel):
    """
    Dùng cho response trả ra client
    """
    jti: UUID
    user_id: UUID
    refresh_token: str
    revoked: bool
    expires_at: datetime
