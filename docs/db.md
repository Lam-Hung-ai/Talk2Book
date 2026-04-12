# 🗺️ Tổng quan Database Schema — Talk2Book

> **Naming convention**: Tất cả tên bảng đều dùng **số ít (singular)**, phù hợp với định nghĩa SQLModel trong `backend/app/models`.
> **Auth system**: Dùng **Better Auth** — `user.id` là kiểu `TEXT` (không phải UUID).

---

## 🧭 1. Nhóm **Định danh và Địa lý (Identity & Geo)**

| Bảng                                        | Mục đích                                                                                                                                                              |
| ------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **currency**                                | Danh mục tiền tệ (mã ISO 3 ký tự, tên). Được tham chiếu bởi nhiều bảng.                                                                                              |
| **country**                                 | Quốc gia (mã ISO 2 ký tự), liên kết đến `currency`.                                                                                                                  |
| **city**                                    | Thành phố, liên kết đến `country`. Ràng buộc unique theo `(country_code, name)`.                                                                                      |
| **airport**                                 | Sân bay (IATA/ICAO), liên kết đến `city`. Dùng chung cho module Flights.                                                                                              |
| **category**                                | Bảng tra cứu / phân loại dùng chung (`group_name` + `value`). Dùng để quản lý taxonomy linh hoạt mà không cần thêm enum mới.                                         |
| **user**                                    | Định danh Better Auth: `id` (**TEXT**), `name`, `email` (CITEXT unique), `email_verified`, `image`, `created_at`, `updated_at`. Là bảng trung tâm cho mọi tương tác. |
| **session**                                 | Phiên đăng nhập Better Auth: `token` (unique), `expires_at`, `ip_address`, `user_agent`. Thay thế cho `refresh_token` truyền thống.                                   |
| **account**                                 | Tài khoản OAuth / credential Better Auth: `account_id`, `provider_id`, `access_token`, `refresh_token`, `id_token`, `scope`, `password`.                             |
| **verification**                            | Token xác thực email/phone Better Auth: `identifier`, `value`, `expires_at`.                                                                                          |
| **user_profile**                            | Hồ sơ domain (tách biệt với auth): `gender`, `birthday`, `nationality`, `address`. Tên/ảnh hiển thị: `user.name`, `user.image`.                                      |
| **role**, **user_role**                     | Phân quyền (admin, supplier, khách, CSKH…). `user_role` là bảng nối nhiều-nhiều; `user_id` kiểu TEXT.                                                                |

---

## 🏢 2. Nhóm **Nhà cung cấp (Providers)**

| Bảng         | Mục đích                                                                                                                                                        |
| ------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **provider** | Thông tin đối tác cung cấp dịch vụ (hãng bay, khách sạn, tour operator, vận chuyển). Có `type` enum: `airline \| hotel \| operator \| transport` và `status`. |

---

## ✈️ 3. Nhóm **Flights (Chuyến bay)**

| Bảng                | Mục đích                                                                                                                                          |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| **route**           | Tuyến bay: `origin` và `destination` (IATA), `distance_km`. Ràng buộc `origin != destination` và unique `(origin, destination)`.                 |
| **flight_schedule** | Lịch trình cố định của hãng (ví dụ "VN123 SGN-HAN mỗi thứ 2–6 8h sáng"). Mã hoá ngày bay bằng chuỗi `dow` 7-bit. Hạng ghế nằm ở `seat_inventory`; có `price_from` tham khảo. |
| **flight_instance** | Chuyến bay thực tế theo ngày cụ thể. Có `dep_datetime`, `arr_datetime` (TIMESTAMPTZ), `aircraft_code` (tàu bay thực tế / điều chỉnh sát giờ bay), `status`.                         |
| **seat_inventory**  | Tồn kho ghế theo cabin (`economy/premium/business/first`). PK composite `(instance_id, cabin)`. Ghi nhận `total_seats`, `held_seats`, `sold_seats`. |

