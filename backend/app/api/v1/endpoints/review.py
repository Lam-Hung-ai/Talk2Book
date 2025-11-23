# app/api/v1/endpoints/review.py
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.v1.deps import get_async_session
from app.schemas.review import (
    ReviewCreate,
    ReviewResponse,
    ReviewUpdate,
)
from app.services.review import ReviewService

router = APIRouter()


def get_review_service(db: AsyncSession = Depends(get_async_session)) -> ReviewService:
    """Dependency để inject ReviewService"""
    return ReviewService(db)


@router.post("/", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_review(
    review_data: ReviewCreate, service: ReviewService = Depends(get_review_service)
):
    """
    Tạo review mới

    - **user_id**: UUID của user đánh giá
    - **service_type**: Loại dịch vụ (flight, hotel, tour, etc.)
    - **service_id**: ID của dịch vụ
    - **rating**: Đánh giá từ 1-5 sao
    - **title**: Tiêu đề đánh giá
    - **content**: Nội dung đánh giá
    """
    return await service.create_review(review_data)


@router.get("/search/", response_model=list[ReviewResponse])
async def search_reviews(
    q: str = Query(..., min_length=1, description="Từ khóa tìm kiếm"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    service: ReviewService = Depends(get_review_service),
):
    """Tìm kiếm reviews theo title, content, hoặc service_type"""
    return await service.search_reviews(query=q, skip=skip, limit=limit)


@router.get("/recent/", response_model=list[ReviewResponse])
async def get_recent_reviews(
    service_type: str | None = Query(None, description="Filter theo loại dịch vụ"),
    limit: int = Query(10, ge=1, le=50),
    service: ReviewService = Depends(get_review_service),
):
    """Lấy reviews mới nhất"""
    return await service.get_recent_reviews(service_type=service_type, limit=limit)


@router.get("/service/{service_type}/{service_id}", response_model=list[ReviewResponse])
async def get_service_reviews(
    service_type: str,
    service_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    service: ReviewService = Depends(get_review_service),
):
    """Lấy tất cả reviews của một dịch vụ"""
    return await service.get_service_reviews(
        service_type=service_type, service_id=service_id, skip=skip, limit=limit
    )


@router.get("/service/{service_type}/{service_id}/stats")
async def get_service_review_stats(
    service_type: str,
    service_id: int,
    service: ReviewService = Depends(get_review_service),
):
    """Lấy thống kê reviews của một dịch vụ (rating trung bình, phân bố sao)"""
    return await service.get_service_review_stats(service_type, service_id)


@router.get("/user/{user_id}", response_model=list[ReviewResponse])
async def get_user_reviews(
    user_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    service: ReviewService = Depends(get_review_service),
):
    """Lấy tất cả reviews của một user"""
    return await service.get_user_reviews(user_id=user_id, skip=skip, limit=limit)


@router.get("/rating/{rating}", response_model=list[ReviewResponse])
async def get_reviews_by_rating(
    rating: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    service: ReviewService = Depends(get_review_service),
):
    """Lấy reviews theo rating (1-5 sao)"""
    return await service.get_reviews_by_rating(rating=rating, skip=skip, limit=limit)


@router.get("/{review_id}", response_model=ReviewResponse)
async def get_review(
    review_id: int, service: ReviewService = Depends(get_review_service)
):
    """Lấy thông tin review theo ID"""
    return await service.get_review(review_id)


@router.get("/")
async def get_reviews(
    skip: int = Query(0, ge=0, description="Số bản ghi bỏ qua"),
    limit: int = Query(100, ge=1, le=100, description="Số bản ghi tối đa"),
    service: ReviewService = Depends(get_review_service),
):
    """Lấy danh sách tất cả reviews với pagination"""
    items = await service.get_reviews(skip=skip, limit=limit)
    total = await service.repo.get_count()

    return {"total": total, "items": items, "skip": skip, "limit": limit}


@router.put("/{review_id}", response_model=ReviewResponse)
async def update_review(
    review_id: int,
    review_data: ReviewUpdate,
    service: ReviewService = Depends(get_review_service),
):
    """Cập nhật review"""
    return await service.update_review(review_id, review_data)


@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_review(
    review_id: int, service: ReviewService = Depends(get_review_service)
):
    """Xóa review"""
    await service.delete_review(review_id)
