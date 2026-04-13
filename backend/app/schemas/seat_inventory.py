from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field, model_validator

from app.models.enums import CabinType


class SeatInventoryBase(BaseModel):
    instance_id: UUID
    cabin: CabinType
    total_seats: int = Field(ge=0)
    held_seats: int = Field(default=0, ge=0)
    sold_seats: int = Field(default=0, ge=0)
    price: Decimal = Field(
        default=Decimal("0"), ge=0, description="Giá vé theo hạng cabin (VNĐ)"
    )
    currency_code: str = Field(default="VND", min_length=3, max_length=3)


class SeatInventoryCreate(SeatInventoryBase):
    pass


class SeatInventoryUpdate(BaseModel):
    total_seats: int | None = Field(default=None, ge=0)
    held_seats: int | None = Field(default=None, ge=0)
    sold_seats: int | None = Field(default=None, ge=0)
    price: Decimal | None = Field(default=None, ge=0)
    currency_code: str | None = Field(default=None, min_length=3, max_length=3)


class SeatInventoryRead(SeatInventoryBase):
    available_seats: int = Field(
        default=0, description="Số ghế còn trống (total - held - sold)"
    )

    @model_validator(mode="after")
    def compute_available_seats(self) -> "SeatInventoryRead":
        self.available_seats = self.total_seats - self.held_seats - self.sold_seats
        return self

    class Config:
        from_attributes = True
