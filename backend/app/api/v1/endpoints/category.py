from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.v1.deps import get_async_session
from app.schemas.category import CategoryCreate, CategoryRead, CategoryUpdate
from app.services.category import CategoryService

router = APIRouter()


def get_category_service(
    db: AsyncSession = Depends(get_async_session),
) -> CategoryService:
    return CategoryService(db)


@router.post("/", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_in: CategoryCreate,
    service: CategoryService = Depends(get_category_service),
):
    return await service.create_category(category_in)


@router.get("/", response_model=dict)
async def get_categories(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    group_name: str | None = Query(None),
    is_active: bool | None = Query(None),
    q: str | None = Query(
        None, description="Tìm theo group_name, value hoặc description"
    ),
    service: CategoryService = Depends(get_category_service),
):
    return await service.get_categories_paginated(
        page=page,
        page_size=page_size,
        group_name=group_name,
        is_active=is_active,
        q=q,
    )


@router.get("/{category_id}", response_model=CategoryRead)
async def get_category(
    category_id: UUID,
    service: CategoryService = Depends(get_category_service),
):
    category = await service.get_category_by_id(category_id)
    return CategoryRead.model_validate(category, from_attributes=True)


@router.put("/{category_id}", response_model=CategoryRead)
async def update_category(
    category_id: UUID,
    category_in: CategoryUpdate,
    service: CategoryService = Depends(get_category_service),
):
    return await service.update_category(category_id, category_in)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: UUID,
    service: CategoryService = Depends(get_category_service),
):
    await service.delete_category(category_id)
    return None
