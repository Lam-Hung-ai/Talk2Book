# app/repositories/refresh_token.py
from collections.abc import Sequence
from datetime import UTC, datetime
from uuid import UUID

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.refresh_token import RefreshToken
from app.repositories.base import BaseCRUD
from app.schemas.refresh_token import RefreshTokenCreate, RefreshTokenUpdate


class RefreshTokenRepository(
    BaseCRUD[RefreshToken, RefreshTokenCreate, RefreshTokenUpdate]
):
    def __init__(self, db: AsyncSession):
        super().__init__(RefreshToken, db)

    async def get_by_jti(self, jti: UUID) -> RefreshToken | None:
        """
        Lấy token theo jti (primary key)
        """
        return await self.get(jti)

    async def get_by_token(self, token: str) -> RefreshToken | None:
        """
        Lấy token theo chuỗi refresh_token (dùng khi verify token gửi từ client)
        """
        result = await self.db.exec(
            select(RefreshToken).where(RefreshToken.refresh_token == token)
        )
        return result.first()

    async def get_user_tokens(
        self,
        user_id: UUID,
        include_revoked: bool = False,
    ) -> Sequence[RefreshToken]:
        """
        Lấy toàn bộ token của 1 user.
        include_revoked = False → chỉ lấy token chưa revoke.
        """
        statement = select(RefreshToken).where(RefreshToken.user_id == user_id)

        if not include_revoked:
            statement = statement.where(RefreshToken.revoked == False)  # noqa: E712

        result = await self.db.exec(statement)
        return result.all()

    async def revoke_token(self, jti: UUID) -> RefreshToken:
        """
        Đánh dấu 1 token là revoked
        """
        token = await self.get_or_404(jti, detail="Refresh token không tồn tại")
        token.revoked = True
        self.db.add(token)
        await self.db.commit()
        await self.db.refresh(token)
        return token

    async def revoke_all_for_user(self, user_id: UUID) -> int:
        """
        Revoke tất cả token còn sống của 1 user.
        Trả về số lượng token đã revoke.
        """
        tokens = await self.get_user_tokens(user_id=user_id, include_revoked=False)
        for t in tokens:
            t.revoked = True
            self.db.add(t)
        await self.db.commit()
        return len(tokens)

    async def delete_expired(self) -> int:
        """
        Xóa các token đã quá hạn (expires_at < now).
        Trả về số lượng token đã xóa.
        """
        now = datetime.now(UTC)
        result = await self.db.exec(
            select(RefreshToken).where(RefreshToken.expires_at < now)
        )
        tokens = result.all()

        for t in tokens:
            await self.db.delete(t)

        await self.db.commit()
        return len(tokens)
