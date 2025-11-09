from typing import Optional, Sequence
from fastapi import HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

from app.models.airport import Airport
from app.models.city import City

# Airports
async def create_airport(session: AsyncSession, iata: str, icao: Optional[str], city_id, name: str, timezone: str) -> Airport:
    if not await session.get(City, city_id):
        raise HTTPException(status_code=400, detail="Invalid city_id")
    if icao:
        exist_icao = (await session.exec(select(Airport).where(Airport.icao == icao.upper()))).first()
        if exist_icao:
            raise HTTPException(status_code=409, detail="ICAO exists")
    exist_city_name = (await session.exec(select(Airport).where(Airport.city_id == city_id, Airport.name == name)) ).first()
    if exist_city_name:
        raise HTTPException(status_code=409, detail="Airport name exists in this city")
    item = Airport(iata=iata.upper(), icao=(icao.upper() if icao else None), city_id=city_id, name=name, timezone=timezone)
    session.add(item)
    await session.commit()
    await session.refresh(item)
    return item

async def list_airports(session: AsyncSession, limit: int, offset: int, city_id=None, country_code: Optional[str]=None, q: Optional[str]=None) -> tuple[Sequence[Airport], int]:
    query = select(Airport)
    if city_id:
        query = query.where(Airport.city_id == city_id)
    if q:
        like = f"%{q}%"
        query = query.where(Airport.name.ilike(like) | Airport.iata.ilike(like) | Airport.icao.ilike(like))
    if country_code:
        # join via City
        query = query.join(City, City.id == Airport.city_id).where(City.country_code == country_code.upper())
    items = (await session.exec(query.offset(offset).limit(limit))).all()
    total = (await session.exec(select(Airport))).all()
    return items, len(total)

async def update_airport(session: AsyncSession, iata: str, icao: Optional[str]=None, name: Optional[str]=None, timezone: Optional[str]=None) -> Airport:
    item = await session.get(Airport, iata.upper())
    if not item:
        raise HTTPException(status_code=404, detail="Airport not found")
    if icao is not None and icao != item.icao:
        exist_icao = (await session.exec(select(Airport).where(Airport.icao == icao.upper()))).first()
        if exist_icao:
            raise HTTPException(status_code=409, detail="ICAO exists")
        item.icao = icao.upper()
    if name is not None:
        # ensure (city_id, name) unique
        dup = (await session.exec(select(Airport).where(Airport.city_id == item.city_id, Airport.name == name))).first()
        if dup and dup.iata != item.iata:
            raise HTTPException(status_code=409, detail="Airport name exists in this city")
        item.name = name
    if timezone is not None:
        item.timezone = timezone
    session.add(item)
    await session.commit()
    await session.refresh(item)
    return item

async def delete_airport(session: AsyncSession, iata: str) -> None:
    item = await session.get(Airport, iata.upper())
    if not item:
        return
    await session.delete(item)
    await session.commit()
