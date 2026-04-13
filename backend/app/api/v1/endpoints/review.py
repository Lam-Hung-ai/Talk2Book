# app/api/v1/endpoints/review.py
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.v1.deps import get_async_session
from app.schemas.review import (
    ReviewCreate,
    ReviewRead,
    ReviewUpdate,
)
from app.services.review import ReviewService

router = APIRouter()


def get_review_service(db: AsyncSession = Depends(get_async_session)) -> ReviewService:
    """Dependency để inject ReviewService"""
    return ReviewService(db)


@router.post("/", response_model=ReviewRead, status_code=status.HTTP_201_CREATED)
async def create_review(
    review_data: ReviewCreate, service: ReviewService = Depends(get_review_service)
):
    """
    Tạo review mới

    - **user_id**: UUID của user đánh giá
    - **target_type**: Loại đối tượng (hotel, product, flight, airport)
    - **target_key**: Key của đối tượng được đánh giá
    - **rating**: Đánh giá từ 1-5 sao
    - **comment**: Bình luận đánh giá
    """
    return await service.create_review(review_data)


@router.get("/", response_model=dict, summary="Danh sách reviews có phân trang")
async def get_reviews(
    page: int = Query(1, ge=1, description="Số trang, bắt đầu từ 1"),
    page_size: int = Query(20, ge=1, le=100, description="Số lượng mỗi trang"),
    target_type: str | None = Query(None, description="Lọc theo loại đối tượng"),
    user_id: str | None = Query(None, description="Lọc theo user_id"),
    service: ReviewService = Depends(get_review_service),
):
    """Lấy danh sách reviews với phân trang và filter"""
    return await service.get_reviews_paginated(
        page=page, page_size=page_size, target_type=target_type, user_id=user_id
    )


@router.get(
    "/{review_id}", response_model=ReviewRead, summary="Lấy thông tin review theo ID"
)
async def get_review(
    review_id: UUID, service: ReviewService = Depends(get_review_service)
):
    """Lấy thông tin review theo ID. Ném 404 nếu không tồn tại"""
    review = await service.get_review(review_id)
    return ReviewRead.model_validate(review, from_attributes=True)


@router.put(
    "/{review_id}", response_model=ReviewRead, summary="Cập nhật thông tin review"
)
async def update_review(
    review_id: UUID,
    review_data: ReviewUpdate,
    service: ReviewService = Depends(get_review_service),
):
    """Cập nhật review"""
    updated_review = await service.update_review(review_id, review_data)
    return ReviewRead.model_validate(updated_review, from_attributes=True)


@router.delete(
    "/{review_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Xóa review"
)
async def delete_review(
    review_id: UUID, service: ReviewService = Depends(get_review_service)
):
    """Xóa review"""
    await service.delete_review(review_id)
    return None


@router.get("/search/mixin", response_model=dict, summary="Tìm kiếm reviews")
async def search_reviews(
    q: str = Query(..., min_length=1, description="Từ khóa tìm kiếm"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    exact_match: bool = Query(False, description="Tìm chính xác toàn bộ chuỗi"),
    case_sensitive: bool = Query(False, description="Phân biệt hoa/thường"),
    service: ReviewService = Depends(get_review_service),
):
    """Tìm kiếm reviews theo comment hoặc target_key"""
    skip = (page - 1) * page_size
    reviews = await service.search_reviews(query=q, skip=skip, limit=page_size)
    total = await service.repo.count_search(
        query=q,
        search_columns=["comment", "target_key"],
        exact_match=exact_match,
        case_sensitive=case_sensitive,
    )
    return {
        "items": [ReviewRead.model_validate(r, from_attributes=True) for r in reviews],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size,
    }


@router.get("/target/{target_type}/{target_key}", response_model=list[ReviewRead])
async def get_target_reviews(
    target_type: str,
    target_key: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    service: ReviewService = Depends(get_review_service),
):
    """Lấy tất cả reviews của một đối tượng"""
    return await service.get_target_reviews(
        target_type=target_type, target_key=target_key, skip=skip, limit=limit
    )


@router.get("/target/{target_type}/{target_key}/stats")
async def get_target_review_stats(
    target_type: str,
    target_key: str,
    service: ReviewService = Depends(get_review_service),
):
    """Lấy thống kê reviews của một đối tượng (rating trung bình, phân bố sao)"""
    return await service.get_target_review_stats(target_type, target_key)


@router.get("/user/{user_id}", response_model=list[ReviewRead])
async def get_user_reviews(
    user_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    service: ReviewService = Depends(get_review_service),
):
    """Lấy tất cả reviews của một user"""
    return await service.get_user_reviews(user_id=user_id, skip=skip, limit=limit)


@router.get("/rating/{rating}", response_model=list[ReviewRead])
async def get_reviews_by_rating(
    rating: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    service: ReviewService = Depends(get_review_service),
):
    """Lấy reviews theo rating (1-5 sao)"""
    return await service.get_reviews_by_rating(rating=rating, skip=skip, limit=limit)


@router.get("/recent/list", response_model=list[ReviewRead])
async def get_recent_reviews(
    target_type: str | None = Query(None, description="Filter theo loại đối tượng"),
    limit: int = Query(10, ge=1, le=50),
    service: ReviewService = Depends(get_review_service),
):
    """Lấy reviews mới nhất"""
    return await service.get_recent_reviews(target_type=target_type, limit=limit)