Cụm này cho phép tìm chuyến bay, giữ chỗ, bán vé và cập nhật trạng thái thời gian thực.

---

## 🏨 4. Nhóm **Stays (Khách sạn / chỗ ở)**

| Bảng                     | Mục đích                                                                                                                                                   |
| ------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **hotel**                | Thông tin khách sạn (tên, sao, địa chỉ, tọa độ `lat/lng`, `description`, `images` JSONB, `amenities` JSONB, `usp`, `room_count`).                         |
| **hotel_room**           | Các loại phòng trong khách sạn (`code`, `capacity`, `bed_config`, `room_type`, `area_sqm`, `view_type`, `service_package`, `cancellation_policy`, `images`). |
| **room_rate_plan**       | Gói giá (`meal_plan`, `cancellation_policy` JSONB, `currency_code`). Unique `(hotel_id, name)`.                                                            |
| **room_inventory_daily** | Tồn phòng theo ngày. PK composite `(room_id, rate_plan_id, stay_date)`. Các cột: `allotment`, `sold`, `stop_sell`, `base_price`.                           |

---

## 🎟️ 5. Nhóm **Tour / Activities / Transport**

| Bảng               | Mục đích                                                                                                                                                      |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **product**        | Sản phẩm du lịch. `type` enum: `tour \| activity \| transport`. Có `title`, `tour_type`, `description`, `detail_description`, `itinerary` JSONB, `costs` JSONB, `images` JSONB, `duration_days`. |
| **time_slot**      | Suất thời gian của sản phẩm (`start_datetime`, `end_datetime`). Unique `(product_id, start_datetime, end_datetime)`.                                          |
| **slot_inventory** | Tồn kho theo suất. PK là `slot_id` (1:1 với `time_slot`). Có `capacity`, `sold`, `price`, `currency_code`.                                                   |

---

## 💰 6. Nhóm **Báo giá (Price Quote)**

| Bảng            | Mục đích                                                                                                                                                              |
| --------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **price_quote** | Snapshot giá tạm thời khi người dùng tìm kiếm — đảm bảo "price integrity". `user_id` kiểu TEXT. Có `vertical`, `payload` JSONB, `total_amount`, `expires_at`. |

---

## 🪙 7. Nhóm **Khuyến mãi & Đặt chỗ (Promo & Bookings)**

| Bảng                  | Mục đích                                                                                                                                               |
| --------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **coupon**            | Mã khuyến mãi: `discount_type` (`percent/amount`), `discount_value`, giới hạn sử dụng (`max_uses_total`, `max_uses_per_user`, `current_uses`), thời gian hiệu lực. |
| **coupon_redemption** | Lưu lịch sử dùng coupon: `user_id` (TEXT), `booking_id`, `discount_amount`. Trigger tự động cập nhật `coupon.current_uses`.                           |
| **booking**           | Đơn đặt chỗ tổng quát. `user_id` kiểu TEXT. `state` enum: `draft → pending_payment → confirmed → cancelled/refunded`. Liên kết `quote_id`, `coupon_id`. |
| **booking_item**      | Chi tiết từng dịch vụ trong booking (`vertical`, `supplier_ref`, `details` JSONB, `price_amount`).                                                     |
| **passenger**         | Hành khách/khách lưu trú liên kết với booking (`full_name`, `nationality`).                                                                            |
| **ticket**            | Vé/voucher phát hành liên kết `booking_item`. `type` enum: `flight \| hotel \| tour`, `code` unique.                                                   |
| **booking_audit_log** | Lịch sử thay đổi trạng thái booking: `actor_type`, `actor_id` (TEXT), `action`, `from_state`, `to_state`, `meta` JSONB.                                |

---

## 💳 8. Nhóm **Thanh toán (Payments)**

| Bảng        | Mục đích                                                                                                                                                              |
| ----------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **payment** | Giao dịch thanh toán: `provider` (cổng), `amount`, `currency_code`, `status` (`pending → authorized → captured/failed/refunded`), `idempotency_key` unique. |

