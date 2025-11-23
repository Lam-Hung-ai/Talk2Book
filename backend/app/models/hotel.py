from datetime import time
from typing import TYPE_CHECKING
from uuid import UUID

from sqlmodel import Field, SQLModel, UniqueConstraint

if TYPE_CHECKING:
    pass


class Hotel(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("city_id", "name", name="uq_hotels_city_name"),)

    hotel_id: UUID = Field(primary_key=True, index=True)
    provider_id: UUID = Field(foreign_key="provider.provider_id", nullable=False)
    city_id: UUID = Field(foreign_key="city.id", nullable=False)

    name: str = Field(nullable=False)
    star_rating: float | None = Field(default=None)
    address: str | None = Field(default=None)

    checkin_time: time | None = Field(default=None)
    checkout_time: time | None = Field(default=None)

    lat: float | None = Field(default=None)
    lng: float | None = Field(default=None)
