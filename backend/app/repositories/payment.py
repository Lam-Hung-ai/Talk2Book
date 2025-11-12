# app/repositories/payment.py
from typing import Optional, Sequence
from uuid import UUID
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.payment_model import Payment
from app.schemas.payment import PaymentCreate, PaymentUpdate
from app.repositories.base import BaseCRUD
from app.repositories.searchable import SearchableRepository


class PaymentRepository(BaseCRUD[Payment, PaymentCreate, PaymentUpdate], SearchableRepository[Payment]):
    """Repository cho Payment với đầy đủ CRUD và tính năng tìm kiếm"""
    
    def __init__(self, db: AsyncSession):
        # Khởi tạo cả 2 class cha
        BaseCRUD.__init__(self, Payment, db)
        SearchableRepository.__init__(self, Payment, db)
    
    async def get_by_user_id(
        self, 
        user_id: UUID, 
        skip: int = 0, 
        limit: int = 100
    ) -> Sequence[Payment]:
        """Lấy danh sách payments của một user"""
        return await self.get_multi(skip=skip, limit=limit, user_id=user_id)
    
    async def get_by_booking_id(self, booking_id: int) -> Sequence[Payment]:
        """Lấy danh sách payments theo booking_id"""
        statement = select(Payment).where(Payment.booking_id == booking_id)
        result = await self.db.exec(statement)
        return result.all()
    
    async def get_by_status(
        self, 
        status: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> Sequence[Payment]:
        """Lấy payments theo trạng thái (pending, completed, failed, refunded)"""
        return await self.get_multi(skip=skip, limit=limit, status=status)
    
    async def get_by_gateway(
        self, 
        gateway: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> Sequence[Payment]:
        """Lấy payments theo payment gateway"""
        return await self.get_multi(skip=skip, limit=limit, gateway=gateway)
    
    async def get_user_payments_by_status(
        self, 
        user_id: UUID, 
        status: str,
        skip: int = 0, 
        limit: int = 100
    ) -> Sequence[Payment]:
        """Lấy payments của user theo trạng thái cụ thể"""
        return await self.get_multi(
            skip=skip, 
            limit=limit, 
            user_id=user_id, 
            status=status
        )
    
    async def count_by_user_id(self, user_id: UUID) -> int:
        """Đếm số lượng payments của một user"""
        return await self.get_count(user_id=user_id)
    
    async def count_by_status(self, status: str) -> int:
        """Đếm số lượng payments theo trạng thái"""
        return await self.get_count(status=status)
    
    async def get_total_amount_by_user(self, user_id: UUID, status: Optional[str] = None) -> float:
        """Tính tổng số tiền đã thanh toán của user"""
        from sqlmodel import func
        
        query = select(func.sum(Payment.amount)).where(Payment.user_id == user_id)
        
        if status:
            query = query.where(Payment.status == status)
        
        result = await self.db.exec(query)
        total = result.one()
        return total if total else 0.0
    
    async def update_status(self, payment_id: int, new_status: str) -> Payment:
        """Cập nhật trạng thái payment"""
        payment = await self.get_or_404(payment_id, detail="Payment not found")
        payment.status = new_status
        self.db.add(payment)
        await self.db.commit()
        await self.db.refresh(payment)
        return payment
