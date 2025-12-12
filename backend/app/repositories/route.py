from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.route import Route
from app.repositories.base import BaseCRUD
from app.repositories.searchable import SearchableRepository
from app.schemas.route import RouteCreate, RouteUpdate


class RouteRepository(BaseCRUD[Route, RouteCreate, RouteUpdate], SearchableRepository):
    def __init__(self, db: AsyncSession):
        BaseCRUD.__init__(self, Route, db)
        SearchableRepository.__init__(self, Route, db)

    async def get_by_od(self, origin: str, destination: str) -> Route | None:
        stmt = select(Route).where(Route.origin == origin, Route.destination == destination)
        result = await self.db.exec(stmt)
        return result.first()

