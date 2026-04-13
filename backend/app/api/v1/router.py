# app/api/v1/router.py
from fastapi import APIRouter

from app.api.v1.endpoints import (
    airport,
    auth,
    booking,
    booking_audit_log,
    booking_item,
    category,
    city,
    country,
    coupon,
    coupon_redemption,
    flight_instance,
    flight_realtime,
    flight_schedule,
    geo,
    hotel,
    hotel_room,
    passenger,
    payment,
    price_quote,
    product,
    provider,
    review,
    role,
    room_inventory_daily,
    room_rate_plan,
    route,
    search,
    seat_inventory,
    slot_inventory,
    ticket,
    time_slot,
    user,
    user_profile,
)

api_router = APIRouter()
api_router.include_router(user.router, prefix="/user", tags=["User"])
api_router.include_router(role.router, prefix="/role", tags=["Role"])
api_router.include_router(user_profile.router, prefix="/profile", tags=["User Profile"])
api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(geo.router, tags=["Geo"])
api_router.include_router(country.router, prefix="/country", tags=["Country"])
api_router.include_router(city.router, prefix="/city", tags=["City"])
api_router.include_router(airport.router, prefix="/airport", tags=["Airport"])
api_router.include_router(provider.router, prefix="/provider", tags=["Provider"])
api_router.include_router(route.router, prefix="/route", tags=["Route"])
api_router.include_router(
    flight_schedule.router, prefix="/flight-schedule", tags=["Flight Schedule"]
)
api_router.include_router(
    flight_instance.router, prefix="/flight-instance", tags=["Flight Instance"]
)
api_router.include_router(
    seat_inventory.router, prefix="/seat-inventory", tags=["Seat Inventory"]
)
api_router.include_router(hotel.router, prefix="/hotel", tags=["Hotel"])
api_router.include_router(hotel_room.router, prefix="/hotel-room", tags=["Hotel Room"])
api_router.include_router(
    room_rate_plan.router, prefix="/room-rate-plan", tags=["Room Rate Plan"]
)
api_router.include_router(
    room_inventory_daily.router,
    prefix="/room-inventory-daily",
    tags=["Room Inventory Daily"],
)
api_router.include_router(product.router, prefix="/product", tags=["Product"])
api_router.include_router(time_slot.router, prefix="/time-slot", tags=["Time Slot"])
api_router.include_router(
    slot_inventory.router, prefix="/slot-inventory", tags=["Slot Inventory"]
)
api_router.include_router(
    price_quote.router, prefix="/price-quote", tags=["Price Quote"]
)
api_router.include_router(coupon.router, prefix="/coupon", tags=["Coupon"])
api_router.include_router(
    coupon_redemption.router, prefix="/coupon-redemption", tags=["Coupon Redemption"]
)
api_router.include_router(booking.router, prefix="/booking", tags=["Booking"])
api_router.include_router(
    booking_item.router, prefix="/booking-item", tags=["Booking Item"]
)
api_router.include_router(passenger.router, prefix="/passenger", tags=["Passenger"])
api_router.include_router(ticket.router, prefix="/ticket", tags=["Ticket"])
api_router.include_router(
    booking_audit_log.router, prefix="/booking-audit-log", tags=["Booking Audit Log"]
)
api_router.include_router(payment.router, prefix="/payment", tags=["Payment"])
api_router.include_router(review.router, prefix="/review", tags=["Review"])
api_router.include_router(search.router, prefix="/search", tags=["Search"])
api_router.include_router(category.router, prefix="/category", tags=["Category"])
api_router.include_router(
    flight_realtime.router,
    prefix="/flight-realtime",
    tags=["Flight Realtime"],
)
