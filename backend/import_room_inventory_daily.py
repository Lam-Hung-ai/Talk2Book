#!/usr/bin/env python3
"""
Script tạo dữ liệu RoomInventoryDaily đa dạng cho tất cả phòng (room) và room_rate_plan.

- Sinh inventory theo ngày lưu trú (stay_date) từ hôm nay trở đi (mặc định 60 ngày)
- Giá phòng thay đổi theo:
  - Thứ trong tuần (weekday/weekend)
  - Mùa cao điểm (ví dụ: tháng 6–8, 12)
- Allotment/sold/stop_sell được sinh đa dạng nhưng vẫn đảm bảo ràng buộc:
  sold <= allotment, allotment > 0, base_price >= 0
"""

import os
import sys
from datetime import date, timedelta
from decimal import Decimal
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
        # 409: inventory cho room_id + rate_plan_id + stay_date đã tồn tại
        if e.response.status_code == 409:
            return {}
        console.print(f"[red]Error {e.response.status_code}: {e.response.text}[/red]")
        raise
    except Exception as e:
        console.print(f"[red]Request failed: {e}[/red]")
        raise


def deterministic_rand(key: str, salt: int = 0) -> int:
    """Hash đơn giản để tạo số pseudo-random ổn định theo key"""
    h = 0
    for ch in key:
        h = (h * 131 + ord(ch)) & 0xFFFFFFFF
    return (h + salt) & 0xFFFFFFFF


def load_hotels() -> dict[str, dict[str, Any]]:
    """Load tất cả hotels, trả về map id -> hotel data"""
    console.print("[bold blue]Loading hotels...[/bold blue]")
    hotels: dict[str, dict[str, Any]] = {}
    page = 1
    while True:
        resp = make_request("GET", f"{BASE_URL}/hotel/?page={page}&page_size=100")
        items = resp.get("items", [])
        if not items:
            break
        for h in items:
            hotels[str(h["id"])] = h
        if page >= resp.get("total_pages", 1):
            break
        page += 1
    console.print(f"  ✓ Loaded {len(hotels)} hotels")
    return hotels


def load_rooms_by_hotel() -> dict[str, list[dict[str, Any]]]:
    """Load tất cả hotel_room, group theo hotel_id"""
    console.print("[bold blue]Loading hotel rooms...[/bold blue]")
    by_hotel: dict[str, list[dict[str, Any]]] = {}
    page = 1
    while True:
        resp = make_request("GET", f"{BASE_URL}/hotel-room/?page={page}&page_size=100")
        items = resp.get("items", [])
        if not items:
            break
        for room in items:
            hid = str(room["hotel_id"])
            by_hotel.setdefault(hid, []).append(room)
        if page >= resp.get("total_pages", 1):
            break
        page += 1
    console.print(f"  ✓ Loaded {sum(len(v) for v in by_hotel.values())} rooms")
    return by_hotel


def load_rate_plans_by_hotel() -> dict[str, list[dict[str, Any]]]:
    """Load tất cả room_rate_plan, group theo hotel_id"""
    console.print("[bold blue]Loading room rate plans...[/bold blue]")
    by_hotel: dict[str, list[dict[str, Any]]] = {}
    page = 1
    while True:
        resp = make_request(
            "GET", f"{BASE_URL}/room-rate-plan/?page={page}&page_size=100"
        )
        items = resp.get("items", [])
        if not items:
            break
        for rp in items:
            hid = str(rp["hotel_id"])
            by_hotel.setdefault(hid, []).append(rp)
        if page >= resp.get("total_pages", 1):
            break
        page += 1
    console.print(f"  ✓ Loaded {sum(len(v) for v in by_hotel.values())} rate plans")
    return by_hotel


def base_price_for_hotel(hotel: dict[str, Any]) -> Decimal:
    """Tính giá base theo star_rating, fallback nếu thiếu dữ liệu"""
    raw_star = hotel.get("star_rating")
    try:
        star = float(raw_star) if raw_star is not None else 4.0
    except (TypeError, ValueError):
        star = 4.0
    # Quy ước đơn giản: 3* ~ 800k, 4* ~ 1.2M, 5* ~ 2M+
    if star < 3:
        return Decimal("600000")
    if star < 4:
        return Decimal("800000")
    if star < 4.5:
        return Decimal("1200000")
    if star < 5:
        return Decimal("1600000")
    return Decimal("2200000")


