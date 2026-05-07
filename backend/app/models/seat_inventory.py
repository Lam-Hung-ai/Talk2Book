from decimal import Decimal
from typing import TYPE_CHECKING, Any
from uuid import UUID

from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import (
    CheckConstraint,
    Column,
    Field,
    Relationship,
    SQLModel,
)

from app.models.enums import CabinType

if TYPE_CHECKING:
    from app.models.flight_instance import FlightInstance


class SeatInventory(SQLModel, table=True):
    __tablename__ = "seat_inventory"  # type: ignore
    __table_args__ = (
        CheckConstraint("held_seats + sold_seats <= total_seats", name="chk_si_seats"),
        CheckConstraint("price >= 0", name="chk_si_price"),
    )

    instance_id: UUID = Field(
        foreign_key="flight_instance.id", primary_key=True, ondelete="CASCADE"
    )
    cabin: CabinType = Field(primary_key=True)

    total_seats: int = Field(nullable=False)
    held_seats: int = Field(default=0, nullable=False)
    sold_seats: int = Field(default=0, nullable=False)
    price: Decimal = Field(
        default=Decimal("0"), decimal_places=2, max_digits=12, nullable=False
    )
    currency_code: str = Field(
        default="VND",
        max_length=3,
        nullable=False,
        foreign_key="currency.code",
    )
    amenities: dict[str, Any] = Field(default={}, sa_column=Column(JSONB))

    # Relationships
    flight_instance: "FlightInstance" = Relationship(back_populates="seat_inventory")
