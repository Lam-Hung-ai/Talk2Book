from typing import Any
from uuid import UUID

from fastapi import HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.repositories.coupon import CouponRepository
from app.schemas.coupon import CouponCreate, CouponRead, CouponUpdate


class CouponService:
    def __init__(self, db: AsyncSession):
        self.repo = CouponRepository(db)
        self.db = db

    async def create_coupon(self, coupon_in: CouponCreate) -> CouponRead:
        if await self.repo.get_by_code(coupon_in.code):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Coupon code already exists",
            )

        coupon = await self.repo.create(coupon_in)
        return CouponRead.model_validate(coupon, from_attributes=True)

    async def get_coupon(self, coupon_id: UUID) -> CouponRead:
        coupon = await self.repo.get_or_404(coupon_id, detail="Coupon not found")
        return CouponRead.model_validate(coupon, from_attributes=True)

    async def list_coupons(
        self,
        page: int = 1,
        page_size: int = 50,
        is_active: bool | None = None,
    ) -> dict[str, Any]:
        skip = (page - 1) * page_size

        filters: dict[str, Any] = {}
        if is_active is not None:
            filters["is_active"] = is_active

        coupons = await self.repo.get_multi(skip=skip, limit=page_size, **filters)
        total = await self.repo.get_count(**filters)

        return {
            "items": [CouponRead.model_validate(c, from_attributes=True) for c in coupons],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        }

    async def update_coupon(self, coupon_id: UUID, coupon_in: CouponUpdate) -> CouponRead:
        coupon = await self.repo.get_or_404(coupon_id, detail="Coupon not found")

        if coupon_in.code and coupon_in.code != coupon.code:
            if await self.repo.get_by_code(coupon_in.code):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Coupon code already exists",
                )

        updated = await self.repo.update(coupon, coupon_in)
        return CouponRead.model_validate(updated, from_attributes=True)

    async def delete_coupon(self, coupon_id: UUID) -> None:
        await self.repo.delete(coupon_id)

    async def search_coupons(
        self,
        q: str,
        page: int = 1,
        page_size: int = 20,
        exact_match: bool = False,
        case_sensitive: bool = False,
    ) -> dict[str, Any]:
        skip = (page - 1) * page_size

        coupons = await self.repo.search(
            query=q,
            search_columns=["code"],
            exact_match=exact_match,
            case_sensitive=case_sensitive,
            skip=skip,
            limit=page_size,
        )

        total = await self.repo.count_search(
            query=q,
            search_columns=["code"],
            exact_match=exact_match,
            case_sensitive=case_sensitive,
        )

        return {
            "items": [CouponRead.model_validate(c, from_attributes=True) for c in coupons],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        }

