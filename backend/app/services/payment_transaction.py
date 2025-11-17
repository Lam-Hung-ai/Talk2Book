# app/services/payment_transaction.py
from typing import Optional, Sequence
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import HTTPException, status

from app.repositories.payment_transaction import PaymentTransactionRepository
from app.repositories.payment import PaymentRepository
from app.schemas.payment_transaction import PaymentTransactionCreate, PaymentTransactionUpdate
from app.models.transaction_model import PaymentTransaction


class PaymentTransactionService:
    """Service layer cho PaymentTransaction business logic"""
    
    def __init__(self, db: AsyncSession):
        self.repo = PaymentTransactionRepository(db)
        self.payment_repo = PaymentRepository(db)
    
    async def create_transaction(
        self,
        transaction_data: PaymentTransactionCreate
    ) -> PaymentTransaction:
        """Tạo transaction mới"""
        # Validate payment tồn tại
        await self.payment_repo.get_or_404(
            transaction_data.payment_id,
            detail="Payment not found"
        )
        
        return await self.repo.create(transaction_data)
    
    async def get_transaction(self, transaction_id: int) -> PaymentTransaction:
        """Lấy transaction theo ID"""
        return await self.repo.get_or_404(transaction_id, detail="Transaction not found")
    
    async def get_transactions(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> Sequence[PaymentTransaction]:
        """Lấy danh sách tất cả transactions"""
        return await self.repo.get_multi(skip=skip, limit=limit)
    
    async def get_payment_transactions(
        self,
        payment_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> Sequence[PaymentTransaction]:
        """Lấy lịch sử transactions của một payment"""
        # Validate payment tồn tại
        await self.payment_repo.get_or_404(payment_id, detail="Payment not found")
        return await self.repo.get_by_payment_id(payment_id, skip=skip, limit=limit)
    
    async def get_latest_transaction(self, payment_id: int) -> Optional[PaymentTransaction]:
        """Lấy transaction mới nhất của payment"""
        await self.payment_repo.get_or_404(payment_id, detail="Payment not found")
        return await self.repo.get_latest_by_payment(payment_id)
    
    async def get_transactions_by_status(
        self,
        status_filter: str,
        skip: int = 0,
        limit: int = 100
    ) -> Sequence[PaymentTransaction]:
        """Lấy transactions theo trạng thái"""
        return await self.repo.get_by_status(status_filter, skip=skip, limit=limit)
    
    async def get_transactions_by_step(
        self,
        step: str,
        skip: int = 0,
        limit: int = 100
    ) -> Sequence[PaymentTransaction]:
        """Lấy transactions theo step"""
        return await self.repo.get_by_step(step, skip=skip, limit=limit)
    
    async def update_transaction(
        self,
        transaction_id: int,
        transaction_data: PaymentTransactionUpdate
    ) -> PaymentTransaction:
        """Cập nhật transaction"""
        transaction = await self.repo.get_or_404(
            transaction_id,
            detail="Transaction not found"
        )
        return await self.repo.update(transaction, transaction_data)
    
    async def update_transaction_status(
        self,
        transaction_id: int,
        new_status: str
    ) -> PaymentTransaction:
        """Cập nhật trạng thái transaction"""
        valid_statuses = ["pending", "processing", "success", "failed", "cancelled"]
        if new_status not in valid_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
            )
        
        return await self.repo.update_status(transaction_id, new_status)
    
    async def delete_transaction(self, transaction_id: int) -> None:
        """Xóa transaction"""
        await self.repo.delete(transaction_id)
    
    async def search_transactions(
        self,
        query: str,
        search_fields: Optional[list[str]] = None,
        skip: int = 0,
        limit: int = 20
    ) -> Sequence[PaymentTransaction]:
        """Tìm kiếm transactions"""
        if search_fields is None:
            search_fields = ["step", "status"]
        
        return await self.repo.search(
            query=query,
            search_columns=search_fields,
            skip=skip,
            limit=limit
        )
    
    async def get_payment_transaction_stats(self, payment_id: int) -> dict:
        """Lấy thống kê transactions của một payment"""
        await self.payment_repo.get_or_404(payment_id, detail="Payment not found")
        
        total_transactions = await self.repo.count_by_payment_id(payment_id)
        latest_transaction = await self.repo.get_latest_by_payment(payment_id)
        
        # Đếm theo status
        transactions = await self.repo.get_by_payment_id(payment_id)
        status_count = {}
        for txn in transactions:
            status_count[txn.status] = status_count.get(txn.status, 0) + 1
        
        return {
            "payment_id": payment_id,
            "total_transactions": total_transactions,
            "latest_status": latest_transaction.status if latest_transaction else None,
            "latest_step": latest_transaction.step if latest_transaction else None,
            "status_distribution": status_count
        }
