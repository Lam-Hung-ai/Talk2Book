# app/api/v1/endpoints/payment.py
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.v1.deps import get_async_session
from app.schemas.payment import (
    PaymentCreate,
    PaymentResponse,
    PaymentUpdate,
)
from app.services.payment import PaymentService

router = APIRouter()


def get_payment_service(
    db: AsyncSession = Depends(get_async_session),
) -> PaymentService:
    """Dependency để inject PaymentService"""
    return PaymentService(db)


@router.post("/", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def create_payment(
    payment_data: PaymentCreate, service: PaymentService = Depends(get_payment_service)
):
    """
    Tạo payment mới

    - **user_id**: UUID của user
    - **booking_id**: ID của booking (optional)
    - **gateway**: Payment gateway (VNPay, Momo, ZaloPay, etc.)
    - **amount**: Số tiền thanh toán
    - **currency**: Loại tiền tệ (mặc định VND)
    - **status**: Trạng thái payment
    """
    return await service.create_payment(payment_data)


@router.get("/search/", response_model=list[PaymentResponse])
async def search_payments(
    q: str = Query(..., min_length=1, description="Từ khóa tìm kiếm"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    service: PaymentService = Depends(get_payment_service),
):
    """
    Tìm kiếm payments theo gateway, status, hoặc currency
    """
    return await service.search_payments(query=q, skip=skip, limit=limit)


@router.get("/user/{user_id}/stats")
async def get_user_payment_stats(
    user_id: UUID, service: PaymentService = Depends(get_payment_service)
):
    """Lấy thống kê payment của user"""
    return await service.get_user_payment_stats(user_id)


@router.get("/user/{user_id}", response_model=list[PaymentResponse])
async def get_user_payments(
    user_id: UUID,
    status_filter: str | None = Query(
        None, alias="status", description="Filter theo status"
    ),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    service: PaymentService = Depends(get_payment_service),
):
    """Lấy danh sách payments của một user"""
    return await service.get_user_payments(
        user_id=user_id, status=status_filter, skip=skip, limit=limit
    )


@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(
    payment_id: int, service: PaymentService = Depends(get_payment_service)
):
    """Lấy thông tin payment theo ID"""
    return await service.get_payment(payment_id)


@router.get("/")
async def get_payments(
    skip: int = Query(0, ge=0, description="Số bản ghi bỏ qua"),
    limit: int = Query(100, ge=1, le=100, description="Số bản ghi tối đa"),
    service: PaymentService = Depends(get_payment_service),
):
    """Lấy danh sách tất cả payments với pagination"""
    items = await service.get_payments(skip=skip, limit=limit)
    total = await service.repo.get_count()

    return {"total": total, "items": items, "skip": skip, "limit": limit}


@router.put("/{payment_id}", response_model=PaymentResponse)
async def update_payment(
    payment_id: int,
    payment_data: PaymentUpdate,
    service: PaymentService = Depends(get_payment_service),
):
    """Cập nhật thông tin payment"""
    return await service.update_payment(payment_id, payment_data)


@router.patch("/{payment_id}/status", response_model=PaymentResponse)
async def update_payment_status(
    payment_id: int,
    new_status: str = Query(
        ...,
        description="Trạng thái mới: pending, completed, failed, refunded, cancelled",
    ),
    service: PaymentService = Depends(get_payment_service),
):
    """Cập nhật trạng thái payment"""
    return await service.update_payment_status(payment_id, new_status)


@router.delete("/{payment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_payment(
    payment_id: int, service: PaymentService = Depends(get_payment_service)
):
    """Xóa payment"""
    await service.delete_payment(payment_id)
