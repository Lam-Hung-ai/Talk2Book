from datetime import date
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.enums import CabinType
from app.schemas.booking import BookingRead
from app.schemas.booking_item import BookingItemRead
from app.schemas.ticket import TicketRead


class FlightBookingRequest(BaseModel):
    """Request đặt vé máy bay dựa trên FlightInstance đã search được."""

    user_id: UUID | None = None
    instance_id: UUID
    cabin: CabinType
    passengers: int = Field(ge=1, description="Số lượng hành khách")
    currency_code: str = Field(default="VND", max_length=3)


class FlightBookingResult(BaseModel):
    booking: BookingRead
    item: BookingItemRead
    tickets: list[TicketRead] | None = None


class HotelBookingRequest(BaseModel):
    """Request đặt phòng sau khi đã xem availability."""

    user_id: UUID | None = None
    hotel_id: UUID
    room_id: UUID
    rate_plan_id: UUID
    check_in: date
    check_out: date
    rooms: int = Field(ge=1, description="Số phòng đặt")
    guests: int = Field(ge=1, description="Tổng số khách")
    currency_code: str = Field(default="VND", max_length=3)


class HotelBookingResult(BaseModel):
    booking: BookingRead
    item: BookingItemRead


