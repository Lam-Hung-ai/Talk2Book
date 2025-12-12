from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class RouteBase(BaseModel):
    origin: str = Field(min_length=3, max_length=3, description="IATA origin")
    destination: str = Field(min_length=3, max_length=3, description="IATA destination")
    distance_km: int | None = Field(default=None, gt=0)


class RouteCreate(RouteBase):
    pass


class RouteUpdate(BaseModel):
    origin: str | None = Field(default=None, min_length=3, max_length=3)
    destination: str | None = Field(default=None, min_length=3, max_length=3)
    distance_km: int | None = Field(default=None, gt=0)


class RouteRead(RouteBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

