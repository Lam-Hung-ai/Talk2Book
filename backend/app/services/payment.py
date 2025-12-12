# app/services/payment.py
from collections.abc import Sequence
from uuid import UUID

from fastapi import HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.payment import Payment
from app.repositories.payment import PaymentRepository
from app.schemas.payment import PaymentCreate, PaymentUpdate


class PaymentService:
    """Service layer cho Payment business logic"""

    def __init__(self, db: AsyncSession):
        self.repo = PaymentRepository(db)

    async def create_payment(self, payment_data: PaymentCreate) -> Payment:
        """Tạo payment mới"""
        # Có thể thêm validation hoặc business logic ở đây
        if payment_data.amount <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payment amount must be greater than 0"
            )

        return await self.repo.create(payment_data)

    async def get_payment(self, payment_id: int) -> Payment:
        """Lấy payment theo ID"""
        return await self.repo.get_or_404(payment_id, detail="Payment not found")

    async def get_payments(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> Sequence[Payment]:
        """Lấy danh sách tất cả payments"""
        return await self.repo.get_multi(skip=skip, limit=limit)

    async def get_user_payments(
        self,
        user_id: UUID,
        status: str | None = None,
        skip: int = 0,
        limit: int = 100
    ) -> Sequence[Payment]:
        """Lấy payments của user, có thể filter theo status"""
        if status:
            return await self.repo.get_user_payments_by_status(
                user_id=user_id,
                status=status,
                skip=skip,
                limit=limit
            )
        return await self.repo.get_by_user_id(user_id=user_id, skip=skip, limit=limit)

    async def update_payment(
        self,
        payment_id: int,
        payment_data: PaymentUpdate
    ) -> Payment:
        """Cập nhật payment"""
        payment = await self.repo.get_or_404(payment_id, detail="Payment not found")
        return await self.repo.update(payment, payment_data)

    async def update_payment_status(
        self,
        payment_id: int,
        new_status: str
    ) -> Payment:
        """Cập nhật trạng thái payment"""
        valid_statuses = ["pending", "completed", "failed", "refunded", "cancelled"]
        if new_status not in valid_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
            )

        return await self.repo.update_status(payment_id, new_status)

    async def delete_payment(self, payment_id: int) -> None:
        """Xóa payment"""
        await self.repo.delete(payment_id)

    async def search_payments(
        self,
        query: str,
        search_fields: list[str] | None = None,
        skip: int = 0,
        limit: int = 20
    ) -> Sequence[Payment]:
        """Tìm kiếm payments"""
        if search_fields is None:
            search_fields = ["gateway", "status", "currency"]

        return await self.repo.search(
            query=query,
            search_columns=search_fields,
            skip=skip,
            limit=limit
        )

    async def get_user_payment_stats(self, user_id: UUID) -> dict:
        """Lấy thống kê payment của user"""
        total_payments = await self.repo.count_by_user_id(user_id)
        total_amount = await self.repo.get_total_amount_by_user(user_id)
        completed_amount = await self.repo.get_total_amount_by_user(user_id, status="completed")

        return {
            "user_id": str(user_id),
            "total_payments": total_payments,
            "total_amount": total_amount,
            "completed_amount": completed_amount,
            "pending_amount": total_amount - completed_amount
        }
