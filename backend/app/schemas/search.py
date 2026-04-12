# app/schemas/search.py
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.enums import CabinType


# ========== Flight Search ==========
class FlightSearchRequest(BaseModel):
    origin: str = Field(
        ..., min_length=3, max_length=3, description="IATA code của sân bay đi"
    )
    destination: str = Field(
        ..., min_length=3, max_length=3, description="IATA code của sân bay đến"
    )
    flight_date: date = Field(..., description="Ngày bay")
    cabin: CabinType | None = Field(default=None, description="Loại cabin (optional)")


class FlightSearchResult(BaseModel):
    instance_id: UUID
    flight_number: str
    provider_name: str
    origin: str
    destination: str
    dep_datetime: datetime
    arr_datetime: datetime
    flight_date: date
    aircraft_code: str | None = None
    status: str
    available_seats: int = Field(description="Số ghế còn trống (total - sold)")
    cabin: CabinType | None = None
    total_seats: int | None = None
    sold_seats: int | None = None

    class Config:
        from_attributes = True


class FlightSearchResponse(BaseModel):
    items: list[FlightSearchResult]
    total: int
    page: int
    page_size: int
    total_pages: int


# ========== Hotel Search ==========
class HotelSearchRequest(BaseModel):
    city_id: UUID = Field(..., description="ID của thành phố")
    check_in: date = Field(..., description="Ngày check-in")
    check_out: date = Field(..., description="Ngày check-out")
    guests: int = Field(..., ge=1, description="Số lượng khách")
    rooms: int = Field(default=1, ge=1, description="Số lượng phòng cần đặt")


class HotelSearchResult(BaseModel):
    hotel_id: UUID
    hotel_name: str
    provider_name: str
    city_name: str
    star_rating: Decimal | None
    address: str | None
    lat: Decimal | None
    lng: Decimal | None
    available_rooms: int = Field(description="Số phòng còn trống trong khoảng ngày")
    min_price: Decimal | None = Field(
        description="Giá thấp nhất cho khoảng ngày (tổng)"
    )
    currency_code: str | None

    class Config:
        from_attributes = True


class HotelSearchResponse(BaseModel):
    items: list[HotelSearchResult]
    total: int
    page: int
    page_size: int
    total_pages: int


# ========== Hotel Availability ==========
class HotelAvailabilityRequest(BaseModel):
    check_in: date = Field(..., description="Ngày check-in")
    check_out: date = Field(..., description="Ngày check-out")


class RoomAvailabilityDetail(BaseModel):
    room_id: UUID
    room_code: str | None
    capacity: int
    bed_config: str | None
    rate_plan_id: UUID
    rate_plan_name: str
    meal_plan: str | None
    available_rooms: int = Field(description="Số phòng còn trống trong khoảng ngày")
    total_price: Decimal = Field(description="Tổng giá cho toàn bộ khoảng ngày")
    price_per_night: Decimal = Field(description="Giá trung bình mỗi đêm")
    currency_code: str
    nights: int = Field(description="Số đêm")

    class Config:
        from_attributes = True


class HotelAvailabilityResponse(BaseModel):
    hotel_id: UUID
    hotel_name: str
    check_in: date
    check_out: date
    nights: int
    rooms: list[RoomAvailabilityDetail]

    class Config:
        from_attributes = True
