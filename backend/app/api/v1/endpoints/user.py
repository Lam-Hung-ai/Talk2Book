from fastapi import APIRouter, Depends, Query
from app.schemas.user import UserRead, UserCreate
from app.services.user import list_users, create_user
from app.api.v1.deps import get_async_session
from sqlmodel.ext.asyncio.session import AsyncSession
from app.models.user import UserStatus

router = APIRouter()

@router.post("", response_model=UserRead, status_code=201)
async def create_user_ep(payload: UserCreate, session: AsyncSession = Depends(get_async_session)):
    user = await create_user(session, email=payload.email, phone=payload.phone, password=payload.password)
    return user

@router.get("/", response_model=list[UserRead])
async def list_user_ep(
    session: AsyncSession = Depends(get_async_session),
    limit: int = Query(10, ge=1, le=200),
    offset: int = Query(0, ge=0),
    q: str | None = Query(None, description="Search by email/phone"),
    status: UserStatus | None = Query(None)
):
    items, total = await list_users(session, limit=limit, offset=offset, q=q, status=status)
    return items
