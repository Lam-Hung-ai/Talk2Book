from uuid import UUID

from fastapi import HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.airport import Airport
from app.repositories.route import RouteRepository
from app.schemas.route import RouteCreate, RouteRead, RouteUpdate


class RouteService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = RouteRepository(db)

    async def _ensure_airport(self, iata: str) -> None:
        exists = await self.db.get(Airport, iata.upper())
        if not exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Airport {iata} does not exist",
            )

    async def _normalize_payload(self, payload: RouteCreate | RouteUpdate) -> dict:
        data = payload.model_dump(exclude_unset=True)
        if "origin" in data:
            await self._ensure_airport(data["origin"])
            data["origin"] = data["origin"].upper()
        if "destination" in data:
            await self._ensure_airport(data["destination"])
            data["destination"] = data["destination"].upper()
        if (
            "origin" in data
            and "destination" in data
            and data["origin"] == data["destination"]
        ):
            raise HTTPException(
                status_code=400, detail="Origin and destination must differ"
            )
        return data

    async def create_route(self, payload: RouteCreate) -> RouteRead:
        data = await self._normalize_payload(payload)
        route = await self.repo.create(data)
        return RouteRead.model_validate(route, from_attributes=True)

    async def list_routes(
        self,
        page: int = 1,
        page_size: int = 20,
        q: str | None = None,
        origin: str | None = None,
        destination: str | None = None,
    ) -> dict[str, object]:
        skip = (page - 1) * page_size

        if q:
            items = await self.repo.search(
                query=q,
                search_columns=["origin", "destination"],
                skip=skip,
                limit=page_size,
                exact_match=False,
                case_sensitive=False,
            )
            total = await self.repo.count_search(
                query=q,
                search_columns=["origin", "destination"],
                exact_match=False,
                case_sensitive=False,
            )
        else:
            filters = {}
            if origin:
                filters["origin"] = origin.upper()
            if destination:
                filters["destination"] = destination.upper()

            items = await self.repo.get_multi(skip=skip, limit=page_size, **filters)
            total = await self.repo.get_count(**filters)

        return {
            "items": [RouteRead.model_validate(r, from_attributes=True) for r in items],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        }

    async def get_route(self, route_id: UUID) -> RouteRead:
        route = await self.repo.get_or_404(route_id, detail="Route not found")
        return RouteRead.model_validate(route, from_attributes=True)

    async def update_route(self, route_id: UUID, payload: RouteUpdate) -> RouteRead:
        route = await self.repo.get_or_404(route_id, detail="Route not found")
        data = await self._normalize_payload(payload)

        # Prevent swapping that makes origin == destination
        new_origin = data.get("origin", route.origin)
        new_destination = data.get("destination", route.destination)
        if new_origin == new_destination:
            raise HTTPException(
                status_code=400, detail="Origin and destination must differ"
            )

        updated = await self.repo.update(route, data)
        return RouteRead.model_validate(updated, from_attributes=True)

    async def delete_route(self, route_id: UUID) -> None:
        await self.repo.delete(route_id)
