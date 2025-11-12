# app/repositories/refund.py
from typing import Optional, Sequence
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.refund_model import Refund
from app.schemas.refund import RefundCreate, RefundUpdate
from app.repositories.base import BaseCRUD
from app.repositories.searchable import SearchableRepository


class RefundRepository(BaseCRUD[Refund, RefundCreate, RefundUpdate], SearchableRepository[Refund]):
    """Repository cho Refund với đầy đủ CRUD và tính năng tìm kiếm"""
    
    def __init__(self, db: AsyncSession):
        # Khởi tạo cả 2 class cha
        BaseCRUD.__init__(self, Refund, db)
        SearchableRepository.__init__(self, Refund, db)
    
    async def get_by_payment_id(self, payment_id: int) -> Sequence[Refund]:
        """Lấy danh sách refunds theo payment_id"""
        statement = select(Refund).where(Refund.payment_id == payment_id)
        result = await self.db.exec(statement)
        return result.all()
    
    async def get_by_status(
        self, 
        status: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> Sequence[Refund]:
        """Lấy refunds theo trạng thái (pending, approved, rejected, completed)"""
        return await self.get_multi(skip=skip, limit=limit, status=status)
    
    async def count_by_status(self, status: str) -> int:
        """Đếm số lượng refunds theo trạng thái"""
        return await self.get_count(status=status)
    
    async def count_by_payment_id(self, payment_id: int) -> int:
        """Đếm số lượng refunds của một payment"""
        return await self.get_count(payment_id=payment_id)
    
    async def get_total_refund_amount_by_payment(self, payment_id: int, status: Optional[str] = None) -> float:
        """Tính tổng số tiền đã hoàn lại cho một payment"""
        from sqlmodel import func
        
        query = select(func.sum(Refund.amount)).where(Refund.payment_id == payment_id)
        
        if status:
            query = query.where(Refund.status == status)
        
        result = await self.db.exec(query)
        total = result.one()
        return total if total else 0.0
    
    async def update_status(self, refund_id: int, new_status: str) -> Refund:
        """Cập nhật trạng thái refund"""
        refund = await self.get_or_404(refund_id, detail="Refund not found")
        refund.status = new_status
        self.db.add(refund)
        await self.db.commit()
        await self.db.refresh(refund)
        return refund
    
    async def get_pending_refunds(self, skip: int = 0, limit: int = 100) -> Sequence[Refund]:
        """Lấy danh sách refunds đang chờ xử lý"""
        return await self.get_by_status("pending", skip=skip, limit=limit)
    
    async def get_approved_refunds(self, skip: int = 0, limit: int = 100) -> Sequence[Refund]:
        """Lấy danh sách refunds đã được duyệt"""
        return await self.get_by_status("approved", skip=skip, limit=limit)
