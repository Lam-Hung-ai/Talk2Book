from collections.abc import Sequence
from datetime import UTC, datetime, timedelta
from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.v1.deps import get_async_session
from app.core.config import settings
from app.core.security import create_token, decode_token, verify_password
from app.models.user import User
from app.models.enums import UserStatus
from app.schemas.auth import LoginSchema, TokenPayload, TokenType
from app.services.refresh_token import RefreshTokenService
from app.services.user import UserService


class AuthService:
    def __init__(self, db: AsyncSession= Depends(get_async_session)):
        self.user_service = UserService(db)
        self.refresh_token_service = RefreshTokenService(db)

    async def login(self, form: LoginSchema) -> tuple[str, str]:
        user_search: Sequence[User] = await self.user_service.repo.search(query=form.identity, search_columns=["email", "phone"], exact_match=True)

        if not user_search:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email/phone or password")

        user: User = user_search[0]
        if not user or user.status != UserStatus.active or not verify_password(form.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
            )


        all_user_info = await self.user_service.get_all_info_by_id(user.id)
        if form.require_scope not in all_user_info.roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")


        access_token = create_token(
            TokenPayload(user_id=all_user_info.user_id,
                         exp=int((datetime.now(UTC) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)).timestamp()),
                         scopes=all_user_info.roles,
                         fullname=all_user_info.full_name,
                         type=TokenType.access
                        ))

        refresh_token = create_token(
            TokenPayload(user_id=all_user_info.user_id,
                         exp=int((datetime.now(UTC) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)).timestamp()),
                         scopes=all_user_info.roles,
                         fullname=all_user_info.full_name,
                         type=TokenType.refresh
                        )
        )

        refresh_token_payload = decode_token(refresh_token, expected_type=TokenType.refresh)
        await self.refresh_token_service.repo.create(
            {
                "jti":refresh_token_payload.jti,
                "user_id": refresh_token_payload.user_id,
                "refresh_token": refresh_token,
                "revoked": False,
                "expires_at": datetime.fromtimestamp(float(refresh_token_payload.exp), tz=UTC)
            }
        )
        return access_token, refresh_token

    async def create_new_access_token(self, refresh_token: str) -> str:
        try:
            payload: TokenPayload = decode_token(refresh_token, expected_type=TokenType.refresh)
        except Exception:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        if payload.type != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")

        jti = payload.jti
        if not jti:
            raise HTTPException(status_code=401, detail="Invalid token payload")

        rec = await self.refresh_token_service.get_by_jti(jti)
        if not rec or rec.revoked:
            raise HTTPException(status_code=401, detail="Refresh token revoked")
        if datetime.now(UTC) > rec.expires_at:
            await self.refresh_token_service.delete_refresh_token(jti)
            raise HTTPException(status_code=401, detail="Refresh token expired")

        user = await self.user_service.get_user_by_id(payload.user_id)
        if not user or not user.status == UserStatus.active:
            await self.refresh_token_service.delete_refresh_token(jti)
            raise HTTPException(status_code=401, detail="User not active")

        all_user_info = await self.user_service.get_all_info_by_id(user.id)
        access_token = create_token(
            TokenPayload(user_id=user.id,
                         exp=int((datetime.now(UTC) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)).timestamp()),
                         scopes=all_user_info.roles,
                         fullname=all_user_info.full_name,
                         type=TokenType.access),
        )
        return access_token


    async def logout(self, refresh_token: str):
        try:
            payload = decode_token(refresh_token)
            if payload.type != TokenType.refresh:
                raise Exception()
            jti = payload.jti
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid refresh token")
        try:
            await self.refresh_token_service.delete_refresh_token(jti)
        except Exception as e:
            print(f"Error deleting token: {e}")
            raise HTTPException(status_code=404, detail="Token not found")

    async def logout_all(self, user_id: UUID):
        await self.refresh_token_service.revoke_all_for_user(user_id)
