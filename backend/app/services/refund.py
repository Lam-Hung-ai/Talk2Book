# app/services/refund.py
from typing import Any
from uuid import UUID

from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.enums import RefundStatus
from app.models.refund import Refund
from app.repositories.booking import BookingRepository
from app.repositories.refund import RefundRepository
from app.schemas.refund import RefundCreate, RefundRead, RefundUpdate


class RefundService:
    """Service layer cho Refund business logic"""

    def __init__(self, db: AsyncSession):
        self.repo = RefundRepository(db)
        self.booking_repo = BookingRepository(db)
        self.db = db

    async def create_refund(self, refund_data: RefundCreate) -> RefundRead:
        """Tạo refund mới"""
        # Validate booking tồn tại
        booking = await self.booking_repo.get_or_404(
            refund_data.booking_id,
            detail="Booking không tồn tại"
        )

        # Validate amount > 0 (đã được validate trong schema)
        # Có thể thêm logic kiểm tra tổng refund không vượt quá booking amount nếu cần

        db_refund = await self.repo.create(refund_data.model_dump())
        return RefundRead.model_validate(db_refund, from_attributes=True)

    async def get_refund_by_id(self, refund_id: UUID) -> Refund:
        """Lấy refund theo ID"""
        return await self.repo.get_or_404(refund_id, detail="Refund không tồn tại")

    async def get_refunds_paginated(
        self,
        page: int = 1,
        page_size: int = 20,
        booking_id: UUID | None = None,
        status: RefundStatus | None = None
    ) -> dict[str, Any]:
        """Lấy danh sách refunds có phân trang và filter"""
        skip = (page - 1) * page_size

        filters = {}
        if booking_id is not None:
            filters["booking_id"] = booking_id
        if status is not None:
            filters["status"] = status

        refunds = await self.repo.get_multi(skip=skip, limit=page_size, **filters)
        total = await self.repo.get_count(**filters)

        return {
            "items": [RefundRead.model_validate(r, from_attributes=True) for r in refunds],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }

    async def update_refund(
        self,
        refund_id: UUID,
        refund_data: RefundUpdate
    ) -> RefundRead:
        """Cập nhật refund"""
        refund = await self.get_refund_by_id(refund_id)
        updated_refund = await self.repo.update(refund, refund_data)
        return RefundRead.model_validate(updated_refund, from_attributes=True)

    async def delete_refund(self, refund_id: UUID) -> None:
        """Xóa refund"""
        await self.repo.delete(refund_id)

    async def search_refunds(
        self,
        q: str,
        page: int = 1,
        page_size: int = 20,
        exact_match: bool = False,
        case_sensitive: bool = False
    ) -> dict[str, Any]:
        """Tìm kiếm refunds theo reason hoặc status"""
        skip = (page - 1) * page_size

        refunds = await self.repo.search(
            query=q,
            search_columns=["reason"],
            exact_match=exact_match,
            case_sensitive=case_sensitive,
            skip=skip,
            limit=page_size
        )

        total = await self.repo.count_search(
            query=q,
            search_columns=["reason"],
            exact_match=exact_match,
            case_sensitive=case_sensitive
        )

        return {
            "items": [RefundRead.model_validate(r, from_attributes=True) for r in refunds],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }
