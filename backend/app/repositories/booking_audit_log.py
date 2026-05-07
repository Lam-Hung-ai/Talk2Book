from collections.abc import Sequence
from uuid import UUID

from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.booking_audit_log import BookingAuditLog
from app.repositories.base import BaseCRUD
from app.repositories.searchable import SearchableRepository
from app.schemas.booking_audit_log import BookingAuditLogCreate, BookingAuditLogUpdate


class BookingAuditLogRepository(
    BaseCRUD[BookingAuditLog, BookingAuditLogCreate, BookingAuditLogUpdate],
    SearchableRepository[BookingAuditLog],
):
    def __init__(self, db: AsyncSession):
        BaseCRUD.__init__(self, BookingAuditLog, db)
        SearchableRepository.__init__(self, BookingAuditLog, db)

    async def get_by_booking(
        self, booking_id: UUID, *, skip: int = 0, limit: int = 100
    ) -> Sequence[BookingAuditLog]:
        return await self.get_multi(skip=skip, limit=limit, booking_id=booking_id)
