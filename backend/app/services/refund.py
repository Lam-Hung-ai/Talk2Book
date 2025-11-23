# app/services/refund.py
from collections.abc import Sequence

from fastapi import HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.refund_model import Refund
from app.repositories.payment import PaymentRepository
from app.repositories.refund import RefundRepository
from app.schemas.refund import RefundCreate, RefundUpdate


class RefundService:
    """Service layer cho Refund business logic"""

    def __init__(self, db: AsyncSession):
        self.repo = RefundRepository(db)
        self.payment_repo = PaymentRepository(db)

    async def create_refund(self, refund_data: RefundCreate) -> Refund:
        """Tạo refund mới"""
        # Validate payment tồn tại
        payment = await self.payment_repo.get_or_404(
            refund_data.payment_id,
            detail="Payment not found"
        )

        # Validate amount
        if refund_data.amount <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Refund amount must be greater than 0"
            )

        # Validate amount không vượt quá payment amount
        if refund_data.amount > payment.amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Refund amount cannot exceed payment amount ({payment.amount})"
            )

        # Kiểm tra tổng refund không vượt quá payment amount
        total_refunded = await self.repo.get_total_refund_amount_by_payment(
            payment_id=refund_data.payment_id,
            status="completed"
        )

        if total_refunded + refund_data.amount > payment.amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Total refund amount would exceed payment amount. Already refunded: {total_refunded}"
            )

        return await self.repo.create(refund_data)

    async def get_refund(self, refund_id: int) -> Refund:
        """Lấy refund theo ID"""
        return await self.repo.get_or_404(refund_id, detail="Refund not found")

    async def get_refunds(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> Sequence[Refund]:
        """Lấy danh sách tất cả refunds"""
        return await self.repo.get_multi(skip=skip, limit=limit)

    async def get_refunds_by_payment(
        self,
        payment_id: int
    ) -> Sequence[Refund]:
        """Lấy danh sách refunds của một payment"""
        # Validate payment tồn tại
        await self.payment_repo.get_or_404(payment_id, detail="Payment not found")
        return await self.repo.get_by_payment_id(payment_id)

    async def get_refunds_by_status(
        self,
        status: str,
        skip: int = 0,
        limit: int = 100
    ) -> Sequence[Refund]:
        """Lấy refunds theo trạng thái"""
        return await self.repo.get_by_status(status, skip=skip, limit=limit)

    async def update_refund(
        self,
        refund_id: int,
        refund_data: RefundUpdate
    ) -> Refund:
        """Cập nhật refund"""
        refund = await self.repo.get_or_404(refund_id, detail="Refund not found")

        # Nếu update amount, validate lại
        if refund_data.amount is not None:
            payment = await self.payment_repo.get_or_404(refund.payment_id)
            if refund_data.amount > payment.amount:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Refund amount cannot exceed payment amount ({payment.amount})"
                )

        return await self.repo.update(refund, refund_data)

    async def update_refund_status(
        self,
        refund_id: int,
        new_status: str
    ) -> Refund:
        """Cập nhật trạng thái refund"""
        valid_statuses = ["pending", "approved", "rejected", "completed", "cancelled"]
        if new_status not in valid_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
            )

        return await self.repo.update_status(refund_id, new_status)

    async def approve_refund(self, refund_id: int) -> Refund:
        """Duyệt refund"""
        return await self.update_refund_status(refund_id, "approved")

    async def reject_refund(self, refund_id: int) -> Refund:
        """Từ chối refund"""
        return await self.update_refund_status(refund_id, "rejected")

    async def complete_refund(self, refund_id: int) -> Refund:
        """Hoàn thành refund"""
        refund = await self.repo.get_or_404(refund_id, detail="Refund not found")

        if refund.status != "approved":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only approved refunds can be completed"
            )

        return await self.update_refund_status(refund_id, "completed")

    async def delete_refund(self, refund_id: int) -> None:
        """Xóa refund (chỉ cho phép nếu status là pending)"""
        refund = await self.repo.get_or_404(refund_id, detail="Refund not found")

        if refund.status not in ["pending", "rejected"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Can only delete pending or rejected refunds"
            )

        await self.repo.delete(refund_id)

    async def search_refunds(
        self,
        query: str,
        search_fields: list[str] | None = None,
        skip: int = 0,
        limit: int = 20
    ) -> Sequence[Refund]:
        """Tìm kiếm refunds"""
        if search_fields is None:
            search_fields = ["reason", "status"]

        return await self.repo.search(
            query=query,
            search_columns=search_fields,
            skip=skip,
            limit=limit
        )

    async def get_payment_refund_stats(self, payment_id: int) -> dict:
        """Lấy thống kê refund của một payment"""
        await self.payment_repo.get_or_404(payment_id, detail="Payment not found")

        total_refunds = await self.repo.count_by_payment_id(payment_id)
        total_amount = await self.repo.get_total_refund_amount_by_payment(payment_id)
        completed_amount = await self.repo.get_total_refund_amount_by_payment(
            payment_id,
            status="completed"
        )
        pending_amount = await self.repo.get_total_refund_amount_by_payment(
            payment_id,
            status="pending"
        )

        return {
            "payment_id": payment_id,
            "total_refunds": total_refunds,
            "total_refund_amount": total_amount,
            "completed_amount": completed_amount,
            "pending_amount": pending_amount
        }
