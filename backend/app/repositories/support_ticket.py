# app/repositories/support_ticket.py
from collections.abc import Sequence
from uuid import UUID

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.support_ticket import SupportTicket
from app.repositories.base import BaseCRUD
from app.repositories.searchable import SearchableRepository
from app.schemas.support_ticket import SupportTicketCreate, SupportTicketUpdate


class SupportTicketRepository(BaseCRUD[SupportTicket, SupportTicketCreate, SupportTicketUpdate], SearchableRepository[SupportTicket]):
    """Repository cho SupportTicket với đầy đủ CRUD và tính năng tìm kiếm"""

    def __init__(self, db: AsyncSession):
        BaseCRUD.__init__(self, SupportTicket, db)
        SearchableRepository.__init__(self, SupportTicket, db)

    async def get_by_user_id(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> Sequence[SupportTicket]:
        """Lấy danh sách tickets của một user"""
        return await self.get_multi(skip=skip, limit=limit, user_id=user_id)

    async def get_by_status(
        self,
        status: str,
        skip: int = 0,
        limit: int = 100
    ) -> Sequence[SupportTicket]:
        """Lấy tickets theo trạng thái"""
        return await self.get_multi(skip=skip, limit=limit, status=status)

    async def get_by_booking_id(
        self,
        booking_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> Sequence[SupportTicket]:
        """Lấy tickets của một booking"""
        statement = select(SupportTicket).where(
            SupportTicket.booking_id == booking_id
        ).offset(skip).limit(limit)
        result = await self.db.exec(statement)
        return result.all()

    async def count_by_user_id(self, user_id: UUID) -> int:
        """Đếm số lượng tickets của user"""
        return await self.get_count(user_id=user_id)

    async def count_by_status(self, status: str) -> int:
        """Đếm số lượng tickets theo trạng thái"""
        return await self.get_count(status=status)

