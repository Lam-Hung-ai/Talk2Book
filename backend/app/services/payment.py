# app/services/payment.py
from typing import Any
from uuid import UUID

from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.enums import PaymentStatus
from app.models.payment import Payment
from app.repositories.payment import PaymentRepository
from app.schemas.payment import PaymentCreate, PaymentRead, PaymentUpdate


class PaymentService:
    """Service layer cho Payment business logic"""

    def __init__(self, db: AsyncSession):
        self.repo = PaymentRepository(db)
        self.db = db

    async def create_payment(self, payment_data: PaymentCreate) -> PaymentRead:
        """Tạo payment mới"""
        # Kiểm tra idempotency_key nếu có
        if payment_data.idempotency_key:
            existing = await self.repo.get_by_idempotency_key(
                payment_data.idempotency_key
            )
            if existing:
                return PaymentRead.model_validate(existing, from_attributes=True)

        db_payment = await self.repo.create(payment_data.model_dump())
        return PaymentRead.model_validate(db_payment, from_attributes=True)

    async def get_payment_by_id(self, payment_id: UUID) -> Payment:
        """Lấy payment theo ID"""
        return await self.repo.get_or_404(payment_id, detail="Payment không tồn tại")

    async def get_payments_paginated(
        self,
        page: int = 1,
        page_size: int = 20,
        booking_id: UUID | None = None,
        status: PaymentStatus | None = None,
        provider: str | None = None,
    ) -> dict[str, Any]:
        """Lấy danh sách payments có phân trang và filter"""
        skip = (page - 1) * page_size

        filters = {}
        if booking_id is not None:
            filters["booking_id"] = booking_id
        if status is not None:
            filters["status"] = status
        if provider is not None:
            filters["provider"] = provider

        payments = await self.repo.get_multi(skip=skip, limit=page_size, **filters)
        total = await self.repo.get_count(**filters)

        return {
            "items": [
                PaymentRead.model_validate(p, from_attributes=True) for p in payments
            ],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        }

    async def update_payment(
        self, payment_id: UUID, payment_data: PaymentUpdate
    ) -> PaymentRead:
        """Cập nhật payment"""
        payment = await self.get_payment_by_id(payment_id)
        updated_payment = await self.repo.update(payment, payment_data)
        return PaymentRead.model_validate(updated_payment, from_attributes=True)

    async def delete_payment(self, payment_id: UUID) -> None:
        """Xóa payment"""
        await self.repo.delete(payment_id)

    async def search_payments(
        self,
        q: str,
        page: int = 1,
        page_size: int = 20,
        exact_match: bool = False,
        case_sensitive: bool = False,
    ) -> dict[str, Any]:
        """Tìm kiếm payments theo provider, currency_code, hoặc status"""
        skip = (page - 1) * page_size

        payments = await self.repo.search(
            query=q,
            search_columns=["provider", "currency_code"],
            exact_match=exact_match,
            case_sensitive=case_sensitive,
            skip=skip,
            limit=page_size,
        )

        total = await self.repo.count_search(
            query=q,
            search_columns=["provider", "currency_code"],
            exact_match=exact_match,
            case_sensitive=case_sensitive,
        )

        return {
            "items": [
                PaymentRead.model_validate(p, from_attributes=True) for p in payments
            ],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        }
