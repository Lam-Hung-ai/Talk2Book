from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class RouteBase(BaseModel):
    origin: str = Field(min_length=3, max_length=3, description="IATA of origin airport")
    destination: str = Field(min_length=3, max_length=3, description="IATA of destination airport")
    distance_km: int | None = Field(default=None, ge=1)


class RouteCreate(RouteBase):
    pass


class RouteUpdate(BaseModel):
    origin: str | None = Field(default=None, min_length=3, max_length=3)
    destination: str | None = Field(default=None, min_length=3, max_length=3)
    distance_km: int | None = Field(default=None, ge=1)


class RouteRead(RouteBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

