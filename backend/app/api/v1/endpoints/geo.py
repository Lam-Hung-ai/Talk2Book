from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.v1.deps import get_async_session
from app.schemas.geo import (
    CityCreate,
    CityRead,
    CountryCreate,
    CountryRead,
    CurrencyCreate,
    CurrencyRead,
)
from app.services.geo import (
    create_city,
    create_country,
    create_currency,
    delete_city,
    delete_country,
    delete_currency,
    list_cities,
    list_countries,
    list_currencies,
    update_country,
    update_currency,
)

router = APIRouter(prefix="/geo", tags=["Geo"])


# Currencies
@router.post("/currencies", response_model=CurrencyRead, status_code=201)
async def create_currency_ep(
    payload: CurrencyCreate, session: AsyncSession = Depends(get_async_session)
):
    return await create_currency(session, code=payload.code, name=payload.name)


@router.get("/currencies", response_model=list[CurrencyRead])
async def list_currencies_ep(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_async_session),
):
    items, total = await list_currencies(session, limit=limit, offset=offset)
    return items


@router.patch("/currencies/{code}", response_model=CurrencyRead)
async def update_currency_ep(
    code: str,
    payload: CurrencyCreate,
    session: AsyncSession = Depends(get_async_session),
):
    return await update_currency(session, code=code, name=payload.name)


@router.delete("/currencies/{code}", status_code=204)
async def delete_currency_ep(
    code: str, session: AsyncSession = Depends(get_async_session)
):
    await delete_currency(session, code)


# Countries
@router.post("/countries", response_model=CountryRead, status_code=201)
async def create_country_ep(
    payload: CountryCreate, session: AsyncSession = Depends(get_async_session)
):
    return await create_country(
        session,
        code=payload.code,
        name=payload.name,
        currency_code=payload.currency_code,
    )


@router.get("/countries", response_model=list[CountryRead])
async def list_countries_ep(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_async_session),
):
    items, total = await list_countries(session, limit=limit, offset=offset)
    return items


@router.patch("/countries/{code}", response_model=CountryRead)
async def update_country_ep(
    code: str,
    payload: CountryCreate,
    session: AsyncSession = Depends(get_async_session),
):
    return await update_country(
        session, code=code, name=payload.name, currency_code=payload.currency_code
    )


@router.delete("/countries/{code}", status_code=204)
async def delete_country_ep(
    code: str, session: AsyncSession = Depends(get_async_session)
):
    await delete_country(session, code)


# City
@router.post("/cities", response_model=CityRead, status_code=201)
async def create_city_ep(
    payload: CityCreate, session: AsyncSession = Depends(get_async_session)
):
    return await create_city(
        session, name=payload.name, country_code=payload.country_code
    )


@router.get("/cities", response_model=list[CityRead])
async def list_cities_ep(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    country_code: Optional[str] = None,
    q: Optional[str] = None,
    session: AsyncSession = Depends(get_async_session),
):
    items, total = await list_cities(
        session, limit=limit, offset=offset, country_code=country_code, q=q
    )
    return items


@router.delete("/cities/{city_id}", status_code=204)
async def delete_city_ep(
    city_id: UUID, session: AsyncSession = Depends(get_async_session)
):
    await delete_city(session, city_id)
