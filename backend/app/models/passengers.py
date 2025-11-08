from typing import Optional
from uuid import UUID, uuid4
from datetime import date
from sqlmodel import Field, SQLModel

class PassengerType(str):
    adult = "adult"
    child = "child"
    infant = "infant"

class Passenger(SQLModel, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    booking_id: UUID = Field(nullable=False, foreign_key="booking.id", ondelete="CASCADE")
    full_name: str = Field(nullable=False)
    birthdate: Optional[date] = Field(default=None)
    nationality: Optional[str] = Field(default=None, foreign_key="country.code", max_length=2)
    passenger_type: Optional[str] = Field(default=PassengerType.adult)
    document_type: Optional[str] = Field(default=None)
    document_number: Optional[str] = Field(default=None)
