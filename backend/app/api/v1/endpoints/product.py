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
    product_in: ProductCreate, service: ProductService = Depends(get_product_service)
):
    """Tạo product mới"""
    return await service.create_product(product_in)


@router.get("/{product_id}", response_model=ProductRead, summary="Lấy thông tin product theo ID")
async def get_product(product_id: UUID, service: ProductService = Depends(get_product_service)):
    """Lấy thông tin product theo ID. Ném 404 nếu không tồn tại"""
    product = await service.get_product_by_id(product_id)
    return ProductRead.model_validate(product, from_attributes=True)


@router.get("/", response_model=dict, summary="Danh sách products có phân trang")
async def get_products(
    page: int = Query(1, ge=1, description="Số trang, bắt đầu từ 1"),
    page_size: int = Query(20, ge=1, le=100, description="Số lượng mỗi trang"),
    provider_id: UUID | None = Query(None, description="Lọc theo provider_id"),
    city_id: UUID | None = Query(None, description="Lọc theo city_id"),
    service: ProductService = Depends(get_product_service),
):
    """Lấy danh sách products với phân trang và filter"""
    return await service.get_products_paginated(
        page=page, page_size=page_size, provider_id=provider_id, city_id=city_id
    )


@router.put("/{product_id}", response_model=ProductRead, summary="Cập nhật thông tin product")
async def update_product(
    product_id: UUID, product_in: ProductUpdate, service: ProductService = Depends(get_product_service)
):
    """Cập nhật product"""
    return await service.update_product(product_id, product_in)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Xóa product")
async def delete_product(product_id: UUID, service: ProductService = Depends(get_product_service)):
    """Xóa product"""
    await service.delete_product(product_id)
    return None


@router.get(
    "/search/mixin", response_model=dict, summary="Tìm kiếm products theo title"
)
async def search_products(
    q: str = Query(..., min_length=1, description="Từ khóa tìm kiếm"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    exact_match: bool = Query(False, description="Tìm chính xác toàn bộ chuỗi"),
    case_sensitive: bool = Query(False, description="Phân biệt hoa/thường"),
    service: ProductService = Depends(get_product_service),
):
    """Tìm kiếm products theo title"""
    return await service.search_products(
        q=q,
        page=page,
        page_size=page_size,
        exact_match=exact_match,
        case_sensitive=case_sensitive,
    )

