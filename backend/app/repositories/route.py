from collections.abc import Sequence

from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.route import Route
from app.repositories.base import BaseCRUD
from app.repositories.searchable import SearchableRepository
from app.schemas.route import RouteCreate, RouteUpdate


class RouteRepository(BaseCRUD[Route, RouteCreate, RouteUpdate], SearchableRepository):
    def __init__(self, db: AsyncSession):
        BaseCRUD.__init__(self, Route, db)
        SearchableRepository.__init__(self, Route, db)

    async def search_routes(
        self,
        *,
        query: str,
        limit: int,
        offset: int,
    ) -> Sequence[Route]:
        return await self.search(
            query=query,
            search_columns=["origin", "destination"],
            skip=offset,
            limit=limit,
            exact_match=False,
            case_sensitive=False,
        )

