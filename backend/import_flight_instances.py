#!/usr/bin/env python3
"""
Script để import flight instances từ ngày hiện tại trở đi
Tự động tạo instances dựa trên flight schedules đã có
"""
import json
import os
import sys
from datetime import date, datetime, timedelta, time
from pathlib import Path
from typing import Any

import httpx
from rich.console import Console

console = Console()
BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:8000/api/v1")


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
            return {}
        console.print(f"[red]Error {e.response.status_code}: {e.response.text}[/red]")
        raise
    except Exception as e:
        console.print(f"[red]Request failed: {e}[/red]")
        raise


def load_flight_schedules() -> dict[str, dict[str, Any]]:
    """Load tất cả flight schedules từ API"""
    console.print("[bold blue]Loading flight schedules...[/bold blue]")
    schedules_map: dict[str, dict[str, Any]] = {}
    
    try:
        page = 1
        while True:
            response = make_request("GET", f"{BASE_URL}/flight-schedule/?page={page}&page_size=100")
            items = response.get("items", [])
            if not items:
                break
            
            for schedule in items:
                flight_number = schedule["flight_number"]
                schedules_map[flight_number] = {
                    "id": str(schedule["id"]),
                    "dep_time": schedule["dep_time"],
                    "arr_time": schedule["arr_time"],
                    "arrival_day_offset": schedule.get("arrival_day_offset", 0),
                    "dow": schedule["dow"],  # Days of week bitstring
                }
            
            if page >= response.get("total_pages", 1):
                break
            page += 1
        
        console.print(f"  ✓ Loaded {len(schedules_map)} flight schedules")
        return schedules_map
    except Exception as e:
        console.print(f"  ✗ Failed to load flight schedules: {e}")
        return {}


def parse_time(time_str: str) -> time:
    """Parse time string to time object"""
    if isinstance(time_str, str):
        return datetime.strptime(time_str, "%H:%M:%S").time()
    return time_str


def get_days_of_week(dow_bitstring: str) -> list[int]:
    """Convert bitstring (e.g., '1111111') to list of weekday numbers (0=Monday, 6=Sunday)"""
    days = []
    for i, bit in enumerate(dow_bitstring):
        if bit == "1":
            days.append(i)
    return days


def create_flight_instances(
    schedule_id: str,
    flight_date: date,
    dep_time: time,
    arr_time: time,
    arrival_day_offset: int,
    status: str,
) -> dict[str, Any]:
    """Tạo flight instance data từ schedule và date"""
    # Combine date and time for dep_datetime
    dep_datetime = datetime.combine(flight_date, dep_time)
    
    # Calculate arrival date (add day offset if needed)
    arr_date = flight_date + timedelta(days=arrival_day_offset)
    arr_datetime = datetime.combine(arr_date, arr_time)
    
    return {
        "schedule_id": schedule_id,
        "flight_date": flight_date.isoformat(),
        "dep_datetime": dep_datetime.isoformat(),
        "arr_datetime": arr_datetime.isoformat(),
        "status": status,
    }


def import_flight_instances(config_file: Path) -> None:
    """Import flight instances từ config file"""
    console.print("[bold blue]Importing flight instances...[/bold blue]")
    
    # Load flight schedules
    schedules_map = load_flight_schedules()
    if not schedules_map:
        console.print("[red]No flight schedules found. Please import flight schedules first.[/red]")
        return
    
    # Load config
    with open(config_file, encoding="utf-8") as f:
        configs = json.load(f)
    
    today = date.today()
    total_created = 0
    total_skipped = 0
    
    for config in configs:
        flight_number = config["flight_number"]
        days_ahead = config.get("days_ahead", 90)
        status = config.get("status", "scheduled")
        
        if flight_number not in schedules_map:
            console.print(f"  ✗ Flight schedule '{flight_number}' not found")
            continue
        
        schedule = schedules_map[flight_number]
        schedule_id = schedule["id"]
        dep_time = parse_time(schedule["dep_time"])
        arr_time = parse_time(schedule["arr_time"])
        arrival_day_offset = schedule["arrival_day_offset"]
        dow = schedule["dow"]
        
        # Get days of week this flight operates
        operating_days = get_days_of_week(dow)
        
        # Create instances for each day in the future that matches the operating days
        created_count = 0
        skipped_count = 0
        
        for day_offset in range(days_ahead):
            flight_date = today + timedelta(days=day_offset)
            weekday = flight_date.weekday()  # 0=Monday, 6=Sunday
            
            # Check if flight operates on this day
            # Note: Python weekday: 0=Monday, 6=Sunday
            # DOW bitstring: position 0=Monday, 6=Sunday
            if weekday not in operating_days:
                continue
            
            instance_data = create_flight_instances(
                schedule_id=schedule_id,
                flight_date=flight_date,
                dep_time=dep_time,
                arr_time=arr_time,
                arrival_day_offset=arrival_day_offset,
                status=status,
            )
            
            try:
                result = make_request("POST", f"{BASE_URL}/flight-instance/", instance_data)
                if result:
                    created_count += 1
                    total_created += 1
                else:
                    skipped_count += 1
                    total_skipped += 1
            except Exception as e:
                console.print(f"  ✗ Failed to create instance for {flight_number} on {flight_date}: {e}")
                skipped_count += 1
                total_skipped += 1
        
        console.print(
            f"  ✓ {flight_number}: Created {created_count} instances, "
            f"skipped {skipped_count} (next {days_ahead} days)"
        )
    
    console.print(f"\n[bold green]Total: {total_created} created, {total_skipped} skipped[/bold green]")


def main():
    """Main function"""
    sample_data_dir = Path(__file__).parent / "sample_data"
    config_file = sample_data_dir / "flight_instances_config.json"
    
    if not config_file.exists():
        console.print(f"[red]Error: Config file {config_file} does not exist[/red]")
        sys.exit(1)
    
    console.print("[bold green]Starting flight instances import...[/bold green]\n")
    console.print(f"[yellow]Note: Instances will be created from today ({date.today()}) onwards[/yellow]\n")
    
    try:
        import_flight_instances(config_file)
        console.print("\n[bold green]✓ Flight instances import completed![/bold green]")
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
