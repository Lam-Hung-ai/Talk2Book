from typing import TYPE_CHECKING
from uuid import UUID

from sqlmodel import Field, SQLModel, UniqueConstraint

if TYPE_CHECKING:
    pass


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
    held_seats: int | None = Field(default=0)
    sold_seats: int | None = Field(default=0)
