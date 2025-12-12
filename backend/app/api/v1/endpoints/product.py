# app/api/v1/endpoints/product.py
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.v1.deps import get_async_session
from app.schemas.product import ProductCreate, ProductRead, ProductUpdate
from app.services.product import ProductService

router = APIRouter()


def get_product_service(db: AsyncSession = Depends(get_async_session)) -> ProductService:
    return ProductService(db)


@router.post(
    "/",
    response_model=ProductRead,
    status_code=status.HTTP_201_CREATED,
    summary="Tạo product mới",
)
async def create_product(
    payload: ProductCreate, service: ProductService = Depends(get_product_service)
):
    return await service.create_product(payload)


@router.get("/", response_model=dict, summary="Danh sách products có phân trang")
async def list_products(
    page: int = Query(1, ge=1, description="Số trang, bắt đầu từ 1"),
    page_size: int = Query(20, ge=1, le=100, description="Số lượng mỗi trang"),
    q: str | None = Query(None, description="Tìm kiếm theo title"),
    provider_id: UUID | None = Query(None, description="Lọc theo provider"),
    city_id: UUID | None = Query(None, description="Lọc theo city"),
    type: str | None = Query(None, description="Lọc theo type (activity/transport)"),
    service: ProductService = Depends(get_product_service),
):
    return await service.list_products(
        page=page,
        page_size=page_size,
        q=q,
        provider_id=provider_id,
        city_id=city_id,
        type=type,
    )


@router.get("/{product_id}", response_model=ProductRead, summary="Chi tiết product")
async def get_product(
    product_id: UUID, service: ProductService = Depends(get_product_service)
):
    return await service.get_product(product_id)


@router.put("/{product_id}", response_model=ProductRead, summary="Cập nhật product")
async def update_product(
    product_id: UUID,
    payload: ProductUpdate,
    service: ProductService = Depends(get_product_service),
):
    return await service.update_product(product_id, payload)


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Xóa product",
)
async def delete_product(
    product_id: UUID, service: ProductService = Depends(get_product_service)
):
    await service.delete_product(product_id)
    return None

