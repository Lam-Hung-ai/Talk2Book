from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.v1.deps import get_async_session
from app.schemas.coupon import CouponCreate, CouponRead, CouponUpdate
from app.services.coupon import CouponService

router = APIRouter()


def get_coupon_service(db: AsyncSession = Depends(get_async_session)) -> CouponService:
    return CouponService(db)


@router.post(
    "/",
    response_model=CouponRead,
    status_code=status.HTTP_201_CREATED,
    summary="Tạo coupon",
)
async def create_coupon(
    coupon_in: CouponCreate, service: CouponService = Depends(get_coupon_service)
):
    return await service.create_coupon(coupon_in)


@router.get(
    "/{coupon_id}",
    response_model=CouponRead,
    summary="Lấy coupon theo ID",
)
async def get_coupon(
    coupon_id: UUID, service: CouponService = Depends(get_coupon_service)
):
    return await service.get_coupon(coupon_id)


@router.get("/", response_model=dict, summary="Danh sách coupon có phân trang")
async def list_coupons(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    is_active: bool | None = Query(None),
    service: CouponService = Depends(get_coupon_service),
):
    return await service.list_coupons(
        page=page, page_size=page_size, is_active=is_active
    )


@router.put(
    "/{coupon_id}",
    response_model=CouponRead,
    summary="Cập nhật coupon",
)
async def update_coupon(
    coupon_id: UUID,
    coupon_in: CouponUpdate,
    service: CouponService = Depends(get_coupon_service),
):
    return await service.update_coupon(coupon_id, coupon_in)


@router.delete(
    "/{coupon_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Xóa coupon",
)
async def delete_coupon(
    coupon_id: UUID, service: CouponService = Depends(get_coupon_service)
):
    await service.delete_coupon(coupon_id)
    return None


@router.get("/search/mixin", response_model=dict, summary="Tìm kiếm coupon")
async def search_coupons(
    q: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    exact_match: bool = Query(False),
    case_sensitive: bool = Query(False),
    service: CouponService = Depends(get_coupon_service),
):
    return await service.search_coupons(
        q=q,
        page=page,
        page_size=page_size,
        exact_match=exact_match,
        case_sensitive=case_sensitive,
    )
