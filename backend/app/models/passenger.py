from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.booking import Booking
    from app.models.country import Country


class Passenger(SQLModel, table=True):
    __tablename__ = "passenger"  # type: ignore

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    booking_id: UUID = Field(
        nullable=False, foreign_key="booking.id", ondelete="CASCADE"
    )
    full_name: str = Field(nullable=False)
    nationality: str | None = Field(
        default=None, foreign_key="country.code", max_length=2, ondelete="RESTRICT"
    )

    # Relationships
    booking: "Booking" = Relationship(back_populates="passengers")
    country: Optional["Country"] = Relationship(back_populates="passengers")
