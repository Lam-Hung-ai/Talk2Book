# Talk to Book - Đặt khách sạn vé máy bay bằng giọng nói
## Demo 1
https://github.com/user-attachments/assets/e44602cc-9d20-455d-a4d6-e8a57554dc8b
## 1. Thành viên
- Nguyễn Văn Lâm Hùng
- Lê Sỹ Long Nhật
- Lê Nguyệt Anh
- Nguyễn Thảo Nguyên
- Nguyễn Tiến Đạt

## 2. Hướng dẫn làm việc
- Khuyến nghị mọi người cài đặt Ruff extention trên VSCode để điều chỉnh định dạng chuẩn (chi cần lưu là Ruff extention sẽ định dạng lại file chuẩn quốc tế)
- Nếu chưa tải repo về máy thì chạy:
```cmd
git clone https://github.com/Lam-Hung-ai/Talk2Book.git
```
- Khi muốn thay đổi code thì tạo nhánh mới:
```cmd
git branch ten_cua_ban  # Nhánh mới mang tên bạn
git branch -a # Xem tất cả các nhánh
git checkout ten_cua_ban # Chuyển sang nhánh mới để làm việc
```
- Khi muốn push code lên repo chung thì:
```cmd
git status      #Xem trạng thái
git add .       # Thêm các file sửa đổi vào git local
git status      #Xem trạng thái
git commit -m "update"      #Xác nhận thay đổi code
git push -u oringin ten_cua_ban     # Đẩy code lên repo với nhánh ten_cua_ban. Chờ mình xác nhận merge code lên nhánh main
```
- Khi muốn cập nhật code đồng bộ với repo github:
```cmd
git pull --no-rebase
```

# 3. Hướng dẫn sử dụng [uv](https://docs.astral.sh/uv/getting-started/installation/) trong dự án
- Tạo môi trường ảo với [uv](https://docs.astral.sh/uv/pip/environments/#creating-a-virtual-environment) và đồng bộ các thư viện
```cmd
cd /backend
uv venv
uv sync
```
- **Pre-commit (nên làm một lần sau khi clone):** Cài hook Git để mỗi lần `git commit` tự chạy kiểm tra định dạng (Ruff), YAML, gitleaks, v.v. theo `.pre-commit-config.yaml` ở thư mục gốc repo. Gói `pre-commit` nằm trong nhóm `dev` của backend. Đứng ở **thư mục gốc** của repo (cùng cấp với `backend/` và `frontend/`), chạy:
```cmd
uv sync --project backend --group dev
uv run --project backend pre-commit install
```
- Kích hoạt môi trường ảo
```cmd
.venv\Scripts\activate
```
- chạy backend
```cmd
cd backend/app
fastapi run main.py
```

## 4. Hướng dẫn tạo cơ sở dữ liệu và dữ liệu mẫu
- Tải [postgres](https://www.postgresql.org/download/) vào máy tính
- Đổi tên file backend/.env.example thành backend/.env, đồng thời cấu hình các thông số phù hợp với postgres
- Vào thư mục backend và chạy chương trình
```cmd
cd backend
python -m app.db.init_db
```
- tạo dữ liệu mẫu chạy từng file chú ý lúc tạo dữ liệu mẫu thì phải chạy backend
- chạy backend
```cmd
cd backend/app
fastapi run main.py
```
```cmd
cd backend
python import_sample_data.py
python import_room_inventory_daily.py
python import_flight_instances.py
python import_seat_inventory.py
```
