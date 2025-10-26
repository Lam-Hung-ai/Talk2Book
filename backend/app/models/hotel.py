from sqlmodel import SQLModel, Field, Relationship, UniqueConstraint
from typing import TYPE_CHECKING, Optional
from uuid import UUID
from datetime import time

if TYPE_CHECKING:
    from .city import City


class Hotel(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint("city_id", "name", name="uq_hotels_city_name"),
    )

    hotel_id: UUID = Field(primary_key=True, index=True)
    provider_id: UUID = Field(foreign_key="provider.provider_id", nullable=False)
    city_id: UUID = Field(foreign_key="city.id", nullable=False)

    name: str = Field(nullable=False)
    star_rating: Optional[float] = Field(default=None)
    address: Optional[str] = Field(default=None)

    checkin_time: Optional[time] = Field(default=None)
    checkout_time: Optional[time] = Field(default=None)

    lat: Optional[float] = Field(default=None)
    lng: Optional[float] = Field(default=None)

   
