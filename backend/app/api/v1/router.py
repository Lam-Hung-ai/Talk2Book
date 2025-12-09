# app/api/v1/router.py
from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    contract,
    flight_instance,
    flight_schedule,
    refresh_token,
    role,
    route as route_ep,
    seat_inventory,
    user,
    user_profile,
)

api_router = APIRouter()
api_router.include_router(user.router, prefix="/user", tags=["User"])
api_router.include_router(
    refresh_token.router, prefix="/refresh-token", tags=["Refresh Token"]
)
api_router.include_router(role.router, prefix="/role", tags=["Role"])

api_router.include_router(contract.router, prefix="/contract", tags=["Contract"])

api_router.include_router(user_profile.router, prefix="/profile", tags=["User Profile"])

api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(route_ep.router, prefix="/route", tags=["Route"])
api_router.include_router(flight_schedule.router, prefix="/flight-schedule", tags=["Flight Schedule"])
api_router.include_router(flight_instance.router, prefix="/flight-instance", tags=["Flight Instance"])
api_router.include_router(seat_inventory.router, prefix="/seat-inventory", tags=["Seat Inventory"])
