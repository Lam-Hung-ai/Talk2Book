# app/api/v1/endpoints/payment.py
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.v1.deps import get_async_session
from app.models.enums import PaymentStatus
from app.schemas.payment import PaymentCreate, PaymentRead, PaymentUpdate
from app.services.payment import PaymentService

router = APIRouter()


def get_payment_service(
    db: AsyncSession = Depends(get_async_session),
) -> PaymentService:
    """Dependency để inject PaymentService"""
    return PaymentService(db)


@router.post(
    "/",
    response_model=PaymentRead,
    status_code=status.HTTP_201_CREATED,
    summary="Tạo payment mới",
)
async def create_payment(
    payment_data: PaymentCreate, service: PaymentService = Depends(get_payment_service)
):
    """
    Tạo payment mới
    """
    return await service.create_payment(payment_data)


@router.get("/{payment_id}", response_model=PaymentRead, summary="Lấy thông tin payment theo ID")
async def get_payment(
    payment_id: UUID, service: PaymentService = Depends(get_payment_service)
):
    """
    Lấy thông tin payment theo ID. Ném 404 nếu không tồn tại
    """
    payment = await service.get_payment_by_id(payment_id)
    return PaymentRead.model_validate(payment, from_attributes=True)


@router.get("/", response_model=dict, summary="Danh sách payments có phân trang")
async def get_payments(
    page: int = Query(1, ge=1, description="Số trang, bắt đầu từ 1"),
    page_size: int = Query(20, ge=1, le=100, description="Số lượng mỗi trang"),
    booking_id: UUID | None = Query(None, description="Lọc theo booking_id"),
    status: PaymentStatus | None = Query(None, description="Lọc theo trạng thái"),
    provider: str | None = Query(None, description="Lọc theo payment gateway"),
    service: PaymentService = Depends(get_payment_service),
):
    """
    Lấy danh sách payments với phân trang và filter
    """
    return await service.get_payments_paginated(
        page=page, page_size=page_size, booking_id=booking_id, status=status, provider=provider
    )


@router.put("/{payment_id}", response_model=PaymentRead, summary="Cập nhật thông tin payment")
async def update_payment(
    payment_id: UUID, payment_data: PaymentUpdate, service: PaymentService = Depends(get_payment_service)
):
    """
    Cập nhật payment
    """
    return await service.update_payment(payment_id, payment_data)


@router.delete("/{payment_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Xóa payment")
async def delete_payment(
    payment_id: UUID, service: PaymentService = Depends(get_payment_service)
):
    """
    Xóa payment
    """
    await service.delete_payment(payment_id)
    return None


@router.get(
    "/search/mixin", response_model=dict, summary="Tìm kiếm payments"
)
async def search_payments(
    q: str = Query(..., min_length=1, description="Từ khóa tìm kiếm"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    exact_match: bool = Query(False, description="Tìm chính xác toàn bộ chuỗi"),
    case_sensitive: bool = Query(False, description="Phân biệt hoa/thường"),
    service: PaymentService = Depends(get_payment_service),
):
    """
    Tìm kiếm payments theo provider hoặc currency_code
    """
    return await service.search_payments(
        q=q,
        page=page,
        page_size=page_size,
        exact_match=exact_match,
        case_sensitive=case_sensitive,
    )
