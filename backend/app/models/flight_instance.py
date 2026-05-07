from datetime import UTC, date, datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import DateTime, UniqueConstraint
from sqlmodel import CheckConstraint, Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.flight_schedule import FlightSchedule
    from app.models.seat_inventory import SeatInventory


class FlightInstance(SQLModel, table=True):
    __tablename__ = "flight_instance"  # type: ignore
    __table_args__ = (
        CheckConstraint("dep_datetime < arr_datetime", name="chk_fi_time"),
        UniqueConstraint("schedule_id", "flight_date", name="uq_fi_schedule_date"),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    schedule_id: UUID = Field(
        foreign_key="flight_schedule.id", nullable=False, ondelete="CASCADE"
    )
    flight_date: date = Field(nullable=False)
    dep_datetime: datetime = Field(sa_type=DateTime(timezone=True), nullable=False)
    arr_datetime: datetime = Field(sa_type=DateTime(timezone=True), nullable=False)
    aircraft_code: str | None = Field(default=None)
    status: str = Field(default="scheduled", max_length=20, nullable=False)

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_type=DateTime(timezone=True),
        nullable=False,
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_type=DateTime(timezone=True),
        nullable=False,
    )

    # Relationships
    schedule: "FlightSchedule" = Relationship(back_populates="instances")
    seat_inventory: list["SeatInventory"] = Relationship(
        back_populates="flight_instance"
    )
