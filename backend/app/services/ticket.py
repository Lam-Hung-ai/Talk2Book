from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from fastapi import HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.repositories.booking_item import BookingItemRepository
from app.repositories.ticket import TicketRepository
from app.schemas.ticket import TicketCreate, TicketRead, TicketUpdate


class TicketService:
    def __init__(self, db: AsyncSession):
        self.repo = TicketRepository(db)
        self.booking_item_repo = BookingItemRepository(db)

    async def create_ticket(self, ticket_in: TicketCreate) -> TicketRead:
        if not await self.booking_item_repo.get(ticket_in.item_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Booking item not found"
            )
        ticket_data = ticket_in.model_dump()
        if ticket_data.get("issued_at") is None:
            ticket_data["issued_at"] = datetime.now(UTC)

        ticket = await self.repo.create(ticket_data)
        return TicketRead.model_validate(ticket, from_attributes=True)

    async def get_ticket(self, ticket_id: UUID) -> TicketRead:
        ticket = await self.repo.get_or_404(ticket_id, detail="Ticket not found")
        return TicketRead.model_validate(ticket, from_attributes=True)

    async def list_tickets(
        self,
        page: int = 1,
        page_size: int = 50,
        item_id: UUID | None = None,
    ) -> dict[str, Any]:
        skip = (page - 1) * page_size
        filters: dict[str, Any] = {}
        if item_id is not None:
            filters["item_id"] = item_id

        tickets = await self.repo.get_multi(skip=skip, limit=page_size, **filters)
        total = await self.repo.get_count(**filters)

        return {
            "items": [
                TicketRead.model_validate(t, from_attributes=True) for t in tickets
            ],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        }

    async def update_ticket(
        self, ticket_id: UUID, ticket_in: TicketUpdate
    ) -> TicketRead:
        ticket = await self.repo.get_or_404(ticket_id, detail="Ticket not found")
        updated = await self.repo.update(ticket, ticket_in)
        return TicketRead.model_validate(updated, from_attributes=True)

    async def delete_ticket(self, ticket_id: UUID) -> None:
        await self.repo.delete(ticket_id)

    async def search_tickets(
        self,
        q: str,
        page: int = 1,
        page_size: int = 20,
        exact_match: bool = False,
        case_sensitive: bool = False,
    ) -> dict[str, Any]:
        skip = (page - 1) * page_size

        tickets = await self.repo.search(
            query=q,
            search_columns=["code"],
            exact_match=exact_match,
            case_sensitive=case_sensitive,
            skip=skip,
            limit=page_size,
        )
        total = await self.repo.count_search(
            query=q,
            search_columns=["code"],
            exact_match=exact_match,
            case_sensitive=case_sensitive,
        )

        return {
            "items": [
                TicketRead.model_validate(t, from_attributes=True) for t in tickets
            ],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        }
