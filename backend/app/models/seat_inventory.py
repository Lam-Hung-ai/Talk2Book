from sqlmodel import SQLModel, Field, Relationship, UniqueConstraint
from typing import TYPE_CHECKING, Optional
from uuid import UUID

if TYPE_CHECKING:
    from .flight_instance import FlightInstance


class SeatInventory(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint(
            "instance_id", "cabin", "fare_bucket", name="uq_instance_cabin_bucket"
        ),
    )

    instance_id: UUID = Field(
        foreign_key="flightinstance.instance_id",
        nullable=False,
        primary_key=True,
    )

    cabin: str = Field(nullable=False)
    fare_bucket: str = Field(max_length=1, nullable=False)

    total_seats: int = Field(nullable=False)
    held_seats: Optional[int] = Field(default=0)
    sold_seats: Optional[int] = Field(default=0)
