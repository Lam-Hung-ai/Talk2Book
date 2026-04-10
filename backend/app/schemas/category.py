from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class CategoryRead(BaseModel):
    id: UUID
    group_name: str
    value: str
    description: str | None
    sort_order: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CategoryCreate(BaseModel):
    group_name: str = Field(min_length=1, max_length=120)
    value: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=500)
    sort_order: int = 0
    is_active: bool = True


class CategoryUpdate(BaseModel):
    group_name: str | None = Field(default=None, min_length=1, max_length=120)
    value: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=500)
    sort_order: int | None = None
    is_active: bool | None = None
