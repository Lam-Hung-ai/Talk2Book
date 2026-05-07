from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.v1.deps import get_async_session
from app.schemas.route import RouteCreate, RouteRead, RouteUpdate
from app.services.route import RouteService

router = APIRouter()


def get_route_service(db: AsyncSession = Depends(get_async_session)) -> RouteService:
    return RouteService(db)


@router.post(
    "/",
    response_model=RouteRead,
    status_code=status.HTTP_201_CREATED,
    summary="Tạo route",
)
async def create_route(
    payload: RouteCreate, service: RouteService = Depends(get_route_service)
):
    return await service.create_route(payload)


@router.get(
    "/",
    response_model=dict,
    summary="Danh sách route",
)
async def list_routes(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    q: str | None = Query(None, description="Tìm theo origin/destination"),
    origin: str | None = Query(None, min_length=3, max_length=3),
    destination: str | None = Query(None, min_length=3, max_length=3),
    service: RouteService = Depends(get_route_service),
):
    return await service.list_routes(
        page=page,
        page_size=page_size,
        q=q,
        origin=origin,
        destination=destination,
    )


@router.get("/{route_id}", response_model=RouteRead, summary="Chi tiết route")
async def get_route(route_id: UUID, service: RouteService = Depends(get_route_service)):
    return await service.get_route(route_id)


@router.put("/{route_id}", response_model=RouteRead, summary="Cập nhật route")
async def update_route(
    route_id: UUID,
    payload: RouteUpdate,
    service: RouteService = Depends(get_route_service),
):
    return await service.update_route(route_id, payload)


@router.delete(
    "/{route_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Xóa route",
)
async def delete_route(
    route_id: UUID, service: RouteService = Depends(get_route_service)
):
    await service.delete_route(route_id)
    return None
