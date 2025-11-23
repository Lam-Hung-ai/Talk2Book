# app/services/refresh_token.py
from typing import Any
from uuid import UUID

from sqlmodel.ext.asyncio.session import AsyncSession

from app.repositories.refresh_token import RefreshTokenRepository
from app.schemas.refresh_token import (
    RefreshTokenCreate,
    RefreshTokenRead,
    RefreshTokenUpdate,
)


class RefreshTokenService:
    def __init__(self, db: AsyncSession):
        self.repo = RefreshTokenRepository(db)

    async def create_refresh_token(
        self, token_in: RefreshTokenCreate
    ) -> RefreshTokenRead:
        db_token = await self.repo.create(token_in)
        return RefreshTokenRead.model_validate(db_token, from_attributes=True)

    async def get_by_jti(self, jti: UUID) -> RefreshTokenRead:
        token = await self.repo.get_or_404(jti, detail="Refresh token không tồn tại")
        return RefreshTokenRead.model_validate(token, from_attributes=True)

    async def get_by_token_str(self, token_str: str) -> RefreshTokenRead | None:
        token = await self.repo.get_by_token(token_str)
        if not token:
            return None
        return RefreshTokenRead.model_validate(token, from_attributes=True)

    async def get_user_tokens(
        self, user_id: UUID, include_revoked: bool = False
    ) -> list[RefreshTokenRead]:
        tokens = await self.repo.get_user_tokens(user_id, include_revoked)
        return [
            RefreshTokenRead.model_validate(t, from_attributes=True) for t in tokens
        ]

    async def revoke_token(self, jti: UUID) -> RefreshTokenRead:
        token = await self.repo.revoke_token(jti)
        return RefreshTokenRead.model_validate(token, from_attributes=True)

    async def revoke_all_for_user(self, user_id: UUID) -> dict[str, Any]:
        count = await self.repo.revoke_all_for_user(user_id)
        return {"user_id": str(user_id), "revoked_tokens": count}

    async def update_refresh_token(
        self, jti: UUID, token_in: RefreshTokenUpdate
    ) -> RefreshTokenRead:
        db_token = await self.repo.get_or_404(jti, detail="Refresh token không tồn tại")
        updated = await self.repo.update(db_token, token_in)
        return RefreshTokenRead.model_validate(updated, from_attributes=True)

    async def delete_refresh_token(self, jti: UUID) -> None:
        await self.repo.delete(jti)

    async def delete_expired(self) -> dict[str, int]:
        count = await self.repo.delete_expired()
        return {"deleted_tokens": count}
