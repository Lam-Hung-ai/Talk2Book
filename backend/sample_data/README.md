# Dữ liệu mẫu cho Talk2Book

Thư mục này chứa các file JSON chứa dữ liệu mẫu về du lịch Việt Nam để import vào database.

## Cấu trúc dữ liệu

### 1. `countries.json`
- Quốc gia: Việt Nam (VN)
- Currency: VND

### 2. `cities.json`
- 15 thành phố lớn ở Việt Nam: Hà Nội, TP.HCM, Đà Nẵng, Hội An, Nha Trang, Phú Quốc, Sapa, Huế, Hạ Long, Đà Lạt, Mũi Né, Vũng Tàu, Cần Thơ, Quy Nhon, Tam Đảo

### 3. `airports.json`
- 8 sân bay chính: Nội Bài (HAN), Tân Sơn Nhất (SGN), Đà Nẵng (DAD), Phú Quốc (PQC), Cam Ranh (CXR), Phú Bài (HUI), Liên Khương (DLI), Cần Thơ (VCA)

### 4. `providers.json`
- **Airlines**: Vietnam Airlines, VietJet Air, Bamboo Airways
- **Hotels**: Vinpearl, InterContinental, Sofitel, Marriott, Vietnam Hotels
- **Operators**: Saigontourist, Vietravel, BestPrice Travel, Local Vietnam Tours
- **Transport**: Phương Trang, Hoàng Long

### 5. `hotels.json`
- 20 khách sạn tại các thành phố lớn
- Bao gồm thông tin: tên, địa chỉ, sao, check-in/check-out time, tọa độ

### 6. `hotel_rooms.json`
- Phòng khách sạn với các loại: Standard (STD), Deluxe (DLX), Suite, Villa
- Thông tin: mã phòng, sức chứa, cấu hình giường

### 7. `room_rate_plans.json`
- Kế hoạch giá phòng: Giá cơ bản (RO), Bao gồm bữa sáng (BB), All Inclusive (AI)

### 8. `products.json`
- 34 sản phẩm du lịch:
  - **Activities**: Tours tham quan, ẩm thực, trekking, lặn biển, etc.
  - **Transport**: Xe khách, xe giường nằm

### 9. `routes.json`
- 20 tuyến bay nội địa giữa các sân bay

### 10. `flight_schedules.json`
- 22 lịch bay của các hãng hàng không
- Bao gồm: số hiệu chuyến bay, thời gian khởi hành/đến, ngày trong tuần

### 11. `flight_instances_config.json`
- Cấu hình để tạo flight instances tự động
- Mỗi flight schedule sẽ tạo instances cho 90 ngày từ ngày hiện tại trở đi
- Tự động tính toán ngày bay dựa trên days of week (dow) của schedule

## Cách sử dụng

### Import tất cả dữ liệu

```bash
cd backend/sample_data
source ../.venv/bin/activate
python import_sample_data.py
```

Script sẽ tự động import theo thứ tự dependency:
1. Countries
2. Cities
3. Providers
4. Airports
5. Routes
6. Hotels
7. Products
8. Flight Schedules

### Import hotel rooms và rate plans (sau khi đã import hotels)

```bash
python import_hotel_data.py
```

### Import flight instances (sau khi đã import flight schedules)

```bash
python import_flight_instances.py
```

Script này sẽ:
- Tự động lấy ngày hiện tại của máy tính
- Tạo flight instances cho 90 ngày tiếp theo (có thể chỉnh trong config)
- Chỉ tạo instances cho các ngày mà flight schedule hoạt động (dựa trên dow)
- Tự động tính toán dep_datetime và arr_datetime

## Lưu ý

- Đảm bảo server backend đang chạy tại `http://127.0.0.1:8000`
- Script sẽ tự động xử lý dependencies (ví dụ: tạo country trước, rồi mới tạo city)
- Nếu dữ liệu đã tồn tại, script sẽ bỏ qua và tiếp tục
- Tất cả dữ liệu đều bằng tiếng Việt

## Mở rộng dữ liệu

Để thêm dữ liệu mới:
1. Chỉnh sửa file JSON tương ứng
2. Chạy lại script import
3. Hoặc tạo script mới nếu cần import entity mới

## Tổng số bản ghi

- 1 quốc gia
- 15 thành phố
- 8 sân bay
- 14 nhà cung cấp
- 20 khách sạn
- 21 phòng khách sạn
- 12 kế hoạch giá phòng
- 34 sản phẩm du lịch
- 20 tuyến bay
- 22 lịch bay
- ~1,890 flight instances (tự động tạo từ ngày hiện tại, 90 ngày × 21 schedules)

**Tổng cộng: ~2,057+ bản ghi dữ liệu mẫu**

## Lưu ý về Flight Instances

Flight instances được tạo tự động từ flight schedules:
- Ngày bay bắt đầu từ ngày hiện tại của máy tính
- Mặc định tạo cho 90 ngày tiếp theo (có thể chỉnh trong `flight_instances_config.json`)
- Chỉ tạo instances cho các ngày mà flight schedule hoạt động (dựa trên `dow` - days of week)
- Tự động tính toán `dep_datetime` và `arr_datetime` dựa trên `flight_date` và schedule times
- Có thể chạy lại script để tạo thêm instances cho các ngày mới

