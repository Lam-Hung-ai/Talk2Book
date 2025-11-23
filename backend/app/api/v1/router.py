# app/api/v1/router.py
from fastapi import APIRouter

from app.api.v1.endpoints import auth, refresh_token, role, user, user_profile

api_router = APIRouter()
api_router.include_router(user.router, prefix="/user", tags=["User"])
api_router.include_router(
    refresh_token.router, prefix="/refresh-token", tags=["Refresh Token"]
)
api_router.include_router(role.router, prefix="/role", tags=["Role"])

api_router.include_router(user_profile.router, prefix="/profile", tags=["User Profile"])

api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
