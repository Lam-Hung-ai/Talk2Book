# app/api/v1/endpoints/refund.py
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.v1.deps import get_async_session
from app.services.refund import RefundService
from app.schemas.refund import (
    RefundCreate, 
    RefundUpdate, 
    RefundResponse, 
    RefundListResponse
)

router = APIRouter()


def get_refund_service(db: AsyncSession = Depends(get_async_session)) -> RefundService:
    """Dependency để inject RefundService"""
    return RefundService(db)


@router.post("/", response_model=RefundResponse, status_code=status.HTTP_201_CREATED)
async def create_refund(
    refund_data: RefundCreate,
    service: RefundService = Depends(get_refund_service)
):
    """
    Tạo refund mới
    
    - **payment_id**: ID của payment cần hoàn tiền
    - **amount**: Số tiền hoàn lại (phải <= payment amount)
    - **reason**: Lý do hoàn tiền
    - **status**: Trạng thái refund (pending, approved, rejected, completed)
    """
    return await service.create_refund(refund_data)


@router.get("/search/", response_model=list[RefundResponse])
async def search_refunds(
    q: str = Query(..., min_length=1, description="Từ khóa tìm kiếm"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    service: RefundService = Depends(get_refund_service)
):
    """
    Tìm kiếm refunds theo reason hoặc status
    """
    return await service.search_refunds(
        query=q,
        skip=skip,
        limit=limit
    )


@router.get("/pending/", response_model=list[RefundResponse])
async def get_pending_refunds(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    service: RefundService = Depends(get_refund_service)
):
    """Lấy danh sách refunds đang chờ xử lý"""
    return await service.repo.get_pending_refunds(skip=skip, limit=limit)


@router.get("/approved/", response_model=list[RefundResponse])
async def get_approved_refunds(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    service: RefundService = Depends(get_refund_service)
):
    """Lấy danh sách refunds đã được duyệt"""
    return await service.repo.get_approved_refunds(skip=skip, limit=limit)


@router.get("/payment/{payment_id}", response_model=list[RefundResponse])
async def get_refunds_by_payment(
    payment_id: int,
    service: RefundService = Depends(get_refund_service)
):
    """Lấy danh sách refunds của một payment"""
    return await service.get_refunds_by_payment(payment_id)


@router.get("/payment/{payment_id}/stats")
async def get_payment_refund_stats(
    payment_id: int,
    service: RefundService = Depends(get_refund_service)
):
    """Lấy thống kê refund của một payment"""
    return await service.get_payment_refund_stats(payment_id)


@router.get("/{refund_id}", response_model=RefundResponse)
async def get_refund(
    refund_id: int,
    service: RefundService = Depends(get_refund_service)
):
    """Lấy thông tin refund theo ID"""
    return await service.get_refund(refund_id)


@router.get("/")
async def get_refunds(
    skip: int = Query(0, ge=0, description="Số bản ghi bỏ qua"),
    limit: int = Query(100, ge=1, le=100, description="Số bản ghi tối đa"),
    service: RefundService = Depends(get_refund_service)
):
    """Lấy danh sách tất cả refunds với pagination"""
    items = await service.get_refunds(skip=skip, limit=limit)
    total = await service.repo.get_count()
    
    return {
        "total": total,
        "items": items,
        "skip": skip,
        "limit": limit
    }


@router.put("/{refund_id}", response_model=RefundResponse)
async def update_refund(
    refund_id: int,
    refund_data: RefundUpdate,
    service: RefundService = Depends(get_refund_service)
):
    """Cập nhật thông tin refund"""
    return await service.update_refund(refund_id, refund_data)


@router.patch("/{refund_id}/status", response_model=RefundResponse)
async def update_refund_status(
    refund_id: int,
    new_status: str = Query(..., description="Trạng thái mới: pending, approved, rejected, completed, cancelled"),
    service: RefundService = Depends(get_refund_service)
):
    """Cập nhật trạng thái refund"""
    return await service.update_refund_status(refund_id, new_status)


@router.patch("/{refund_id}/approve", response_model=RefundResponse)
async def approve_refund(
    refund_id: int,
    service: RefundService = Depends(get_refund_service)
):
    """Duyệt refund"""
    return await service.approve_refund(refund_id)


@router.patch("/{refund_id}/reject", response_model=RefundResponse)
async def reject_refund(
    refund_id: int,
    service: RefundService = Depends(get_refund_service)
):
    """Từ chối refund"""
    return await service.reject_refund(refund_id)


@router.patch("/{refund_id}/complete", response_model=RefundResponse)
async def complete_refund(
    refund_id: int,
    service: RefundService = Depends(get_refund_service)
):
    """Hoàn thành refund (chỉ khi đã approved)"""
    return await service.complete_refund(refund_id)


@router.delete("/{refund_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_refund(
    refund_id: int,
    service: RefundService = Depends(get_refund_service)
):
    """Xóa refund (chỉ cho phép pending hoặc rejected)"""
    await service.delete_refund(refund_id)
