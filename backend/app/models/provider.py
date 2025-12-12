from datetime import UTC, datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import Column, func
from sqlalchemy import DateTime as SA_DateTime
from sqlmodel import DateTime, Field, Relationship, SQLModel

from app.models.enums import ProviderType, UserStatus

if TYPE_CHECKING:
    from app.models.contract import Contract
    from app.models.country import Country
    from app.models.flight_schedule import FlightSchedule
    from app.models.hotel import Hotel
    from app.models.product import Product

class Provider(SQLModel, table=True):
    __tablename__ = "provider"  # type: ignore

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    type: ProviderType = Field(nullable=False)
    legal_name: str = Field(nullable=False)
    display_name: str = Field(nullable=False)

    country_code: str | None = Field(
        default=None,
        foreign_key="country.code",
        max_length=2,
        ondelete="RESTRICT"
    )

    status: UserStatus = Field(default=UserStatus.active, nullable=False)

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_type=DateTime(timezone=True),
        nullable=False,
    )

    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(
            SA_DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
            onupdate=func.now()
        ),
    )

    contracts: list["Contract"] = Relationship(back_populates="provider")
    country: "Country" = Relationship(back_populates="providers")
    flight_schedules: list["FlightSchedule"] = Relationship(back_populates="provider")
    hotels: list["Hotel"] = Relationship(back_populates="provider")
    products: list['Product'] = Relationship(back_populates="provider")
