# app/schemas/provider.py
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.enums import ProviderType, UserStatus


class ProviderBase(BaseModel):
    type: ProviderType
    legal_name: str = Field(min_length=1)
    display_name: str = Field(min_length=1)
    country_code: str | None = Field(default=None, max_length=2)
    status: UserStatus = UserStatus.active


class ProviderCreate(ProviderBase):
    pass


class ProviderUpdate(BaseModel):
    type: ProviderType | None = None
    legal_name: str | None = Field(default=None, min_length=1)
    display_name: str | None = Field(default=None, min_length=1)
    country_code: str | None = Field(default=None, max_length=2)
    status: UserStatus | None = None


class ProviderRead(ProviderBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
