from typing import List, Sequence, Optional
from uuid import UUID
from fastapi import HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from app.models.country import Country
from app.models.city import City
from app.models.currency import Currency
from app.models.airport import Airport

async def create_currency(session: AsyncSession, code: str, name: str) -> Currency:
    if await session.get(Currency, code):
        raise HTTPException(status_code=409, detail="Currency exists")
    item = Currency(code=code.upper(), name=name)
    session.add(item)
    await session.commit()
    await session.refresh(item)
    return item

async def list_currencies(session: AsyncSession, limit: int, offset: int) -> tuple(Sequence[Sequence[Currency]], int):
    items = (await session.exec(select(Currency).offset(offset).limit(limit))).all()
    total = (await session.exec(select(Currency))).all()
    return items, len(total)

async def update_currency(session: AsyncSession, code: str, name: Optional[str]) -> Currency:
    item = session.get(Currency, code)
    if not item:
        raise HTTPException(status_code=404, detail="Currency not found")
    if name is not None:
        item.name = name
    session.add(item)
    session.commit()
    session.refresh(item)
    return item

async def delete_currency(session: AsyncSession, code: str) -> None:
    item = session.get(Currency, code)
    if not item:
        return
    session.delete(item)
    session.commit()

# Countries
async def create_country(session: AsyncSession, code: str, name: str, currency_code: str) -> Country:
    if session.get(Country, code):
        raise HTTPException(status_code=409, detail="Country exists")
    if not session.get(Currency, currency_code):
        raise HTTPException(status_code=400, detail="Invalid currency_code")
    item = Country(code=code.upper(), name=name, currency_code=currency_code.upper())
    session.add(item)
    session.commit()
    session.refresh(item)
    return item

async def list_countries(session: AsyncSession, limit: int, offset: int) -> Tuple[List[Country], int]:
    items = session.exec(select(Country).offset(offset).limit(limit)).all()
    total = session.exec(select(Country)).all()
    return items, len(total)

async def update_country(session: AsyncSession, code: str, name: Optional[str], currency_code: Optional[str]) -> Country:
    item = session.get(Country, code)
    if not item:
        raise HTTPException(status_code=404, detail="Country not found")
    if name is not None:
        item.name = name
    if currency_code is not None:
        if not session.get(Currency, currency_code):
            raise HTTPException(status_code=400, detail="Invalid currency_code")
        item.currency_code = currency_code.upper()
    session.add(item)
    session.commit()
    session.refresh(item)
    return item

async def delete_country(session: AsyncSession, code: str) -> None:
    item = session.get(Country, code)
    if not item:
        return
    session.delete(item)
    session.commit()

# Cities
async def create_city(session: AsyncSession, name: str, country_code: str) -> City:
    if not session.get(Country, country_code):
        raise HTTPException(status_code=400, detail="Invalid country_code")
    existing = session.exec(select(City).where(City.country_code == country_code, City.name == name)).first()
    if existing:
        raise HTTPException(status_code=409, detail="City exists in this country")
    item = City(name=name, country_code=country_code.upper())
    session.add(item)
    session.commit()
    session.refresh(item)
    return item

async def list_cities(session: AsyncSession, limit: int, offset: int, country_code: Optional[str] = None, q: Optional[str] = None):
    query = select(City)
    if country_code:
        query = query.where(City.country_code == country_code.upper())
    if q:
        like = f"%{q}%"
        query = query.where(City.name.ilike(like))
    items = session.exec(query.offset(offset).limit(limit)).all()
    total = session.exec(select(City)).all()
    return items, len(total)

async def delete_city(session: AsyncSession, city_id) -> None:
    item = session.get(City, city_id)
    if not item:
        return
    session.delete(item)
    session.commit()

# Airports
async def create_airport(session: AsyncSession, iata: str, icao: Optional[str], city_id, name: str, timezone: str) -> Airport:
    if not session.get(City, city_id):
        raise HTTPException(status_code=400, detail="Invalid city_id")
    if icao:
        exist_icao = session.exec(select(Airport).where(Airport.icao == icao)).first()
        if exist_icao:
            raise HTTPException(status_code=409, detail="ICAO exists")
    exist_city_name = session.exec(select(Airport).where(Airport.city_id == city_id, Airport.name == name)).first()
    if exist_city_name:
        raise HTTPException(status_code=409, detail="Airport name exists in this city")
    item = Airport(iata=iata.upper(), icao=(icao.upper() if icao else None), city_id=city_id, name=name, timezone=timezone)
    session.add(item)
    session.commit()
    session.refresh(item)
    return item

async def list_airports(session: AsyncSession, limit: int, offset: int, city_id=None, country_code: Optional[str]=None, q: Optional[str]=None):
    from app.models.geo import City, Country  # local import to avoid cycles
    query = select(Airport)
    if city_id:
        query = query.where(Airport.city_id == city_id)
    if q:
        like = f"%{q}%"
        query = query.where(Airport.name.ilike(like) | Airport.iata.ilike(like) | Airport.icao.ilike(like))
    if country_code:
        # join via City
        query = query.join(City, City.id == Airport.city_id).where(City.country_code == country_code.upper())
    items = session.exec(query.offset(offset).limit(limit)).all()
    total = session.exec(select(Airport)).all()
    return items, len(total)

async def update_airport(session: AsyncSession, iata: str, icao: Optional[str]=None, name: Optional[str]=None, timezone: Optional[str]=None) -> Airport:
    item = session.get(Airport, iata.upper())
    if not item:
        raise HTTPException(status_code=404, detail="Airport not found")
    if icao is not None and icao != item.icao:
        exist_icao = session.exec(select(Airport).where(Airport.icao == icao)).first()
        if exist_icao:
            raise HTTPException(status_code=409, detail="ICAO exists")
        item.icao = icao.upper()
    if name is not None:
        # ensure (city_id, name) unique
        dup = session.exec(select(Airport).where(Airport.city_id == item.city_id, Airport.name == name)).first()
        if dup and dup.iata != item.iata:
            raise HTTPException(status_code=409, detail="Airport name exists in this city")
        item.name = name
    if timezone is not None:
        item.timezone = timezone
    session.add(item)
    session.commit()
    session.refresh(item)
    return item

async def delete_airport(session: AsyncSession, iata: str) -> None:
    item = session.get(Airport, iata.upper())
    if not item:
        return
    session.delete(item)
    session.commit()
