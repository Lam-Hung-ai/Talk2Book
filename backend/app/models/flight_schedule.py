from datetime import UTC, datetime, time
from typing import TYPE_CHECKING, Any
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.flight_instance import FlightInstance
    from app.models.provider import Provider
    from app.models.route import Route


class FlightSchedule(SQLModel, table=True):
    __tablename__ = "flight_schedule"  # type: ignore
    __table_args__ = (
        UniqueConstraint(
            "provider_id",
            "route_id",
            "flight_number",
            "dow",
            "dep_time",
            name="uq_fs_provider_route_flt_dow_time",
        ),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    provider_id: UUID = Field(
        foreign_key="provider.id", nullable=False, ondelete="RESTRICT"
    )
    route_id: UUID = Field(foreign_key="route.id", nullable=False, ondelete="CASCADE")
    flight_number: str = Field(nullable=False)
    dow: str = Field(
        nullable=False,
        description="Bitstring representing Days of Week (e.g., 1000000)",
    )
    dep_time: time = Field(nullable=False)
    arr_time: time = Field(nullable=False)
    arrival_day_offset: int = Field(default=0, nullable=False)
    aircraft_code: str | None = None
    cabin_class: str | None = Field(default=None)        # Economy, Business, First...
    ticket_type: str | None = Field(default=None)        # Loại vé (từ danh mục)
    amenities: list[str] | None = Field(default=None, sa_column=Column[Any](JSONB))
    price_from: float | None = Field(default=None)       # Giá tham khảo chưa VAT

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
    route: "Route" = Relationship(back_populates="flight_schedules")
    provider: "Provider" = Relationship(back_populates="flight_schedules")
    instances: list["FlightInstance"] = Relationship(back_populates="schedule")