def price_for_date(
    base: Decimal, d: date, hotel_hash: int, rate_plan_hash: int
) -> Decimal:
    """Tinh giá theo ngày, weekend, high season, random nhẹ"""
    price = base

    # Weekend: Fri, Sat (4,5) tăng 15%
    if d.weekday() in (4, 5):
        price *= Decimal("1.15")

    # High season: tháng 6-8, 12: +25%
    if d.month in (6, 7, 8, 12):
        price *= Decimal("1.25")

    # Random nhẹ ±10% dựa trên hash
    rnd = (hotel_hash ^ rate_plan_hash ^ d.toordinal()) % 21  # 0..20
    factor = Decimal("0.90") + Decimal(rnd) / Decimal("200")  # 0.90 .. 2.0? no: 0.90 + 0.1 = 1.0
    price *= factor

    # Làm tròn đến 1,000 VND
    price = (price // Decimal("1000")) * Decimal("1000")
    if price < Decimal("300000"):
        price = Decimal("300000")
    return price


def build_inventory_for_room_rate_plan(
    room: dict[str, Any],
    rate_plan: dict[str, Any],
    hotel: dict[str, Any],
    days_ahead: int = 60,
) -> list[dict[str, Any]]:
    """Sinh danh sách RoomInventoryDaily cho 1 room + rate_plan"""
    room_id = str(room["id"])
    rate_plan_id = str(rate_plan["id"])
    key = f"{room_id}-{rate_plan_id}"
    inv: list[dict[str, Any]] = []

    hotel_hash = deterministic_rand(str(hotel["id"]))
    rp_hash = deterministic_rand(rate_plan_id)

    base = base_price_for_hotel(hotel)

    today = date.today()
    capacity = max(1, int(room.get("capacity") or 2))

    for offset in range(days_ahead):
        stay_date = today + timedelta(days=offset)
        k2 = deterministic_rand(key, salt=stay_date.toordinal())

        # Allotment: từ capacity đến capacity * 3 (tuỳ loại phòng/villa)
        multiplier = 1 + (k2 % 3)  # 1..3
        allotment = max(capacity, capacity * multiplier)

        # Sold: 10% - 95% allotment
        util = 0.1 + (k2 % 86) / 100  # 0.1..0.95
        sold = int(allotment * util)
        if sold > allotment:
            sold = allotment

        # Một số ngày stop_sell (ví dụ full hoặc close)
        stop_sell = False
        if (k2 % 97) == 0:  # hiếm
            stop_sell = True

        price = price_for_date(base, stay_date, hotel_hash, rp_hash)

        inv.append(
            {
                "room_id": room_id,
                "rate_plan_id": rate_plan_id,
                "stay_date": stay_date.isoformat(),
                "allotment": int(allotment),
                "sold": int(sold),
                "stop_sell": stop_sell,
                "base_price": str(price),
            }
        )

    return inv


def import_room_inventory_daily(days_ahead: int = 60) -> None:
    console.print(
        f"[bold blue]Importing RoomInventoryDaily for next {days_ahead} days...[/bold blue]"
    )

    hotels = load_hotels()
    rooms_by_hotel = load_rooms_by_hotel()
    rps_by_hotel = load_rate_plans_by_hotel()

    total_created = 0
    total_skipped = 0

    for hid, hotel in hotels.items():
        rooms = rooms_by_hotel.get(hid, [])
        rps = rps_by_hotel.get(hid, [])

        if not rooms or not rps:
            continue

        hotel_created = 0
        hotel_skipped = 0

        for room in rooms:
            for rp in rps:
                inventories = build_inventory_for_room_rate_plan(
                    room, rp, hotel, days_ahead=days_ahead
                )
                for inv in inventories:
                    try:
                        result = make_request(
                            "POST", f"{BASE_URL}/room-inventory-daily/", inv
                        )
                        if result:
                            hotel_created += 1
                            total_created += 1
                        else:
                            hotel_skipped += 1
                            total_skipped += 1
                    except Exception:
                        hotel_skipped += 1
                        total_skipped += 1

        console.print(
            f"  ✓ Hotel {hotel['name']}: created {hotel_created}, skipped {hotel_skipped}"
        )

    console.print(
        f"\n[bold green]RoomInventoryDaily import done: "
        f"{total_created} created, {total_skipped} skipped[/bold green]"
    )


def main() -> None:
    console.print(
        f"[bold green]Starting RoomInventoryDaily import from {date.today()}...[/bold green]\n"
    )
    try:
        import_room_inventory_daily(days_ahead=60)
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
