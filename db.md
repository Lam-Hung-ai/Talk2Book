## 🧭 1. Nhóm **Định danh và Địa lý (Identity & Geo)**

| Bảng                                    | Mục đích                                                                                                                                                  |
| --------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **users**                               | Lưu thông tin người dùng: email, số điện thoại, mật khẩu mã hóa, trạng thái tài khoản. Là bảng trung tâm cho mọi giao dịch, đặt vé, thanh toán, đánh giá… |
| **roles**, **user_roles**               | Hỗ trợ phân quyền (admin, supplier, khách, CSKH...). `user_roles` là bảng nối nhiều-nhiều giữa người dùng và vai trò.                                     |
| **countries**, **cities**, **airports** | Dữ liệu địa lý: quốc gia, thành phố, sân bay. Dùng chung cho mọi module (Flights, Hotels, Activities). `airports` liên kết đến `cities`.                  |

---

## 🏢 2. Nhóm **Nhà cung cấp (Providers)**

| Bảng          | Mục đích                                                                                                                     |
| ------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| **providers** | Thông tin đối tác cung cấp dịch vụ (hãng bay, khách sạn, tour operator, đơn vị vận chuyển...).                               |

---

## ✈️ 3. Nhóm **Flights (Chuyến bay)**

| Bảng                 | Mục đích                                                                                                |
| -------------------- | ------------------------------------------------------------------------------------------------------- |
| **routes**           | Tuyến bay: điểm đi (`origin`), điểm đến (`destination`), khoảng cách.                                   |
| **flight_schedules** | Lịch trình cố định của hãng (ví dụ “VN123 SGN-HAN mỗi ngày 8h sáng”).                                   |
| **flight_instances** | Chuyến bay thực tế theo ngày cụ thể (ví dụ VN123 ngày 12/12/2025). Có giờ cất/hạ cánh thực, trạng thái. |
| **seat_inventory**   | Quản lý tồn kho ghế theo cabin (economy/premium/business/first). Ghi nhận tổng, đã giữ, đã bán. |

Cụm này cho phép tính năng tìm chuyến bay, giữ chỗ, bán vé, và cập nhật trạng thái thời gian thực.

---

## 🏨 4. Nhóm **Stays (Khách sạn / chỗ ở)**

| Bảng                     | Mục đích                                                                                                                 |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------------ |
| **hotels**               | Thông tin khách sạn (tên, sao, địa chỉ, tọa độ, giờ check-in/out...).                                                    |
| **hotel_rooms**          | Các loại phòng trong khách sạn (code, sức chứa, loại giường).                                                            |
| **room_rate_plans**      | Gói giá (có ăn sáng, hoàn hủy, đơn vị tiền tệ...).                                                                       |
| **room_inventory_daily** | Tồn phòng theo ngày, allotment (số lượng), đã bán, giá cơ bản, cờ stop-sell. Đây là bảng cốt lõi cho kiểm tra còn phòng. |

---

## 🎟️ 5. Nhóm **Activities / Transport**

| Bảng               | Mục đích                                                                                       |
| ------------------ | ---------------------------------------------------------------------------------------------- |
| **products**       | Hoạt động/tour hoặc dịch vụ vận chuyển (ví dụ “Tour du lịch Hạ Long”, “Xe khách Hà Nội-Sapa”). |
| **time_slots**     | Suất thời gian cụ thể của sản phẩm (ví dụ “Tour 8h sáng 1/5/2025”).                            |
| **slot_inventory** | Tồn chỗ theo suất: tổng, đã bán, giá, tiền tệ.                                                 |

---

## 💰 6. Nhóm **Giá, Thuế, Ngoại tệ (Pricing & FX)**

| Bảng               | Mục đích                                                                                                                     |
| ------------------ | ---------------------------------------------------------------------------------------------------------------------------- |
| **taxes**          | Danh mục thuế/phí áp dụng cho từng loại dịch vụ (VAT, phí sân bay…). Chỉ có **một** trong hai: tỷ lệ % hoặc số tiền cố định. |
| **exchange_rates** | Tỷ giá hằng ngày giữa các loại tiền tệ. Giúp hiển thị giá theo đơn vị nội địa.                                               |
| **price_quotes**   | Snapshot giá tạm thời (quote) cho người dùng khi họ tìm kiếm — đảm bảo tính “price integrity” khi đặt vé sau vài phút.       |

---

## 🪙 7. Nhóm **Khuyến mãi & Đặt chỗ (Promo & Bookings)**

| Bảng                   | Mục đích                                                                                                                  |
| ---------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| **coupons**            | Mã khuyến mãi: giảm phần trăm hoặc số tiền, thời gian hiệu lực, giới hạn số lần.                                          |
| **coupon_redemptions** | Lưu lịch sử người dùng dùng coupon nào cho booking nào (tránh lạm dụng).                                                  |
| **bookings**           | Đơn đặt chỗ tổng quát — áp dụng cho mọi loại sản phẩm. Lưu trạng thái (created, paid, canceled...), tổng tiền, thời điểm. |
| **booking_items**      | Chi tiết từng dịch vụ trong booking (một chuyến bay, một phòng, một tour...). Lưu snapshot thông tin & giá.               |
| **passengers**         | Thông tin hành khách/khách lưu trú (họ tên, ngày sinh, quốc tịch...).                                                     |
| **tickets**            | Vé hoặc voucher đã phát hành (có mã riêng).                                                                               |
| **booking_audit_logs** | Lịch sử thay đổi trạng thái, thao tác hệ thống/người dùng trên booking.                                                   |

---

## 💳 8. Nhóm **Thanh toán & Hoàn tiền (Payments & Refunds)**

| Bảng                     | Mục đích                                                                                                      |
| ------------------------ | ------------------------------------------------------------------------------------------------------------- |
| **payments**             | Giao dịch thanh toán chính, ghi nhận cổng thanh toán (Momo, Stripe...), trạng thái (authorized, captured...). |
| **refunds**              | Hoàn tiền cho booking: số tiền, lý do, trạng thái.                                                            |

Các bảng này bảo đảm khả năng xử lý nhiều gateway và hỗ trợ hoàn tiền linh hoạt.

---

## 🌟 9. Nhóm **Đánh giá & Hỗ trợ khách hàng (Reviews & Support)**

| Bảng                | Mục đích                                                                                           |
| ------------------- | -------------------------------------------------------------------------------------------------- |
| **reviews**         | Người dùng đánh giá dịch vụ (hotel, flight, activity) — có rating, tiêu đề, nội dung.              |
| **support_tickets** | Yêu cầu hỗ trợ: liên kết tới booking, theo dõi trạng thái xử lý (open, pending, resolved, closed). |

---

## 🔗 10. Quan hệ chính (tóm tắt)

* `users` là **trung tâm** của mọi tương tác.
* `providers` liên kết với các module (flights, hotels, products).
* `bookings` là **gốc của giao dịch**, nối đến `booking_items`, `payments`, `passengers`, `tickets`, `refunds`.
* `coupons` ↔ `bookings` là quan hệ **1–n** (một coupon có thể được áp dụng cho nhiều booking khác nhau).
* `price_quotes` đảm bảo giá được “đóng băng” tại thời điểm người dùng xem.

