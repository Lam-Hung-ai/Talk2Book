from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.v1.deps import get_async_session
from app.schemas.coupon_redemption import (
    CouponRedemptionCreate,
    CouponRedemptionRead,
    CouponRedemptionUpdate,
)
from app.services.coupon_redemption import CouponRedemptionService

router = APIRouter()


def get_coupon_redemption_service(
    db: AsyncSession = Depends(get_async_session),
) -> CouponRedemptionService:
    return CouponRedemptionService(db)


@router.post(
    "/",
    response_model=CouponRedemptionRead,
    status_code=status.HTTP_201_CREATED,
    summary="Tạo coupon redemption",
)
async def create_redemption(
    redemption_in: CouponRedemptionCreate,
    service: CouponRedemptionService = Depends(get_coupon_redemption_service),
):
    return await service.create_redemption(redemption_in)


@router.get(
    "/{redemption_id}",
    response_model=CouponRedemptionRead,
    summary="Lấy redemption theo ID",
)
async def get_redemption(
    redemption_id: UUID,
    service: CouponRedemptionService = Depends(get_coupon_redemption_service),
):
    return await service.get_redemption(redemption_id)


@router.get("/", response_model=dict, summary="Danh sách redemption có phân trang")
async def list_redemptions(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    coupon_id: UUID | None = Query(None),
    user_id: UUID | None = Query(None),
    booking_id: UUID | None = Query(None),
    service: CouponRedemptionService = Depends(get_coupon_redemption_service),
):
    return await service.list_redemptions(
        page=page,
        page_size=page_size,
        coupon_id=coupon_id,
        user_id=user_id,
        booking_id=booking_id,
    )


@router.put(
    "/{redemption_id}",
    response_model=CouponRedemptionRead,
    summary="Cập nhật redemption",
)
async def update_redemption(
    redemption_id: UUID,
    redemption_in: CouponRedemptionUpdate,
    service: CouponRedemptionService = Depends(get_coupon_redemption_service),
):
    return await service.update_redemption(redemption_id, redemption_in)


@router.delete(
    "/{redemption_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Xóa redemption",
)
async def delete_redemption(
    redemption_id: UUID,
    service: CouponRedemptionService = Depends(get_coupon_redemption_service),
):
    await service.delete_redemption(redemption_id)
    return None


@router.get("/search/mixin", response_model=dict, summary="Tìm kiếm redemption")
async def search_redemptions(
    q: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    exact_match: bool = Query(False),
    case_sensitive: bool = Query(False),
    service: CouponRedemptionService = Depends(get_coupon_redemption_service),
):
    return await service.search_redemptions(
        q=q,
        page=page,
        page_size=page_size,
        exact_match=exact_match,
        case_sensitive=case_sensitive,
    )

