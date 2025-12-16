from collections.abc import Sequence

from fastapi import HTTPException
from sqlmodel import col, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.city import City
from app.models.country import Country
from app.models.currency import Currency


# Currencies
async def create_currency(session: AsyncSession, code: str, name: str) -> Currency:

    if await session.get(Currency, code):
        raise HTTPException(status_code=409, detail="Currency exists")

    item = Currency(code=code.upper(), name=name)
    session.add(item)
    await session.commit()
    await session.refresh(item)
    return item

async def list_currencies(session: AsyncSession, limit: int, offset: int) -> tuple[Sequence[Currency], int]:

    items = (await session.exec(select(Currency).offset(offset).limit(limit))).all()
    total = (await session.exec(select(Currency))).all()
    return items, len(total)

async def update_currency(session: AsyncSession, code: str, name: str | None) -> Currency:

    item = await session.get(Currency, code)
    if not item:
        raise HTTPException(status_code=404, detail="Currency not found")
    if name is not None:
        item.name = name
    session.add(item)
    await session.commit()
    await session.refresh(item)
    return item

async def delete_currency(session: AsyncSession, code: str) -> None:

    item = await session.get(Currency, code)
    if not item:
        return
    await session.delete(item)
    await session.commit()

# Countries
async def create_country(session: AsyncSession, code: str, name: str, currency_code: str) -> Country:

    if await session.get(Country, code):
        raise HTTPException(status_code=409, detail="Country exists")
    if not await session.get(Currency, currency_code):
        raise HTTPException(status_code=400, detail="Invalid currency_code")
    item = Country(code=code.upper(), name=name, currency_code=currency_code.upper())
    session.add(item)
    await session.commit()
    await session.refresh(item)
    return item

async def list_countries(session: AsyncSession, limit: int, offset: int) -> tuple[Sequence[Country], int]:

    items = (await session.exec(select(Country).offset(offset).limit(limit))).all()
    total = (await session.exec(select(Country))).all()
    return items, len(total)

async def update_country(session: AsyncSession, code: str, name: str | None, currency_code: str | None) -> Country:

    item = await session.get(Country, code)
    if not item:
        raise HTTPException(status_code=404, detail="Country not found")
    if name is not None:
        item.name = name
    if currency_code is not None:
        if not await session.get(Currency, currency_code):
            raise HTTPException(status_code=400, detail="Invalid currency_code")
        item.currency_code = currency_code.upper()
    session.add(item)
    await session.commit()
    await session.refresh(item)
    return item

async def delete_country(session: AsyncSession, code: str) -> None:
    item = await session.get(Country, code)
    if not item:
        return
    await session.delete(item)
    await session.commit()

# Cities
async def create_city(session: AsyncSession, name: str, country_code: str) -> City:
    if not await session.get(Country, country_code):
        raise HTTPException(status_code=400, detail="Invalid country_code")
    existing = (await session.exec(select(City).where(City.country_code == country_code, City.name == name))).first()
    if existing:
        raise HTTPException(status_code=409, detail="City exists in this country")
    item = City(name=name, country_code=country_code.upper())
    session.add(item)
    await session.commit()
    await session.refresh(item)
    return item

async def list_cities(session: AsyncSession, limit: int, offset: int, country_code: str | None = None, q: str | None = None):
    query = select(City)
    if country_code:
        query = query.where(City.country_code == country_code.upper())
    if q:
        like = f"%{q}%"
        query = query.where(col(City.name).ilike(like))
    items = (await session.exec(query.offset(offset).limit(limit))).all()
    total = (await session.exec(select(City))).all()
    return items, len(total)

async def delete_city(session: AsyncSession, city_id) -> None:
    item = await session.get(City, city_id)
    if not item:
        return
    await session.delete(item)
    await session.commit()
