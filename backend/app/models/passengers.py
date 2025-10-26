from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4
from datetime import date

from sqlmodel import Field, SQLModel

if TYPE_CHECKING:
    from .bookings import Booking


class PassengerType(str):
    adult = "adult"
    child = "child"
    infant = "infant"


class Passenger(SQLModel, table=True):
    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    booking_id: UUID = Field(nullable=False, foreign_key="booking.id", ondelete="CASCADE")
    full_name: str = Field(nullable=False)
    birthdate: date | None = Field(default=None)
    nationality: str | None = Field(default=None, foreign_key="country.code", max_length=2)
    passenger_type: str | None = Field(default=PassengerType.adult)
    document_type: str | None = Field(default=None)
    document_number: str | None = Field(default=None)
