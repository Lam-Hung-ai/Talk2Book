#!/usr/bin/env python3
"""
Script để import dữ liệu mẫu từ JSON vào database thông qua API
"""
import json
import sys
from pathlib import Path
from typing import Any

import httpx
from rich.console import Console

console = Console()
BASE_URL = "http://127.0.0.1:8000/api/v1"

# Cache để lưu mapping từ name -> id
cache: dict[str, dict[str, str]] = {
    "country": {},
    "city": {},
    "currency": {},
    "provider": {},
    "airport": {},
    "route": {},
    "hotel": {},
}


def make_request(method: str, url: str, data: dict | None = None) -> dict[str, Any]:
    """Gửi HTTP request và trả về response"""
    try:
        if method == "GET":
            response = httpx.get(url, timeout=30.0)
        elif method == "POST":
            response = httpx.post(url, json=data, timeout=30.0)
        elif method == "PUT":
            response = httpx.put(url, json=data, timeout=30.0)
        else:
            raise ValueError(f"Unsupported method: {method}")

        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        console.print(f"[red]Error {e.response.status_code}: {e.response.text}[/red]")
        raise
    except Exception as e:
        console.print(f"[red]Request failed: {e}[/red]")
        raise
def import_currencies(file_path: Path) -> None:
    """Import currencies"""
    console.print("[bold blue]Importing currencies...[/bold blue]")
    with open(file_path, encoding="utf-8") as f:
        currencies = json.load(f)

    for currency in currencies:
        try:
            result = make_request("POST", f"{BASE_URL}/geo/currencies", currency)
            cache["currency"][currency["code"]] = result["code"]
            console.print(f"  ✓ Created currency: {currency['name']} ({currency['code']})")
        except Exception as e:
            console.print(f"  ✗ Failed to create currency {currency['name']}: {e}")

def import_countries(file_path: Path) -> None:
    """Import countries"""
    console.print("[bold blue]Importing countries...[/bold blue]")
    with open(file_path, encoding="utf-8") as f:
        countries = json.load(f)

    for country in countries:
        try:
            result = make_request("POST", f"{BASE_URL}/country/", country)
            cache["country"][country["code"]] = result["code"]
            console.print(f"  ✓ Created country: {country['name']} ({country['code']})")
        except Exception as e:
            console.print(f"  ✗ Failed to create country {country['name']}: {e}")


def import_cities(file_path: Path) -> None:
    """Import cities"""
    console.print("[bold blue]Importing cities...[/bold blue]")
    with open(file_path, encoding="utf-8") as f:
        cities = json.load(f)

    for city in cities:
        try:
            result = make_request("POST", f"{BASE_URL}/city/", city)
            cache["city"][city["name"]] = str(result["id"])
            console.print(f"  ✓ Created city: {city['name']}")
        except Exception as e:
            console.print(f"  ✗ Failed to create city {city['name']}: {e}")


def import_airports(file_path: Path) -> None:
    """Import airports"""
    console.print("[bold blue]Importing airports...[/bold blue]")
    with open(file_path, encoding="utf-8") as f:
        airports = json.load(f)

    for airport in airports:
        city_name = airport.pop("city_name")
        if city_name not in cache["city"]:
            console.print(f"  ✗ City '{city_name}' not found in cache")
            continue

        airport["city_id"] = cache["city"][city_name]
        try:
            result = make_request("POST", f"{BASE_URL}/airport/", airport)
            if airport.get("iata"):
                cache["airport"][airport["iata"]] = str(result.get("iata", ""))
            console.print(f"  ✓ Created airport: {airport['name']} ({airport.get('iata', 'N/A')})")
        except Exception as e:
            console.print(f"  ✗ Failed to create airport {airport['name']}: {e}")


def import_providers(file_path: Path) -> None:
    """Import providers"""
    console.print("[bold blue]Importing providers...[/bold blue]")
    with open(file_path, encoding="utf-8") as f:
        providers = json.load(f)

    for provider in providers:
        try:
            result = make_request("POST", f"{BASE_URL}/provider/", provider)
            cache["provider"][provider["display_name"]] = str(result["id"])
            console.print(f"  ✓ Created provider: {provider['display_name']}")
        except Exception as e:
            console.print(f"  ✗ Failed to create provider {provider['display_name']}: {e}")


def import_hotels(file_path: Path) -> None:
    """Import hotels"""
    console.print("[bold blue]Importing hotels...[/bold blue]")
    with open(file_path, encoding="utf-8") as f:
        hotels = json.load(f)

    for hotel in hotels:
        provider_name = hotel.pop("provider_name")
        city_name = hotel.pop("city_name")

        if provider_name not in cache["provider"]:
            console.print(f"  ✗ Provider '{provider_name}' not found in cache")
            continue
        if city_name not in cache["city"]:
            console.print(f"  ✗ City '{city_name}' not found in cache")
            continue

        hotel["provider_id"] = cache["provider"][provider_name]
        hotel["city_id"] = cache["city"][city_name]

        # Convert time strings to time format (keep as string for JSON)
        # FastAPI will parse it automatically

        try:
            result = make_request("POST", f"{BASE_URL}/hotel/", hotel)
            cache["hotel"][hotel["name"]] = str(result["id"])
            console.print(f"  ✓ Created hotel: {hotel['name']}")
        except Exception as e:
            console.print(f"  ✗ Failed to create hotel {hotel['name']}: {e}")


def import_products(file_path: Path) -> None:
    """Import products"""
    console.print("[bold blue]Importing products...[/bold blue]")
    with open(file_path, encoding="utf-8") as f:
        products = json.load(f)

    for product in products:
        provider_name = product.pop("provider_name")
        city_name = product.pop("city_name", None)

        if provider_name not in cache["provider"]:
            console.print(f"  ✗ Provider '{provider_name}' not found in cache")
            continue

        product["provider_id"] = cache["provider"][provider_name]
        if city_name and city_name in cache["city"]:
            product["city_id"] = cache["city"][city_name]
        else:
            product["city_id"] = None

        try:
            result = make_request("POST", f"{BASE_URL}/product/", product)
            console.print(f"  ✓ Created product: {product['title']}")
        except Exception as e:
            console.print(f"  ✗ Failed to create product {product['title']}: {e}")


def import_routes(file_path: Path) -> None:
    """Import routes"""
    console.print("[bold blue]Importing routes...[/bold blue]")
    with open(file_path, encoding="utf-8") as f:
        routes = json.load(f)

    for route in routes:
        try:
            result = make_request("POST", f"{BASE_URL}/route/", route)
            route_key = f"{route['origin']}-{route['destination']}"
            cache["route"][route_key] = str(result["id"])
            console.print(f"  ✓ Created route: {route['origin']} -> {route['destination']}")
        except Exception as e:
            console.print(f"  ✗ Failed to create route {route['origin']} -> {route['destination']}: {e}")


def import_hotel_rooms(file_path: Path) -> None:
    """Import hotel rooms"""
    console.print("[bold blue]Importing hotel rooms...[/bold blue]")
    with open(file_path, encoding="utf-8") as f:
        rooms = json.load(f)

    for room in rooms:
        hotel_name = room.pop("hotel_name")
        if hotel_name not in cache["hotel"]:
            console.print(f"  ✗ Hotel '{hotel_name}' not found in cache")
            continue

        room["hotel_id"] = cache["hotel"][hotel_name]
        try:
            result = make_request("POST", f"{BASE_URL}/hotel-room/", room)
            console.print(f"  ✓ Created room: {room.get('code', 'N/A')} at {hotel_name}")
        except Exception as e:
            console.print(f"  ✗ Failed to create room at {hotel_name}: {e}")


def import_room_rate_plans(file_path: Path) -> None:
    """Import room rate plans"""
    console.print("[bold blue]Importing room rate plans...[/bold blue]")
    with open(file_path, encoding="utf-8") as f:
        rate_plans = json.load(f)

    for plan in rate_plans:
        hotel_name = plan.pop("hotel_name")
        if hotel_name not in cache["hotel"]:
            console.print(f"  ✗ Hotel '{hotel_name}' not found in cache")
            continue

        plan["hotel_id"] = cache["hotel"][hotel_name]
        try:
            result = make_request("POST", f"{BASE_URL}/room-rate-plan/", plan)
            console.print(f"  ✓ Created rate plan: {plan['name']} at {hotel_name}")
        except Exception as e:
            console.print(f"  ✗ Failed to create rate plan at {hotel_name}: {e}")


def import_flight_schedules(file_path: Path) -> None:
    """Import flight schedules"""
    console.print("[bold blue]Importing flight schedules...[/bold blue]")
    with open(file_path, encoding="utf-8") as f:
        schedules = json.load(f)

    for schedule in schedules:
        provider_name = schedule.pop("provider_name")
        route_origin = schedule.pop("route_origin")
        route_destination = schedule.pop("route_destination")

        if provider_name not in cache["provider"]:
            console.print(f"  ✗ Provider '{provider_name}' not found in cache")
            continue

        route_key = f"{route_origin}-{route_destination}"
        if route_key not in cache["route"]:
            console.print(f"  ✗ Route '{route_key}' not found in cache")
            continue

        schedule["provider_id"] = cache["provider"][provider_name]
        schedule["route_id"] = cache["route"][route_key]

        # Time strings are already in correct format for API

        try:
            result = make_request("POST", f"{BASE_URL}/flight-schedule/", schedule)
            console.print(f"  ✓ Created flight schedule: {schedule['flight_number']}")
        except Exception as e:
            console.print(f"  ✗ Failed to create flight schedule {schedule['flight_number']}: {e}")


def main():
    """Main function"""
    sample_data_dir = Path(__file__).parent / "sample_data"

    if not sample_data_dir.exists():
        console.print(f"[red]Error: Directory {sample_data_dir} does not exist[/red]")
        sys.exit(1)

    console.print("[bold green]Starting data import...[/bold green]\n")

    # Import theo thứ tự dependency
    try:
        # 0. Currencies (no dependency)
        import_currencies(sample_data_dir / "currencies.json")

        # 1. Countries (dependency on currencies)
        import_countries(sample_data_dir / "countries.json")

        # 2. Cities (depends on countries)
        import_cities(sample_data_dir / "cities.json")

        # 3. Providers (no dependency on other entities)
        import_providers(sample_data_dir / "providers.json")

        # 4. Airports (depends on cities)
        import_airports(sample_data_dir / "airports.json")

        # 5. Routes (depends on airports)
        import_routes(sample_data_dir / "routes.json")

        # 6. Hotels (depends on providers and cities)
        import_hotels(sample_data_dir / "hotels.json")

        # 7. Products (depends on providers and cities)
        import_products(sample_data_dir / "products.json")

        # 8. Hotel rooms (depends on hotels)
        import_hotel_rooms(sample_data_dir / "hotel_rooms.json")

        # 9. Room rate plans (depends on hotels)
        import_room_rate_plans(sample_data_dir / "room_rate_plans.json")

        # 10. Flight schedules (depends on providers and routes)
        import_flight_schedules(sample_data_dir / "flight_schedules.json")

        console.print("\n[bold green]✓ Data import completed![/bold green]")
    except KeyboardInterrupt:
        console.print("\n[yellow]Import interrupted by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[red]Import failed: {e}[/red]")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

