from collections.abc import Sequence
from uuid import UUID

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.coupon import Coupon
from app.repositories.base import BaseCRUD
from app.repositories.searchable import SearchableRepository
from app.schemas.coupon import CouponCreate, CouponUpdate


class CouponRepository(BaseCRUD[Coupon, CouponCreate, CouponUpdate], SearchableRepository[Coupon]):
    def __init__(self, db: AsyncSession):
        BaseCRUD.__init__(self, Coupon, db)
        SearchableRepository.__init__(self, Coupon, db)

    async def get_by_code(self, code: str) -> Coupon | None:
        result = await self.db.exec(select(Coupon).where(Coupon.code == code))
        return result.first()

    async def get_active(self, *, skip: int = 0, limit: int = 100) -> Sequence[Coupon]:
        return await self.get_multi(skip=skip, limit=limit, is_active=True)

