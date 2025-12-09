from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.booking import Booking
    from app.models.contract import Contract
    from app.models.country import Country
    from app.models.coupon import Coupon
    from app.models.room_rate_plan import RoomRatePlan
    from app.models.time_slot import SlotInventory

class Currency(SQLModel, table=True):
    code: str = Field(nullable=False, max_length=3, primary_key=True)
    name: str = Field(nullable=False)

    countries: list["Country"] = Relationship(back_populates="currency")
    contracts: list["Contract"] =  Relationship(back_populates="currency")
    room_rate_plans: list["RoomRatePlan"] = Relationship(back_populates="currency")
    inventories: list['SlotInventory'] = Relationship(back_populates="currency")
    bookings: list["Booking"] = Relationship(back_populates="currency")
    coupons: list["Coupon"] = Relationship(back_populates="currency")
