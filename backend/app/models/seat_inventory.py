from typing import TYPE_CHECKING
from uuid import UUID

from sqlmodel import Field, Relationship, SQLModel, UniqueConstraint

from app.models.enums import CabinType, FareBucketType

if TYPE_CHECKING:
    from app.models.flight_instance import FlightInstance


class SeatInventory(SQLModel, table=True):
    __tablename__ = "seat_inventory"  # type: ignore
    __table_args__ = (
        UniqueConstraint(
            "instance_id", "cabin", "fare_bucket", name="uq_instance_cabin_bucket"
        ),
    )

    instance_id: UUID = Field(foreign_key="flight_instance.id", primary_key=True, ondelete="CASCADE")
    cabin: CabinType = Field(primary_key=True)
    fare_bucket: FareBucketType = Field(primary_key=True)

    total_seats: int = Field(nullable=False)
    held_seats: int = Field(default=0, nullable=False)
    sold_seats: int = Field(default=0, nullable=False)

    # Relationships
    flight_instance: "FlightInstance" = Relationship(back_populates="seat_inventory")
