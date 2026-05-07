from datetime import datetime

from pydantic import BaseModel


class FlightRealtimeItem(BaseModel):
    provider: str
    flight_number: str
    airline_name: str | None = None
    departure_airport: str | None = None
    arrival_airport: str | None = None
    status: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    altitude_m: float | None = None
    speed_kmh: float | None = None
    observed_at: datetime | None = None


class FlightRealtimeResponse(BaseModel):
    provider: str
    total: int
    items: list[FlightRealtimeItem]
