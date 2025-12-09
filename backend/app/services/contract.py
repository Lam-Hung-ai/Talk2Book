# app/services/contract.py
from typing import Any
from uuid import UUID

from sqlmodel.ext.asyncio.session import AsyncSession

from app.repositories.contract import ContractRepository
from app.schemas.contract import ContractCreate, ContractRead, ContractUpdate


class ContractService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = ContractRepository(db)

    async def create_contract(self, contract_in: ContractCreate) -> ContractRead:
        contract = await self.repo.create(contract_in)
        return ContractRead.model_validate(contract, from_attributes=True)

    async def get_contract(self, contract_id: UUID) -> ContractRead:
        contract = await self.repo.get_or_404(contract_id, detail="Contract không tồn tại")
        return ContractRead.model_validate(contract, from_attributes=True)

    async def get_contracts_paginated(
        self,
        page: int = 1,
        page_size: int = 50,
        provider_id: UUID | None = None,
        currency_code: str | None = None,
    ) -> dict[str, Any]:
        skip = (page - 1) * page_size

        filters: dict[str, Any] = {}
        if provider_id is not None:
            filters["provider_id"] = provider_id
        if currency_code is not None:
            filters["currency_code"] = currency_code

        contracts = await self.repo.get_multi(skip=skip, limit=page_size, **filters)
        total = await self.repo.get_count(**filters)

        return {
            "items": [ContractRead.model_validate(c, from_attributes=True) for c in contracts],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        }

    async def update_contract(self, contract_id: UUID, contract_in: ContractUpdate) -> ContractRead:
        db_contract = await self.repo.get_or_404(contract_id, detail="Contract không tồn tại")
        updated = await self.repo.update(db_contract, contract_in)
        return ContractRead.model_validate(updated, from_attributes=True)

    async def delete_contract(self, contract_id: UUID) -> None:
        await self.repo.delete(contract_id)

