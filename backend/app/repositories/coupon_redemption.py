from collections.abc import Sequence
from uuid import UUID

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.coupon_redemption import CouponRedemption
from app.repositories.base import BaseCRUD
from app.repositories.searchable import SearchableRepository
from app.schemas.coupon_redemption import CouponRedemptionCreate, CouponRedemptionUpdate


class CouponRedemptionRepository(
    BaseCRUD[CouponRedemption, CouponRedemptionCreate, CouponRedemptionUpdate],
    SearchableRepository[CouponRedemption],
):
    def __init__(self, db: AsyncSession):
        BaseCRUD.__init__(self, CouponRedemption, db)
        SearchableRepository.__init__(self, CouponRedemption, db)

    async def get_by_coupon(
        self, coupon_id: UUID, *, skip: int = 0, limit: int = 100
    ) -> Sequence[CouponRedemption]:
        return await self.get_multi(skip=skip, limit=limit, coupon_id=coupon_id)

    async def get_by_user(
        self, user_id: str, *, skip: int = 0, limit: int = 100
    ) -> Sequence[CouponRedemption]:
        return await self.get_multi(skip=skip, limit=limit, user_id=user_id)

    async def exists_for_booking(self, booking_id: UUID) -> bool:
        result = await self.db.exec(
            select(CouponRedemption.id).where(CouponRedemption.booking_id == booking_id)
        )
        return result.first() is not None
