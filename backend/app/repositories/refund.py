# app/repositories/refund.py
from collections.abc import Sequence
from uuid import UUID

from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.enums import RefundStatus
from app.models.refund import Refund
from app.repositories.base import BaseCRUD
from app.repositories.searchable import SearchableRepository
from app.schemas.refund import RefundCreate, RefundUpdate


class RefundRepository(BaseCRUD[Refund, RefundCreate, RefundUpdate], SearchableRepository[Refund]):
    """Repository cho Refund với đầy đủ CRUD và tính năng tìm kiếm"""

    def __init__(self, db: AsyncSession):
        # Khởi tạo cả 2 class cha
        BaseCRUD.__init__(self, Refund, db)
        SearchableRepository.__init__(self, Refund, db)

    async def get_by_booking_id(self, booking_id: UUID, skip: int = 0, limit: int = 100) -> Sequence[Refund]:
        """Lấy danh sách refunds theo booking_id"""
        return await self.get_multi(skip=skip, limit=limit, booking_id=booking_id)

    async def get_by_status(
        self,
        status: RefundStatus,
        skip: int = 0,
        limit: int = 100
    ) -> Sequence[Refund]:
        """Lấy refunds theo trạng thái"""
        return await self.get_multi(skip=skip, limit=limit, status=status)
