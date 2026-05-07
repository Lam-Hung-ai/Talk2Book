# app/services/airport.py
from typing import Any
from uuid import UUID

from fastapi import HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.airport import Airport
from app.models.city import City
from app.repositories.airport import AirportRepository
from app.schemas.airport import AirportCreate, AirportRead, AirportUpdate


class AirportService:
    def __init__(self, db: AsyncSession):
        self.repo = AirportRepository(db)
        self.db = db

    async def get_airport_by_iata(self, iata: str) -> Airport:
        """Lấy airport theo IATA code, ném 404 nếu không tồn tại"""
        if not iata:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="IATA code không được để trống",
            )
        airport = await self.repo.get_by_iata(iata.upper())
        if not airport:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Airport với IATA code '{iata}' không tồn tại",
            )
        return airport

    async def create_airport(self, airport_in: AirportCreate) -> AirportRead:
        """Tạo airport mới"""
        # Kiểm tra city_id có tồn tại không
        city = await self.db.get(City, airport_in.city_id)
        if not city:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"City với ID '{airport_in.city_id}' không tồn tại",
            )

        # Kiểm tra unique constraint (city_id, name)
        if await self.repo.get_by_city_id_and_name(airport_in.city_id, airport_in.name):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Airport '{airport_in.name}' đã tồn tại trong city này",
            )

        # Kiểm tra IATA unique nếu có
        if airport_in.iata:
            existing = await self.repo.get_by_iata(airport_in.iata.upper())
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"IATA code '{airport_in.iata}' đã tồn tại",
                )

        # Kiểm tra ICAO unique nếu có
        if airport_in.icao:
            existing = await self.repo.get_by_icao(airport_in.icao.upper())
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"ICAO code '{airport_in.icao}' đã tồn tại",
                )

        airport_data = airport_in.model_dump()
        if airport_data.get("iata"):
            airport_data["iata"] = airport_data["iata"].upper()
        if airport_data.get("icao"):
            airport_data["icao"] = airport_data["icao"].upper()

        db_airport = await self.repo.create(airport_data)
        return AirportRead.model_validate(db_airport, from_attributes=True)

    async def get_airports_paginated(
        self,
        page: int = 1,
        page_size: int = 20,
        city_id: UUID | None = None,
    ) -> dict[str, Any]:
        """Lấy danh sách airports có phân trang và filter"""
        skip = (page - 1) * page_size

        if city_id:
            airports = await self.repo.get_by_city_id(
                city_id, skip=skip, limit=page_size
            )
            # Đếm tổng số airports của city
            all_airports = await self.repo.get_by_city_id(city_id, skip=0, limit=10000)
            total = len(all_airports)
        else:
            filters = {}
            airports = await self.repo.get_multi(skip=skip, limit=page_size, **filters)
            total = await self.repo.get_count(**filters)

        return {
            "items": [
                AirportRead.model_validate(a, from_attributes=True) for a in airports
            ],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        }

    async def update_airport(self, iata: str, airport_in: AirportUpdate) -> AirportRead:
        """Cập nhật airport"""
        db_airport = await self.get_airport_by_iata(iata)

        update_data = airport_in.model_dump(exclude_unset=True)

        # Kiểm tra city_id nếu có update
        if "city_id" in update_data:
            city = await self.db.get(City, update_data["city_id"])
            if not city:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"City với ID '{update_data['city_id']}' không tồn tại",
                )

        # Kiểm tra unique constraint nếu có update name hoặc city_id
        if "name" in update_data or "city_id" in update_data:
            final_city_id = update_data.get("city_id", db_airport.city_id)
            final_name = update_data.get("name", db_airport.name)
            existing_airport = await self.repo.get_by_city_id_and_name(
                final_city_id, final_name
            )
            if existing_airport and existing_airport.iata != db_airport.iata:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Airport '{final_name}' đã tồn tại trong city này",
                )

        # Kiểm tra IATA unique nếu có update
        if "iata" in update_data and update_data["iata"]:
            update_data["iata"] = update_data["iata"].upper()
            if update_data["iata"] != db_airport.iata:
                existing = await self.repo.get_by_iata(update_data["iata"])
                if existing:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail=f"IATA code '{update_data['iata']}' đã tồn tại",
                    )

        # Kiểm tra ICAO unique nếu có update
        if "icao" in update_data and update_data["icao"]:
            update_data["icao"] = update_data["icao"].upper()
            existing = await self.repo.get_by_icao(update_data["icao"])
            if existing and existing.iata != db_airport.iata:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"ICAO code '{update_data['icao']}' đã tồn tại",
                )

        updated_airport = await self.repo.update(db_airport, update_data)
        return AirportRead.model_validate(updated_airport, from_attributes=True)

    async def delete_airport(self, iata: str) -> None:
        """Xóa airport"""
        await self.repo.get_or_404(
            iata.upper(), detail=f"Airport với IATA code '{iata}' không tồn tại"
        )
        await self.repo.delete(iata.upper())

    async def search_airports(
        self,
        q: str,
        page: int = 1,
        page_size: int = 20,
        exact_match: bool = False,
        case_sensitive: bool = False,
    ) -> dict[str, Any]:
        """Tìm kiếm airports theo name, iata, hoặc icao"""
        skip = (page - 1) * page_size

        airports = await self.repo.search(
            query=q,
            search_columns=["name", "iata", "icao"],
            exact_match=exact_match,
            case_sensitive=case_sensitive,
            skip=skip,
            limit=page_size,
        )

        total = await self.repo.count_search(
            query=q,
            search_columns=["name", "iata", "icao"],
            exact_match=exact_match,
            case_sensitive=case_sensitive,
        )

        return {
            "items": [
                AirportRead.model_validate(a, from_attributes=True) for a in airports
            ],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        }
