from datetime import UTC, datetime

import aiohttp
from fastapi import HTTPException, status

from app.core.config import settings
from app.schemas.flight_realtime import FlightRealtimeItem, FlightRealtimeResponse


class FlightRealtimeService:
    async def search_flights(
        self,
        *,
        flight_number: str | None = None,
        dep_iata: str | None = None,
        arr_iata: str | None = None,
        limit: int = 20,
    ) -> FlightRealtimeResponse:
        provider = settings.FLIGHT_API_PROVIDER.lower().strip()

        if provider == "aviationstack" and settings.AVIATIONSTACK_API_KEY:
            return await self._search_aviationstack(
                flight_number=flight_number,
                dep_iata=dep_iata,
                arr_iata=arr_iata,
                limit=limit,
            )

        return await self._search_opensky(
            flight_number=flight_number,
            dep_iata=dep_iata,
            arr_iata=arr_iata,
            limit=limit,
        )

    async def _search_aviationstack(
        self,
        *,
        flight_number: str | None,
        dep_iata: str | None,
        arr_iata: str | None,
        limit: int,
    ) -> FlightRealtimeResponse:
        params: dict[str, str | int] = {
            "access_key": settings.AVIATIONSTACK_API_KEY,
            "limit": limit,
        }
        if flight_number:
            params["flight_iata"] = flight_number
        if dep_iata:
            params["dep_iata"] = dep_iata
        if arr_iata:
            params["arr_iata"] = arr_iata

        timeout = aiohttp.ClientTimeout(total=15)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(settings.AVIATIONSTACK_BASE_URL, params=params) as resp:
                if resp.status >= 400:
                    detail = await resp.text()
                    raise HTTPException(
                        status_code=status.HTTP_502_BAD_GATEWAY,
                        detail=f"AviationStack error: {detail}",
                    )
                payload = await resp.json()

        data = payload.get("data", []) or []
        items: list[FlightRealtimeItem] = []
        for row in data[:limit]:
            live = row.get("live") or {}
            flight = row.get("flight") or {}
            airline = row.get("airline") or {}
            departure = row.get("departure") or {}
            arrival = row.get("arrival") or {}

            observed_at = None
            if live.get("updated"):
                try:
                    observed_at = datetime.fromisoformat(
                        str(live["updated"]).replace("Z", "+00:00")
                    )
                except ValueError:
                    observed_at = None

            items.append(
                FlightRealtimeItem(
                    provider="aviationstack",
                    flight_number=flight.get("iata") or flight.get("number") or "UNKNOWN",
                    airline_name=airline.get("name"),
                    departure_airport=departure.get("iata"),
                    arrival_airport=arrival.get("iata"),
                    status=row.get("flight_status"),
                    latitude=live.get("latitude"),
                    longitude=live.get("longitude"),
                    altitude_m=live.get("altitude"),
                    speed_kmh=live.get("speed_horizontal"),
                    observed_at=observed_at,
                )
            )

        return FlightRealtimeResponse(provider="aviationstack", total=len(items), items=items)

    async def _search_opensky(
        self,
        *,
        flight_number: str | None,
        dep_iata: str | None,
        arr_iata: str | None,
        limit: int,
    ) -> FlightRealtimeResponse:
        timeout = aiohttp.ClientTimeout(total=15)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(settings.OPENSKY_BASE_URL) as resp:
                if resp.status >= 400:
                    detail = await resp.text()
                    raise HTTPException(
                        status_code=status.HTTP_502_BAD_GATEWAY,
                        detail=f"OpenSky error: {detail}",
                    )
                payload = await resp.json()

        states = payload.get("states") or []
        items: list[FlightRealtimeItem] = []
        flight_filter = flight_number.strip().upper() if flight_number else None

        for row in states:
            if not isinstance(row, list) or len(row) < 10:
                continue

            callsign = (row[1] or "").strip().upper()
            if flight_filter and flight_filter not in callsign:
                continue

            items.append(
                FlightRealtimeItem(
                    provider="opensky",
                    flight_number=callsign or "UNKNOWN",
                    departure_airport=dep_iata,
                    arrival_airport=arr_iata,
                    status="airborne" if row[8] is False else "on_ground",
                    longitude=row[5],
                    latitude=row[6],
                    altitude_m=row[7],
                    speed_kmh=(row[9] * 3.6) if row[9] is not None else None,
                    observed_at=datetime.fromtimestamp(row[4], tz=UTC) if row[4] else None,
                )
            )
            if len(items) >= limit:
                break

        return FlightRealtimeResponse(provider="opensky", total=len(items), items=items)
