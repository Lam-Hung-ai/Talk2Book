# app/api/v1/endpoints/support_ticket.py
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.v1.deps import get_async_session
from app.schemas.support_ticket import (
    SupportTicketCreate,
    SupportTicketRead,
    SupportTicketUpdate,
)
from app.services.support_ticket import SupportTicketService

router = APIRouter()


def get_support_ticket_service(db: AsyncSession = Depends(get_async_session)) -> SupportTicketService:
    """Dependency để inject SupportTicketService"""
    return SupportTicketService(db)


@router.post(
    "/",
    response_model=SupportTicketRead,
    status_code=status.HTTP_201_CREATED,
    summary="Tạo support ticket mới",
)
async def create_ticket(
    ticket_data: SupportTicketCreate,
    service: SupportTicketService = Depends(get_support_ticket_service)
):
    """
    Tạo support ticket mới

    - **user_id**: UUID của user tạo ticket
    - **booking_id**: UUID của booking liên quan (nếu có)
    - **subject**: Tiêu đề ticket
    - **status**: Trạng thái ticket (mặc định: open)
    """
    return await service.create_ticket(ticket_data)


@router.get("/", response_model=dict, summary="Danh sách tickets có phân trang")
async def get_tickets(
    page: int = Query(1, ge=1, description="Số trang, bắt đầu từ 1"),
    page_size: int = Query(20, ge=1, le=100, description="Số lượng mỗi trang"),
    status: str | None = Query(None, description="Lọc theo trạng thái"),
    user_id: UUID | None = Query(None, description="Lọc theo user_id"),
    service: SupportTicketService = Depends(get_support_ticket_service),
):
    """Lấy danh sách tickets với phân trang và filter"""
    return await service.get_tickets_paginated(
        page=page, page_size=page_size, status=status, user_id=user_id
    )


@router.get("/{ticket_id}", response_model=SupportTicketRead, summary="Lấy thông tin ticket theo ID")
async def get_ticket(
    ticket_id: UUID,
    service: SupportTicketService = Depends(get_support_ticket_service)
):
    """Lấy thông tin ticket theo ID. Ném 404 nếu không tồn tại"""
    ticket = await service.get_ticket(ticket_id)
    return SupportTicketRead.model_validate(ticket, from_attributes=True)


@router.put("/{ticket_id}", response_model=SupportTicketRead, summary="Cập nhật thông tin ticket")
async def update_ticket(
    ticket_id: UUID,
    ticket_data: SupportTicketUpdate,
    service: SupportTicketService = Depends(get_support_ticket_service)
):
    """Cập nhật ticket"""
    updated_ticket = await service.update_ticket(ticket_id, ticket_data)
    return SupportTicketRead.model_validate(updated_ticket, from_attributes=True)


@router.delete("/{ticket_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Xóa ticket")
async def delete_ticket(
    ticket_id: UUID,
    service: SupportTicketService = Depends(get_support_ticket_service)
):
    """Xóa ticket"""
    await service.delete_ticket(ticket_id)
    return None


@router.get("/search/mixin", response_model=dict, summary="Tìm kiếm tickets")
async def search_tickets(
    q: str = Query(..., min_length=1, description="Từ khóa tìm kiếm"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    exact_match: bool = Query(False, description="Tìm chính xác toàn bộ chuỗi"),
    case_sensitive: bool = Query(False, description="Phân biệt hoa/thường"),
    service: SupportTicketService = Depends(get_support_ticket_service),
):
    """Tìm kiếm tickets theo subject"""
    skip = (page - 1) * page_size
    tickets = await service.search_tickets(query=q, skip=skip, limit=page_size)
    total = await service.repo.count_search(
        query=q,
        search_columns=["subject"],
        exact_match=exact_match,
        case_sensitive=case_sensitive
    )
    return {
        "items": [SupportTicketRead.model_validate(t, from_attributes=True) for t in tickets],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size
    }


@router.get("/user/{user_id}", response_model=list[SupportTicketRead])
async def get_user_tickets(
    user_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    service: SupportTicketService = Depends(get_support_ticket_service),
):
    """Lấy tất cả tickets của một user"""
    return await service.get_user_tickets(user_id=user_id, skip=skip, limit=limit)


@router.get("/status/{status}", response_model=list[SupportTicketRead])
async def get_tickets_by_status(
    status: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    service: SupportTicketService = Depends(get_support_ticket_service),
):
    """Lấy tickets theo trạng thái"""
    return await service.get_tickets_by_status(status=status, skip=skip, limit=limit)


@router.get("/booking/{booking_id}", response_model=list[SupportTicketRead])
async def get_booking_tickets(
    booking_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    service: SupportTicketService = Depends(get_support_ticket_service),
):
    """Lấy tất cả tickets của một booking"""
    return await service.get_tickets_by_booking(booking_id=booking_id, skip=skip, limit=limit)

