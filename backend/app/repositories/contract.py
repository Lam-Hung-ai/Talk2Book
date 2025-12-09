# app/repositories/contract.py
from uuid import UUID

from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.contract import Contract
from app.repositories.base import BaseCRUD
from app.schemas.contract import ContractCreate, ContractUpdate


class ContractRepository(BaseCRUD[Contract, ContractCreate, ContractUpdate]):
    """CRUD repository cho Contract."""

    def __init__(self, db: AsyncSession):
        super().__init__(Contract, db)

    async def get_by_provider(
        self, provider_id: UUID, *, skip: int = 0, limit: int = 100
    ):
        return await self.get_multi(skip=skip, limit=limit, provider_id=provider_id)

