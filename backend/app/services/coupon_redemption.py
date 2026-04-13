from typing import Any
from uuid import UUID

from fastapi import HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.repositories.booking import BookingRepository
from app.repositories.coupon import CouponRepository
from app.repositories.coupon_redemption import CouponRedemptionRepository
from app.schemas.coupon_redemption import (
    CouponRedemptionCreate,
    CouponRedemptionRead,
    CouponRedemptionUpdate,
)


class CouponRedemptionService:
    def __init__(self, db: AsyncSession):
        self.repo = CouponRedemptionRepository(db)
        self.coupon_repo = CouponRepository(db)
        self.booking_repo = BookingRepository(db)

    async def create_redemption(
        self, redemption_in: CouponRedemptionCreate
    ) -> CouponRedemptionRead:
        await self.coupon_repo.get_or_404(
            redemption_in.coupon_id, detail="Coupon not found"
        )
        await self.booking_repo.get_or_404(
            redemption_in.booking_id, detail="Booking not found"
        )

        if await self.repo.exists_for_booking(redemption_in.booking_id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Redemption already exists for this booking",
            )

        redemption = await self.repo.create(redemption_in)
        return CouponRedemptionRead.model_validate(redemption, from_attributes=True)

    async def get_redemption(self, redemption_id: UUID) -> CouponRedemptionRead:
        redemption = await self.repo.get_or_404(
            redemption_id, detail="Redemption not found"
        )
        return CouponRedemptionRead.model_validate(redemption, from_attributes=True)

    async def list_redemptions(
        self,
        page: int = 1,
        page_size: int = 50,
        coupon_id: UUID | None = None,
        user_id: str | None = None,
        booking_id: UUID | None = None,
    ) -> dict[str, Any]:
        skip = (page - 1) * page_size

        filters: dict[str, Any] = {}
        if coupon_id is not None:
            filters["coupon_id"] = coupon_id
        if user_id is not None:
            filters["user_id"] = user_id
        if booking_id is not None:
            filters["booking_id"] = booking_id

        redemptions = await self.repo.get_multi(skip=skip, limit=page_size, **filters)
        total = await self.repo.get_count(**filters)

        return {
            "items": [
                CouponRedemptionRead.model_validate(r, from_attributes=True)
                for r in redemptions
            ],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        }

    async def update_redemption(
        self, redemption_id: UUID, redemption_in: CouponRedemptionUpdate
    ) -> CouponRedemptionRead:
        redemption = await self.repo.get_or_404(
            redemption_id, detail="Redemption not found"
        )
        updated = await self.repo.update(redemption, redemption_in)
        return CouponRedemptionRead.model_validate(updated, from_attributes=True)

    async def delete_redemption(self, redemption_id: UUID) -> None:
        await self.repo.delete(redemption_id)

    async def search_redemptions(
        self,
        q: str,
        page: int = 1,
        page_size: int = 20,
        exact_match: bool = False,
        case_sensitive: bool = False,
    ) -> dict[str, Any]:
        skip = (page - 1) * page_size

        results = await self.repo.search(
            query=q,
            search_columns=["currency_code"],
            exact_match=exact_match,
            case_sensitive=case_sensitive,
            skip=skip,
            limit=page_size,
        )
        total = await self.repo.count_search(
            query=q,
            search_columns=["currency_code"],
            exact_match=exact_match,
            case_sensitive=case_sensitive,
        )

        return {
            "items": [
                CouponRedemptionRead.model_validate(r, from_attributes=True)
                for r in results
            ],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        }
