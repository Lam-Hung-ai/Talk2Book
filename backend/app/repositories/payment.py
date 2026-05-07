# app/repositories/payment.py
from collections.abc import Sequence
from uuid import UUID

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.enums import PaymentStatus
from app.models.payment import Payment
from app.repositories.base import BaseCRUD
from app.repositories.searchable import SearchableRepository
from app.schemas.payment import PaymentCreate, PaymentUpdate


class PaymentRepository(
    BaseCRUD[Payment, PaymentCreate, PaymentUpdate], SearchableRepository[Payment]
):
    """Repository cho Payment với đầy đủ CRUD và tính năng tìm kiếm"""

    def __init__(self, db: AsyncSession):
        # Khởi tạo cả 2 class cha
        BaseCRUD.__init__(self, Payment, db)
        SearchableRepository.__init__(self, Payment, db)

    async def get_by_booking_id(
        self, booking_id: UUID, skip: int = 0, limit: int = 100
    ) -> Sequence[Payment]:
        """Lấy danh sách payments theo booking_id"""
        return await self.get_multi(skip=skip, limit=limit, booking_id=booking_id)

    async def get_by_status(
        self, status: PaymentStatus, skip: int = 0, limit: int = 100
    ) -> Sequence[Payment]:
        """Lấy payments theo trạng thái"""
        return await self.get_multi(skip=skip, limit=limit, status=status)

    async def get_by_provider(
        self, provider: str, skip: int = 0, limit: int = 100
    ) -> Sequence[Payment]:
        """Lấy payments theo payment gateway"""
        return await self.get_multi(skip=skip, limit=limit, provider=provider)

    async def get_by_idempotency_key(self, idempotency_key: str) -> Payment | None:
        """Lấy payment theo idempotency_key để tránh duplicate"""
        result = await self.db.exec(
            select(Payment).where(Payment.idempotency_key == idempotency_key)
        )
        return result.first()
