# app/schemas/product.py
from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.enums import ProductType


class ProductBase(BaseModel):
    provider_id: UUID
    city_id: UUID | None = None
    type: ProductType
    title: str = Field(min_length=1, max_length=255)
    # Rich fields
    tour_type: str | None = None
    description: str | None = None
    detail_description: str | None = None
    itinerary: list[dict[str, Any]] | None = None
    costs: list[dict[str, Any]] | None = None
    images: list[str] | None = None
    duration_days: int | None = None


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    provider_id: UUID | None = None
    city_id: UUID | None = None
    type: ProductType | None = None
    title: str | None = Field(default=None, min_length=1, max_length=255)
    tour_type: str | None = None
    description: str | None = None
    detail_description: str | None = None
    itinerary: list[dict[str, Any]] | None = None
    costs: list[dict[str, Any]] | None = None
    images: list[str] | None = None
    duration_days: int | None = None


class ProductRead(ProductBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
