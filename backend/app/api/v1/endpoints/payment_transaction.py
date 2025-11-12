# app/api/v1/endpoints/payment_transaction.py
from typing import Optional
from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.v1.deps import get_async_session
from app.services.payment_transaction import PaymentTransactionService
from app.schemas.payment_transaction import (
    PaymentTransactionCreate,
    PaymentTransactionUpdate,
    PaymentTransactionResponse,
    PaymentTransactionListResponse
)

router = APIRouter()


def get_transaction_service(
    db: AsyncSession = Depends(get_async_session)
) -> PaymentTransactionService:
    """Dependency để inject PaymentTransactionService"""
    return PaymentTransactionService(db)


@router.post("/", response_model=PaymentTransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    transaction_data: PaymentTransactionCreate,
    service: PaymentTransactionService = Depends(get_transaction_service)
):
    """
    Tạo payment transaction mới
    
    - **payment_id**: ID của payment
    - **step**: Bước trong quy trình (init, verify, process, complete, etc.)
    - **status**: Trạng thái (pending, processing, success, failed)
    """
    return await service.create_transaction(transaction_data)


@router.get("/search/", response_model=list[PaymentTransactionResponse])
async def search_transactions(
    q: str = Query(..., min_length=1, description="Từ khóa tìm kiếm"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    service: PaymentTransactionService = Depends(get_transaction_service)
):
    """Tìm kiếm transactions theo step hoặc status"""
    return await service.search_transactions(
        query=q,
        skip=skip,
        limit=limit
    )


@router.get("/failed/", response_model=list[PaymentTransactionResponse])
async def get_failed_transactions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    service: PaymentTransactionService = Depends(get_transaction_service)
):
    """Lấy danh sách transactions failed"""
    return await service.repo.get_failed_transactions(skip=skip, limit=limit)


@router.get("/success/", response_model=list[PaymentTransactionResponse])
async def get_success_transactions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    service: PaymentTransactionService = Depends(get_transaction_service)
):
    """Lấy danh sách transactions success"""
    return await service.repo.get_success_transactions(skip=skip, limit=limit)


@router.get("/payment/{payment_id}", response_model=list[PaymentTransactionResponse])
async def get_payment_transactions(
    payment_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    service: PaymentTransactionService = Depends(get_transaction_service)
):
    """Lấy lịch sử transactions của một payment (theo thứ tự thời gian)"""
    return await service.get_payment_transactions(
        payment_id=payment_id,
        skip=skip,
        limit=limit
    )


@router.get("/payment/{payment_id}/latest", response_model=PaymentTransactionResponse)
async def get_latest_transaction(
    payment_id: int,
    service: PaymentTransactionService = Depends(get_transaction_service)
):
    """Lấy transaction mới nhất của một payment"""
    transaction = await service.get_latest_transaction(payment_id)
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No transactions found for this payment"
        )
    return transaction


@router.get("/payment/{payment_id}/stats")
async def get_payment_transaction_stats(
    payment_id: int,
    service: PaymentTransactionService = Depends(get_transaction_service)
):
    """Lấy thống kê transactions của một payment"""
    return await service.get_payment_transaction_stats(payment_id)


@router.get("/status/{status_filter}", response_model=list[PaymentTransactionResponse])
async def get_transactions_by_status(
    status_filter: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    service: PaymentTransactionService = Depends(get_transaction_service)
):
    """Lấy transactions theo status"""
    return await service.get_transactions_by_status(
        status_filter=status_filter,
        skip=skip,
        limit=limit
    )


@router.get("/step/{step}", response_model=list[PaymentTransactionResponse])
async def get_transactions_by_step(
    step: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    service: PaymentTransactionService = Depends(get_transaction_service)
):
    """Lấy transactions theo step"""
    return await service.get_transactions_by_step(
        step=step,
        skip=skip,
        limit=limit
    )


@router.get("/{transaction_id}", response_model=PaymentTransactionResponse)
async def get_transaction(
    transaction_id: int,
    service: PaymentTransactionService = Depends(get_transaction_service)
):
    """Lấy thông tin transaction theo ID"""
    return await service.get_transaction(transaction_id)


@router.get("/")
async def get_transactions(
    skip: int = Query(0, ge=0, description="Số bản ghi bỏ qua"),
    limit: int = Query(100, ge=1, le=100, description="Số bản ghi tối đa"),
    service: PaymentTransactionService = Depends(get_transaction_service)
):
    """Lấy danh sách tất cả transactions với pagination"""
    items = await service.get_transactions(skip=skip, limit=limit)
    total = await service.repo.get_count()
    
    return {
        "total": total,
        "items": items,
        "skip": skip,
        "limit": limit
    }


@router.put("/{transaction_id}", response_model=PaymentTransactionResponse)
async def update_transaction(
    transaction_id: int,
    transaction_data: PaymentTransactionUpdate,
    service: PaymentTransactionService = Depends(get_transaction_service)
):
    """Cập nhật transaction"""
    return await service.update_transaction(transaction_id, transaction_data)


@router.patch("/{transaction_id}/status", response_model=PaymentTransactionResponse)
async def update_transaction_status(
    transaction_id: int,
    new_status: str = Query(
        ...,
        description="Trạng thái mới: pending, processing, success, failed, cancelled"
    ),
    service: PaymentTransactionService = Depends(get_transaction_service)
):
    """Cập nhật trạng thái transaction"""
    return await service.update_transaction_status(transaction_id, new_status)


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(
    transaction_id: int,
    service: PaymentTransactionService = Depends(get_transaction_service)
):
    """Xóa transaction"""
    await service.delete_transaction(transaction_id)