---

## 🌟 9. Nhóm **Đánh giá (Reviews)**

| Bảng       | Mục đích                                                                                                                                           |
| ---------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| **review** | Đánh giá dịch vụ. `user_id` kiểu TEXT. `target_type` enum: `hotel \| product \| flight \| airport`, `target_key`, `rating` (1–5). Unique per user+target. |

---

## 🔗 10. Quan hệ chính (tóm tắt)

* **`user`** (Better Auth, `id` = TEXT) là trung tâm của mọi tương tác: `session`, `account`, `verification`, `user_profile`, `booking`, `review`, `coupon_redemption`, `booking_audit_log`.
* **`provider`** liên kết với các module inventory: `flight_schedule`, `hotel`, `product`.
* **`booking`** là gốc của giao dịch, nối đến `booking_item`, `payment`, `passenger`, `ticket`, `booking_audit_log`, `coupon_redemption`.
* **`coupon`** ↔ `booking` thông qua `coupon_redemption` (many-to-many có metadata). Trigger tự động cập nhật `current_uses`.
* **`price_quote`** đảm bảo giá được "đóng băng" tại thời điểm người dùng xem.
* **`currency`** được tham chiếu rộng rãi: `country`, `room_rate_plan`, `slot_inventory`, `coupon_redemption`, `price_quote`, `booking`, `payment`, `coupon`.
* **`category`** là bảng taxonomy dùng chung, thay thế cho việc thêm nhiều enum.

---

## 📋 11. Danh sách bảng đầy đủ

| # | Bảng                   | PK kiểu       | Auth FK kiểu |
|---|------------------------|---------------|--------------|
| 1 | `currency`             | `CHAR(3)`     | —            |
| 2 | `country`              | `CHAR(2)`     | —            |
| 3 | `city`                 | `UUID`        | —            |
| 4 | `airport`              | `CHAR(3)`     | —            |
| 5 | `category`             | `UUID`        | —            |
| 6 | `user`                 | `TEXT`        | —            |
| 7 | `session`              | `TEXT`        | `user_id TEXT` |
| 8 | `account`              | `TEXT`        | `user_id TEXT` |
| 9 | `verification`         | `TEXT`        | —            |
| 10 | `user_profile`        | `UUID`        | `user_id TEXT` |
| 11 | `role`                | `UUID`        | —            |
| 12 | `user_role`           | composite     | `user_id TEXT` |
| 13 | `provider`            | `UUID`        | —            |
| 14 | `route`               | `UUID`        | —            |
| 15 | `flight_schedule`     | `UUID`        | —            |
| 16 | `flight_instance`     | `UUID`        | —            |
| 17 | `seat_inventory`      | composite     | —            |
| 18 | `hotel`               | `UUID`        | —            |
| 19 | `hotel_room`          | `UUID`        | —            |
| 20 | `room_rate_plan`      | `UUID`        | —            |
| 21 | `room_inventory_daily`| composite     | —            |
| 22 | `product`             | `UUID`        | —            |
| 23 | `time_slot`           | `UUID`        | —            |
| 24 | `slot_inventory`      | `UUID` (FK)   | —            |
| 25 | `price_quote`         | `UUID`        | `user_id TEXT` |
| 26 | `coupon`              | `UUID`        | —            |
| 27 | `coupon_redemption`   | `UUID`        | `user_id TEXT` |
| 28 | `booking`             | `UUID`        | `user_id TEXT` |
| 29 | `booking_item`        | `UUID`        | —            |
| 30 | `passenger`           | `UUID`        | —            |
| 31 | `ticket`              | `UUID`        | —            |
| 32 | `booking_audit_log`   | `UUID`        | `actor_id TEXT` |
| 33 | `payment`             | `UUID`        | —            |
| 34 | `review`              | `UUID`        | `user_id TEXT` |
