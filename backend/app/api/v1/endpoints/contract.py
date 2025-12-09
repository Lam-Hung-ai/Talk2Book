# app/api/v1/endpoints/contract.py
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.v1.deps import get_async_session
from app.schemas.contract import ContractCreate, ContractRead, ContractUpdate
from app.services.contract import ContractService

router = APIRouter()


def get_contract_service(db: AsyncSession = Depends(get_async_session)) -> ContractService:
    return ContractService(db)


@router.post(
    "/",
    response_model=ContractRead,
    status_code=status.HTTP_201_CREATED,
    summary="Tạo contract mới",
)
async def create_contract(
    contract_in: ContractCreate, service: ContractService = Depends(get_contract_service)
):
    return await service.create_contract(contract_in)


@router.get(
    "/{contract_id}",
    response_model=ContractRead,
    summary="Lấy thông tin contract theo ID",
)
async def get_contract(
    contract_id: UUID, service: ContractService = Depends(get_contract_service)
):
    return await service.get_contract(contract_id)


@router.get(
    "/",
    response_model=dict,
    summary="Danh sách contracts có phân trang",
)
async def list_contracts(
    page: int = Query(1, ge=1, description="Số trang, bắt đầu từ 1"),
    page_size: int = Query(20, ge=1, le=100, description="Số lượng mỗi trang"),
    provider_id: UUID | None = Query(None, description="Lọc theo provider_id"),
    currency_code: str | None = Query(None, description="Lọc theo currency_code"),
    service: ContractService = Depends(get_contract_service),
):
    return await service.get_contracts_paginated(
        page=page,
        page_size=page_size,
        provider_id=provider_id,
        currency_code=currency_code,
    )


@router.put(
    "/{contract_id}",
    response_model=ContractRead,
    summary="Cập nhật contract",
)
async def update_contract(
    contract_id: UUID,
    contract_in: ContractUpdate,
    service: ContractService = Depends(get_contract_service),
):
    return await service.update_contract(contract_id, contract_in)


@router.delete(
    "/{contract_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Xóa contract",
)
async def delete_contract(
    contract_id: UUID, service: ContractService = Depends(get_contract_service)
):
    await service.delete_contract(contract_id)
    return None

