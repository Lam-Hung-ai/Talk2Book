from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.v1.deps import get_async_session
from app.schemas.ticket import TicketCreate, TicketRead, TicketUpdate
from app.services.ticket import TicketService

router = APIRouter()


def get_ticket_service(db: AsyncSession = Depends(get_async_session)) -> TicketService:
    return TicketService(db)


@router.post(
    "/",
    response_model=TicketRead,
    status_code=status.HTTP_201_CREATED,
    summary="Tạo ticket",
)
async def create_ticket(
    ticket_in: TicketCreate, service: TicketService = Depends(get_ticket_service)
):
    return await service.create_ticket(ticket_in)


@router.get(
    "/{ticket_id}",
    response_model=TicketRead,
    summary="Lấy ticket theo ID",
)
async def get_ticket(
    ticket_id: UUID, service: TicketService = Depends(get_ticket_service)
):
    return await service.get_ticket(ticket_id)


@router.get("/", response_model=dict, summary="Danh sách ticket")
async def list_tickets(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    item_id: UUID | None = Query(None),
    service: TicketService = Depends(get_ticket_service),
):
    return await service.list_tickets(
        page=page,
        page_size=page_size,
        item_id=item_id,
    )


@router.put(
    "/{ticket_id}",
    response_model=TicketRead,
    summary="Cập nhật ticket",
)
async def update_ticket(
    ticket_id: UUID,
    ticket_in: TicketUpdate,
    service: TicketService = Depends(get_ticket_service),
):
    return await service.update_ticket(ticket_id, ticket_in)


@router.delete(
    "/{ticket_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Xóa ticket",
)
async def delete_ticket(
    ticket_id: UUID, service: TicketService = Depends(get_ticket_service)
):
    await service.delete_ticket(ticket_id)
    return None


@router.get("/search/mixin", response_model=dict, summary="Tìm kiếm ticket")
async def search_tickets(
    q: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    exact_match: bool = Query(False),
    case_sensitive: bool = Query(False),
    service: TicketService = Depends(get_ticket_service),
):
    return await service.search_tickets(
        q=q,
        page=page,
        page_size=page_size,
        exact_match=exact_match,
        case_sensitive=case_sensitive,
    )
