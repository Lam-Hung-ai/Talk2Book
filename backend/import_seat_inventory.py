#!/usr/bin/env python3
"""
Script để import seat_inventory cho các flight_instance đã có.

- Tự động lấy danh sách flight_instance từ API
- Với mỗi flight_instance, tạo một bản ghi seat_inventory cho mỗi cabin (economy / premium / business / first)
- Số ghế total/held/sold được random theo từng chuyến để dữ liệu phong phú
"""

import os
import sys
from datetime import date
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
            response = httpx.get(url, timeout=60.0)
        elif method == "POST":
            response = httpx.post(url, json=data, timeout=60.0)
        else:
            raise ValueError(f"Unsupported method: {method}")

        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        # 409: duplicate seat_inventory (instance_id + cabin)
        if e.response.status_code == 409:
            return {}
        console.print(f"[red]Error {e.response.status_code}: {e.response.text}[/red]")
        raise
    except Exception as e:
        console.print(f"[red]Request failed: {e}[/red]")
        raise


def load_flight_instances() -> list[dict[str, Any]]:
    """Load tất cả flight instances từ API"""
    console.print("[bold blue]Loading flight instances...[/bold blue]")
    items: list[dict[str, Any]] = []
    try:
        page = 1
        while True:
            resp = make_request(
                "GET", f"{BASE_URL}/flight-instance/?page={page}&page_size=200"
            )
            batch = resp.get("items", [])
            if not batch:
                break
            items.extend(batch)
            total_pages = resp.get("total_pages", 1)
            if page >= total_pages:
                break
            page += 1
        console.print(f"  ✓ Loaded {len(items)} flight instances")
        return items
    except Exception as e:
        console.print(f"  ✗ Failed to load flight instances: {e}")
        return []


def deterministic_rand(instance_id: str, salt: int = 0) -> int:
    """Hash đơn giản để tạo số pseudo-random ổn định theo instance_id"""
    h = 0
    for ch in instance_id:
        h = (h * 131 + ord(ch)) & 0xFFFFFFFF
    return (h + salt) & 0xFFFFFFFF


def build_seat_profiles(instance: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Tạo danh sách seat_inventory cho 1 flight_instance — một dòng cho mỗi cabin.
    """
    instance_id = str(instance["id"])
    base_rand = deterministic_rand(instance_id)

    has_premium = (base_rand & 0x1) == 0
    has_business = (base_rand & 0x2) == 0
    has_first = (base_rand & 0x4) == 0

    profiles: list[dict[str, Any]] = []

    # Economy — luôn có
    econ_total = 130 + (base_rand % 40)
    r = deterministic_rand(instance_id, salt=1)
    utilization = 0.3 + (r % 70) / 100
    sold = int(econ_total * utilization)
    held = min(5, r % 6)
    if held + sold > econ_total:
        held = 0
    profiles.append(
        {
            "instance_id": instance_id,
            "cabin": "economy",
            "total_seats": econ_total,
            "held_seats": held,
            "sold_seats": sold,
        }
    )

    if has_premium:
        prem_total = 24 + (base_rand % 12)
        r = deterministic_rand(instance_id, salt=2)
        utilization = 0.25 + (r % 60) / 100
        sold = int(prem_total * utilization)
        held = min(3, r % 4)
        if held + sold > prem_total:
            held = 0
        profiles.append(
            {
                "instance_id": instance_id,
                "cabin": "premium",
                "total_seats": prem_total,
                "held_seats": held,
                "sold_seats": sold,
            }
        )

    if has_business:
        biz_total = 16 + (base_rand % 8)
        r = deterministic_rand(instance_id, salt=3)
        utilization = 0.2 + (r % 50) / 100
        sold = int(biz_total * utilization)
        held = min(2, r % 3)
        if held + sold > biz_total:
            held = 0
        profiles.append(
            {
                "instance_id": instance_id,
                "cabin": "business",
                "total_seats": biz_total,
                "held_seats": held,
                "sold_seats": sold,
            }
        )

    if has_first:
        first_total = 8 + (base_rand % 4)
        r = deterministic_rand(instance_id, salt=4)
        utilization = 0.1 + (r % 40) / 100
        sold = int(first_total * utilization)
        held = min(1, r % 2)
        if held + sold > first_total:
            held = 0
        profiles.append(
            {
                "instance_id": instance_id,
                "cabin": "first",
                "total_seats": first_total,
                "held_seats": held,
                "sold_seats": sold,
            }
        )

    return profiles


def import_seat_inventory() -> None:
    """Main import logic"""
    console.print("[bold blue]Importing seat inventories...[/bold blue]")
    instances = load_flight_instances()
    if not instances:
        console.print("[red]No flight instances found. Please import them first.[/red]")
        return

    total_created = 0
    total_skipped = 0

    for idx, instance in enumerate(instances, start=1):
        instance_id = str(instance["id"])
        profiles = build_seat_profiles(instance)

        created = 0
        skipped = 0

        for profile in profiles:
            try:
                result = make_request(
                    "POST", f"{BASE_URL}/seat-inventory/", profile
                )
                if result:
                    created += 1
                    total_created += 1
                else:
                    skipped += 1
                    total_skipped += 1
            except Exception:
                skipped += 1
                total_skipped += 1

        console.print(
            f"  ✓ Instance {idx}/{len(instances)} "
            f"({instance_id}): {created} created, {skipped} skipped"
        )

    console.print(
        f"\n[bold green]Seat inventory import done: "
        f"{total_created} created, {total_skipped} skipped[/bold green]"
    )


def main() -> None:
    console.print(
        f"[bold green]Starting seat inventory import at {date.today()}...[/bold green]\n"
    )
    try:
        import_seat_inventory()
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
