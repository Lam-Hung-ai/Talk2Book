from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.v1.deps import get_async_session
from app.schemas.route import (
    RouteCreate,
    RouteRead,
    RouteUpdate,
)
from app.services.route import (
    create_route,
    delete_route_by_id,
    get_route_by_id,
    list_routes,
    update_route_by_id,
)

router = APIRouter()


@router.post(
    "",
    response_model=RouteRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_route_ep(
    payload: RouteCreate,
    session: AsyncSession = Depends(get_async_session),
):
    route = await create_route(session, payload)
    return route


@router.get(
    "/",
    response_model=list[RouteRead],
)
async def list_routes_ep(
    session: AsyncSession = Depends(get_async_session),
    limit: int = Query(10, ge=1, le=200),
    offset: int = Query(0, ge=0),
    q: str | None = Query(None, description="Search by origin/destination IATA"),
    origin: str | None = Query(None, max_length=3),
    destination: str | None = Query(None, max_length=3),
):
    items, _ = await list_routes(
        session=session,
        limit=limit,
        offset=offset,
        q=q,
        origin=origin,
        destination=destination,
    )
    return items


@router.get(
    "/{route_id}",
    response_model=RouteRead,
)
async def get_route_ep(
    route_id: UUID = Path(...),
    session: AsyncSession = Depends(get_async_session),
):
    route = await get_route_by_id(session, route_id)
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
    return route


@router.put(
    "/{route_id}",
    response_model=RouteRead,
)
async def update_route_ep(
    route_id: UUID,
    payload: RouteUpdate,
    session: AsyncSession = Depends(get_async_session),
):
    route = await update_route_by_id(session, route_id, payload)
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
    return route


@router.delete(
    "/{route_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_route_ep(
    route_id: UUID,
    session: AsyncSession = Depends(get_async_session),
):
    ok = await delete_route_by_id(session, route_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Route not found")
    return None
