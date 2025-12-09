from collections.abc import Sequence
from uuid import UUID

from fastapi import HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.airport import Airport
from app.models.route import Route
from app.repositories.route import RouteRepository
from app.schemas.route import RouteCreate, RouteRead, RouteUpdate


async def _ensure_airport(session: AsyncSession, iata: str) -> None:
    exists = await session.get(Airport, iata.upper())
    if not exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Airport {iata} does not exist",
        )


async def create_route(session: AsyncSession, payload: RouteCreate) -> RouteRead:
    if payload.origin.upper() == payload.destination.upper():
        raise HTTPException(status_code=400, detail="Origin and destination must differ")

    await _ensure_airport(session, payload.origin)
    await _ensure_airport(session, payload.destination)

    repo = RouteRepository(session)
    data = payload.model_dump()
    data["origin"] = payload.origin.upper()
    data["destination"] = payload.destination.upper()

    route = await repo.create(data)
    return RouteRead.model_validate(route, from_attributes=True)


async def list_routes(
    session: AsyncSession,
    limit: int,
    offset: int,
    q: str | None = None,
    origin: str | None = None,
    destination: str | None = None,
) -> tuple[Sequence[Route], int]:
    repo = RouteRepository(session)

    query = select(Route)
    if origin:
        query = query.where(Route.origin == origin.upper())
    if destination:
        query = query.where(Route.destination == destination.upper())
    if q:
        like = f"%{q}%"
        query = query.where(Route.origin.ilike(like) | Route.destination.ilike(like))

    items = (await session.exec(query.offset(offset).limit(limit))).all()
    total = (await session.exec(select(Route))).all()
    return items, len(total)


async def get_route_by_id(session: AsyncSession, route_id: UUID) -> RouteRead | None:
    repo = RouteRepository(session)
    route = await repo.get(route_id)
    return RouteRead.model_validate(route, from_attributes=True) if route else None


async def update_route_by_id(
    session: AsyncSession, route_id: UUID, payload: RouteUpdate
) -> RouteRead | None:
    repo = RouteRepository(session)
    route = await repo.get(route_id)
    if not route:
        return None

    data = payload.model_dump(exclude_unset=True)
    if "origin" in data:
        await _ensure_airport(session, data["origin"])
        data["origin"] = data["origin"].upper()
    if "destination" in data:
        await _ensure_airport(session, data["destination"])
        data["destination"] = data["destination"].upper()
    if (
        ("origin" in data and data["origin"] == route.destination)
        or ("destination" in data and data["destination"] == route.origin)
    ):
        raise HTTPException(status_code=400, detail="Origin and destination must differ")

    updated = await repo.update(route, data)
    return RouteRead.model_validate(updated, from_attributes=True)


async def delete_route_by_id(session: AsyncSession, route_id: UUID) -> bool:
    repo = RouteRepository(session)
    route = await repo.get(route_id)
    if not route:
        return False
    await repo.delete(route_id)
    return True

