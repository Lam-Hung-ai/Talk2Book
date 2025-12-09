from uuid import UUID

from pydantic import BaseModel, Field

from app.models.enums import CabinType, FareBucketType


class SeatInventoryBase(BaseModel):
    instance_id: UUID
    cabin: CabinType
    fare_bucket: FareBucketType
    total_seats: int = Field(ge=0)
    held_seats: int = Field(default=0, ge=0)
    sold_seats: int = Field(default=0, ge=0)


class SeatInventoryCreate(SeatInventoryBase):
    pass


class SeatInventoryUpdate(BaseModel):
    total_seats: int | None = Field(default=None, ge=0)
    held_seats: int | None = Field(default=None, ge=0)
    sold_seats: int | None = Field(default=None, ge=0)


class SeatInventoryRead(SeatInventoryBase):
    class Config:
        from_attributes = True

