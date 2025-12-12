from typing import Any
from uuid import UUID

from fastapi import HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.repositories.booking import BookingRepository
from app.repositories.booking_audit_log import BookingAuditLogRepository
from app.schemas.booking_audit_log import (
    BookingAuditLogCreate,
    BookingAuditLogRead,
    BookingAuditLogUpdate,
)


class BookingAuditLogService:
    def __init__(self, db: AsyncSession):
        self.repo = BookingAuditLogRepository(db)
        self.booking_repo = BookingRepository(db)

    async def create_log(self, log_in: BookingAuditLogCreate) -> BookingAuditLogRead:
        if not await self.booking_repo.get(log_in.booking_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found"
            )

        log = await self.repo.create(log_in)
        return BookingAuditLogRead.model_validate(log, from_attributes=True)

    async def get_log(self, log_id: UUID) -> BookingAuditLogRead:
        log = await self.repo.get_or_404(log_id, detail="Booking audit log not found")
        return BookingAuditLogRead.model_validate(log, from_attributes=True)

    async def list_logs(
        self,
        page: int = 1,
        page_size: int = 50,
        booking_id: UUID | None = None,
    ) -> dict[str, Any]:
        skip = (page - 1) * page_size
        filters: dict[str, Any] = {}
        if booking_id is not None:
            filters["booking_id"] = booking_id

        logs = await self.repo.get_multi(skip=skip, limit=page_size, **filters)
        total = await self.repo.get_count(**filters)

        return {
            "items": [BookingAuditLogRead.model_validate(l, from_attributes=True) for l in logs],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        }

    async def update_log(
        self, log_id: UUID, log_in: BookingAuditLogUpdate
    ) -> BookingAuditLogRead:
        log = await self.repo.get_or_404(log_id, detail="Booking audit log not found")
        updated = await self.repo.update(log, log_in)
        return BookingAuditLogRead.model_validate(updated, from_attributes=True)

    async def delete_log(self, log_id: UUID) -> None:
        await self.repo.delete(log_id)

    async def search_logs(
        self,
        q: str,
        page: int = 1,
        page_size: int = 20,
        exact_match: bool = False,
        case_sensitive: bool = False,
    ) -> dict[str, Any]:
        skip = (page - 1) * page_size

        logs = await self.repo.search(
            query=q,
            search_columns=["action"],
            exact_match=exact_match,
            case_sensitive=case_sensitive,
            skip=skip,
            limit=page_size,
        )
        total = await self.repo.count_search(
            query=q,
            search_columns=["action"],
            exact_match=exact_match,
            case_sensitive=case_sensitive,
        )

        return {
            "items": [BookingAuditLogRead.model_validate(l, from_attributes=True) for l in logs],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        }

