from fastapi import APIRouter, Depends, Query, Path, HTTPException, status
from typing import Optional
from uuid import UUID
from sqlmodel.ext.asyncio.session import AsyncSession
from app.api.v1.deps import get_async_session

from app.schemas.room_rate_plan import (
    RoomRatePlanRead,
    RoomRatePlanCreate,
    RoomRatePlanUpdate,
)
from app.services.room_rate_plan import (
    create_room_rate_plan,
    list_room_rate_plans,
    get_room_rate_plan_by_id,
    update_room_rate_plan_by_id,
    delete_room_rate_plan_by_id,
)

router = APIRouter()

@router.post("", response_model=RoomRatePlanRead, status_code=status.HTTP_201_CREATED)
async def create_room_rate_plan_ep(
    payload: RoomRatePlanCreate,
    session: AsyncSession = Depends(get_async_session),
):
    plan = await create_room_rate_plan(session, payload)
    return plan


@router.get("/", response_model=list[RoomRatePlanRead])
async def list_room_rate_plans_ep(
    session: AsyncSession = Depends(get_async_session),
    limit: int = Query(10, ge=1, le=200),
    offset: int = Query(0, ge=0),
    q: Optional[str] = Query(None, description="Search by name or meal plan"),
    hotel_id: Optional[UUID] = Query(None),
    currency_code: Optional[str] = Query(None, max_length=3),
):
    items, _ = await list_room_rate_plans(
        session=session,
        limit=limit,
        offset=offset,
        q=q,
        hotel_id=hotel_id,
        currency_code=currency_code,
    )
    return items


@router.get("/{rate_plan_id}", response_model=RoomRatePlanRead)
async def get_room_rate_plan_ep(
    rate_plan_id: UUID = Path(...),
    session: AsyncSession = Depends(get_async_session),
):
    plan = await get_room_rate_plan_by_id(session, rate_plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Rate plan not found")
    return plan


@router.put("/{rate_plan_id}", response_model=RoomRatePlanRead)
async def update_room_rate_plan_ep(
    rate_plan_id: UUID,
    payload: RoomRatePlanUpdate,
    session: AsyncSession = Depends(get_async_session),
):
    plan = await update_room_rate_plan_by_id(session, rate_plan_id, payload)
    if not plan:
        raise HTTPException(status_code=404, detail="Rate plan not found")
    return plan


@router.delete("/{rate_plan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_room_rate_plan_ep(
    rate_plan_id: UUID,
    session: AsyncSession = Depends(get_async_session),
):
    ok = await delete_room_rate_plan_by_id(session, rate_plan_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Rate plan not found")
    return None
