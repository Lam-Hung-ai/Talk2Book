# app/repositories/payment_transaction.py
from typing import Optional, Sequence
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.transaction_model import PaymentTransaction
from app.schemas.payment_transaction import PaymentTransactionCreate, PaymentTransactionUpdate
from app.repositories.base import BaseCRUD
from app.repositories.searchable import SearchableRepository


class PaymentTransactionRepository(
    BaseCRUD[PaymentTransaction, PaymentTransactionCreate, PaymentTransactionUpdate],
    SearchableRepository[PaymentTransaction]
):
    """Repository cho PaymentTransaction với đầy đủ CRUD và tính năng tìm kiếm"""
    
    def __init__(self, db: AsyncSession):
        BaseCRUD.__init__(self, PaymentTransaction, db)
        SearchableRepository.__init__(self, PaymentTransaction, db)
    
    async def get_by_payment_id(
        self,
        payment_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> Sequence[PaymentTransaction]:
        """Lấy danh sách transactions của một payment (theo thứ tự thời gian)"""
        from sqlmodel import col
        
        statement = select(PaymentTransaction).where(
            PaymentTransaction.payment_id == payment_id
        ).order_by(col(PaymentTransaction.created_at)).offset(skip).limit(limit)
        result = await self.db.exec(statement)
        return result.all()
    
    async def get_by_status(
        self,
        status: str,
        skip: int = 0,
        limit: int = 100
    ) -> Sequence[PaymentTransaction]:
        """Lấy transactions theo trạng thái"""
        return await self.get_multi(skip=skip, limit=limit, status=status)
    
    async def get_by_step(
        self,
        step: str,
        skip: int = 0,
        limit: int = 100
    ) -> Sequence[PaymentTransaction]:
        """Lấy transactions theo step"""
        return await self.get_multi(skip=skip, limit=limit, step=step)
    
    async def get_latest_by_payment(self, payment_id: int) -> Optional[PaymentTransaction]:
        """Lấy transaction mới nhất của một payment"""
        from sqlmodel import desc
        
        statement = select(PaymentTransaction).where(
            PaymentTransaction.payment_id == payment_id
        ).order_by(desc(PaymentTransaction.created_at)).limit(1)
        result = await self.db.exec(statement)
        return result.first()
    
    async def count_by_payment_id(self, payment_id: int) -> int:
        """Đếm số lượng transactions của một payment"""
        return await self.get_count(payment_id=payment_id)
    
    async def count_by_status(self, status: str) -> int:
        """Đếm số lượng transactions theo trạng thái"""
        return await self.get_count(status=status)
    
    async def get_failed_transactions(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> Sequence[PaymentTransaction]:
        """Lấy danh sách transactions failed"""
        return await self.get_by_status("failed", skip=skip, limit=limit)
    
    async def get_success_transactions(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> Sequence[PaymentTransaction]:
        """Lấy danh sách transactions success"""
        return await self.get_by_status("success", skip=skip, limit=limit)
    
    async def update_status(
        self,
        transaction_id: int,
        new_status: str
    ) -> PaymentTransaction:
        """Cập nhật trạng thái transaction"""
        transaction = await self.get_or_404(transaction_id, detail="Transaction not found")
        transaction.status = new_status
        self.db.add(transaction)
        await self.db.commit()
        await self.db.refresh(transaction)
        return transaction
