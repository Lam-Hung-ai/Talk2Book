# app/services/support_ticket.py
from collections.abc import Sequence
from typing import Any
from uuid import UUID

from fastapi import HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.support_ticket import SupportTicket
from app.repositories.support_ticket import SupportTicketRepository
from app.schemas.support_ticket import SupportTicketCreate, SupportTicketRead, SupportTicketUpdate


class SupportTicketService:
    """Service layer cho SupportTicket business logic"""

    def __init__(self, db: AsyncSession):
        self.repo = SupportTicketRepository(db)
        self.db = db

    async def create_ticket(self, ticket_data: SupportTicketCreate) -> SupportTicket:
        """Tạo ticket mới"""
        return await self.repo.create(ticket_data)

    async def get_ticket(self, ticket_id: UUID) -> SupportTicket:
        """Lấy ticket theo ID"""
        return await self.repo.get_or_404(ticket_id, detail="Support ticket không tồn tại")

    async def get_tickets(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> Sequence[SupportTicket]:
        """Lấy danh sách tất cả tickets"""
        return await self.repo.get_multi(skip=skip, limit=limit)

    async def get_user_tickets(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> Sequence[SupportTicket]:
        """Lấy tickets của user"""
        return await self.repo.get_by_user_id(user_id, skip=skip, limit=limit)

    async def get_tickets_by_status(
        self,
        status: str,
        skip: int = 0,
        limit: int = 100
    ) -> Sequence[SupportTicket]:
        """Lấy tickets theo trạng thái"""
        return await self.repo.get_by_status(status, skip=skip, limit=limit)

    async def get_tickets_by_booking(
        self,
        booking_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> Sequence[SupportTicket]:
        """Lấy tickets của một booking"""
        return await self.repo.get_by_booking_id(booking_id, skip=skip, limit=limit)

    async def update_ticket(
        self,
        ticket_id: UUID,
        ticket_data: SupportTicketUpdate
    ) -> SupportTicket:
        """Cập nhật ticket"""
        ticket = await self.repo.get_or_404(ticket_id, detail="Support ticket không tồn tại")
        return await self.repo.update(ticket, ticket_data)

    async def delete_ticket(self, ticket_id: UUID) -> None:
        """Xóa ticket"""
        await self.repo.delete(ticket_id)

    async def search_tickets(
        self,
        query: str,
        search_fields: list[str] | None = None,
        skip: int = 0,
        limit: int = 20
    ) -> Sequence[SupportTicket]:
        """Tìm kiếm tickets"""
        if search_fields is None:
            search_fields = ["subject"]

        return await self.repo.search(
            query=query,
            search_columns=search_fields,
            skip=skip,
            limit=limit
        )

    async def get_tickets_paginated(
        self,
        page: int = 1,
        page_size: int = 20,
        status: str | None = None,
        user_id: UUID | None = None
    ) -> dict[str, Any]:
        """Lấy danh sách tickets có phân trang và filter"""
        skip = (page - 1) * page_size

        filters = {}
        if status is not None:
            filters["status"] = status
        if user_id is not None:
            filters["user_id"] = user_id

        tickets = await self.repo.get_multi(skip=skip, limit=page_size, **filters)
        total = await self.repo.get_count(**filters)

        return {
            "items": [SupportTicketRead.model_validate(t, from_attributes=True) for t in tickets],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }

