#!/usr/bin/env python3
"""
Script để import hotel rooms và rate plans (chạy sau khi đã import hotels)
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
    "hotel": {},
}


def make_request(method: str, url: str, data: dict | None = None) -> dict[str, Any]:
    """Gửi HTTP request và trả về response"""
    try:
        if method == "GET":
            response = httpx.get(url, timeout=30.0)
        elif method == "POST":
            response = httpx.post(url, json=data, timeout=30.0)
        else:
            raise ValueError(f"Unsupported method: {method}")

        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 409:  # Conflict - already exists
            console.print("  ⚠ Already exists, skipping...")
            return {}
        console.print(f"[red]Error {e.response.status_code}: {e.response.text}[/red]")
        raise
    except Exception as e:
        console.print(f"[red]Request failed: {e}[/red]")
        raise


def load_hotel_cache() -> None:
    """Load hotel cache từ API"""
    console.print("[bold blue]Loading hotel cache...[/bold blue]")
    try:
        page = 1
        while True:
            response = make_request("GET", f"{BASE_URL}/hotel/?page={page}&page_size=100")
            items = response.get("items", [])
            if not items:
                break
            for hotel in items:
                cache["hotel"][hotel["name"]] = str(hotel["id"])
            if page >= response.get("total_pages", 1):
                break
            page += 1
        console.print(f"  ✓ Loaded {len(cache['hotel'])} hotels from database")
    except Exception as e:
        console.print(f"  ✗ Failed to load hotels: {e}")


def import_hotel_rooms(file_path: Path) -> None:
    """Import hotel rooms"""
    console.print("[bold blue]Importing hotel rooms...[/bold blue]")
    with open(file_path, encoding="utf-8") as f:
        rooms = json.load(f)

    for room in rooms:
        hotel_name = room.pop("hotel_name")
        if hotel_name not in cache["hotel"]:
            console.print(f"  ✗ Hotel '{hotel_name}' not found")
            continue

        room["hotel_id"] = cache["hotel"][hotel_name]
        try:
            result = make_request("POST", f"{BASE_URL}/hotel-room/", room)
            if result:
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
            console.print(f"  ✗ Hotel '{hotel_name}' not found")
            continue

        plan["hotel_id"] = cache["hotel"][hotel_name]
        try:
            result = make_request("POST", f"{BASE_URL}/room-rate-plan/", plan)
            if result:
                console.print(f"  ✓ Created rate plan: {plan['name']} at {hotel_name}")
        except Exception as e:
            console.print(f"  ✗ Failed to create rate plan at {hotel_name}: {e}")


def main():
    """Main function"""
    sample_data_dir = Path(__file__).parent / "sample_data"

    if not sample_data_dir.exists():
        console.print(f"[red]Error: Directory {sample_data_dir} does not exist[/red]")
        sys.exit(1)

    console.print("[bold green]Starting hotel data import...[/bold green]\n")

    try:
        # Load hotel cache from database
        load_hotel_cache()

        # Import hotel rooms
        import_hotel_rooms(sample_data_dir / "hotel_rooms.json")

        # Import room rate plans
        import_room_rate_plans(sample_data_dir / "room_rate_plans.json")

        console.print("\n[bold green]✓ Hotel data import completed![/bold green]")
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

