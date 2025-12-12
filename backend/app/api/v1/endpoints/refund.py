# app/api/v1/endpoints/refund.py
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.v1.deps import get_async_session
from app.models.enums import RefundStatus
from app.schemas.refund import RefundCreate, RefundRead, RefundUpdate
from app.services.refund import RefundService

router = APIRouter()


def get_refund_service(db: AsyncSession = Depends(get_async_session)) -> RefundService:
    """Dependency để inject RefundService"""
    return RefundService(db)


@router.post(
    "/",
    response_model=RefundRead,
    status_code=status.HTTP_201_CREATED,
    summary="Tạo refund mới",
)
async def create_refund(
    refund_data: RefundCreate, service: RefundService = Depends(get_refund_service)
):
    """
    Tạo refund mới
    """
    return await service.create_refund(refund_data)


@router.get("/{refund_id}", response_model=RefundRead, summary="Lấy thông tin refund theo ID")
async def get_refund(
    refund_id: UUID, service: RefundService = Depends(get_refund_service)
):
    """
    Lấy thông tin refund theo ID. Ném 404 nếu không tồn tại
    """
    refund = await service.get_refund_by_id(refund_id)
    return RefundRead.model_validate(refund, from_attributes=True)


@router.get("/", response_model=dict, summary="Danh sách refunds có phân trang")
async def get_refunds(
    page: int = Query(1, ge=1, description="Số trang, bắt đầu từ 1"),
    page_size: int = Query(20, ge=1, le=100, description="Số lượng mỗi trang"),
    booking_id: UUID | None = Query(None, description="Lọc theo booking_id"),
    status: RefundStatus | None = Query(None, description="Lọc theo trạng thái"),
    service: RefundService = Depends(get_refund_service),
):
    """
    Lấy danh sách refunds với phân trang và filter
    """
    return await service.get_refunds_paginated(
        page=page, page_size=page_size, booking_id=booking_id, status=status
    )


@router.put("/{refund_id}", response_model=RefundRead, summary="Cập nhật thông tin refund")
async def update_refund(
    refund_id: UUID, refund_data: RefundUpdate, service: RefundService = Depends(get_refund_service)
):
    """
    Cập nhật refund
    """
    return await service.update_refund(refund_id, refund_data)


@router.delete("/{refund_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Xóa refund")
async def delete_refund(
    refund_id: UUID, service: RefundService = Depends(get_refund_service)
):
    """
    Xóa refund
    """
    await service.delete_refund(refund_id)
    return None


@router.get(
    "/search/mixin", response_model=dict, summary="Tìm kiếm refunds"
)
async def search_refunds(
    q: str = Query(..., min_length=1, description="Từ khóa tìm kiếm"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    exact_match: bool = Query(False, description="Tìm chính xác toàn bộ chuỗi"),
    case_sensitive: bool = Query(False, description="Phân biệt hoa/thường"),
    service: RefundService = Depends(get_refund_service),
):
    """
    Tìm kiếm refunds theo reason
    """
    return await service.search_refunds(
        q=q,
        page=page,
        page_size=page_size,
        exact_match=exact_match,
        case_sensitive=case_sensitive,
    )
