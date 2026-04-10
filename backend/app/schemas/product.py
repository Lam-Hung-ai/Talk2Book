# app/schemas/product.py
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.enums import ProductType


class ProductBase(BaseModel):
    provider_id: UUID
    city_id: UUID | None = None
    type: ProductType
    title: str = Field(min_length=1, max_length=255)
    # Rich fields
    tour_type: str | None = None           # Loại tour (từ danh mục)
    description: str | None = None         # Giới thiệu chung
    detail_description: str | None = None  # Giới thiệu chi tiết
    itinerary: str | None = None           # JSON: '[{"day":1,"title":"","description":""}]'
    costs: str | None = None               # JSON: '[{"item":"","amount":0,"note":""}]'
    images: str | None = None              # JSON: '["url1","url2"]'
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
    itinerary: str | None = None
    costs: str | None = None
    images: str | None = None
    duration_days: int | None = None


class ProductRead(ProductBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
