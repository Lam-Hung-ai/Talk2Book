from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.booking import Booking
    from app.models.country import Country
    from app.models.coupon import Coupon
    from app.models.coupon_redemption import CouponRedemption
    from app.models.payment import Payment
    from app.models.price_quote import PriceQuote
    from app.models.room_rate_plan import RoomRatePlan
    from app.models.slot_inventory import SlotInventory


class Currency(SQLModel, table=True):
    code: str = Field(nullable=False, max_length=3, primary_key=True)
    name: str = Field(nullable=False)

    countries: list["Country"] = Relationship(back_populates="currency")
    room_rate_plans: list["RoomRatePlan"] = Relationship(back_populates="currency")
    inventories: list["SlotInventory"] = Relationship(back_populates="currency")
    bookings: list["Booking"] = Relationship(back_populates="currency")
    coupons: list["Coupon"] = Relationship(back_populates="currency")
    coupon_redemptions: list["CouponRedemption"] = Relationship(
        back_populates="currency"
    )
    price_quotes: list["PriceQuote"] = Relationship(back_populates="currency")
    payments: list["Payment"] = Relationship(back_populates="currency")
