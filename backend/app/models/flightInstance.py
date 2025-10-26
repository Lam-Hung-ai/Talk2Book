from sqlmodel import SQLModel, Field, Relationship, UniqueConstraint
from typing import TYPE_CHECKING, Optional
from uuid import UUID
from datetime import date, datetime  

if TYPE_CHECKING:
    from .flight_schedule import FlightSchedule  

class FlightInstance(SQLModel, table=True):
    __table_args__ = UniqueConstraint("schedule_id", "flight_date", name="uq_instance_schedule_date")

    instance_id: UUID = Field(primary_key=True, index=True)
    schedule_id: UUID = Field(
        foreign_key="flightschedule.schedule_id",  
        nullable=False
    )

    flight_date: date = Field(nullable=False) 
    dep_datetime: Optional[datetime] = Field(
        default=None, description="Departure datetime with timezone (timestamptz)"
    )
    arr_datetime: Optional[datetime] = Field(
        default=None, description="Arrival datetime with timezone (timestamptz)"
    )
    status: Optional[str] = Field(
        default="scheduled",
        description="VD: scheduled, departed, arrived, cancelled, delayed..."
    )
