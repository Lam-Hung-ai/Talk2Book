from fastapi import APIRouter, Depends, Query

from app.schemas.flight_realtime import FlightRealtimeResponse
from app.services.flight_realtime import FlightRealtimeService

router = APIRouter()


def get_flight_realtime_service() -> FlightRealtimeService:
    return FlightRealtimeService()


@router.get("/search", response_model=FlightRealtimeResponse)
async def search_realtime_flights(
    flight_number: str | None = Query(None, description="Ví dụ: VN123"),
    dep_iata: str | None = Query(None, description="Ví dụ: HAN"),
    arr_iata: str | None = Query(None, description="Ví dụ: SGN"),
    limit: int = Query(20, ge=1, le=100),
    service: FlightRealtimeService = Depends(get_flight_realtime_service),
):
    return await service.search_flights(
        flight_number=flight_number,
        dep_iata=dep_iata,
        arr_iata=arr_iata,
        limit=limit,
    )
