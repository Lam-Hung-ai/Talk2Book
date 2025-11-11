# AI_hotel
## 1. Thành viên 
- Nguyễn Văn Lâm Hùng
- Lê Sỹ Long Nhật
- Lê Nguyệt Anh
- Nguyễn Thảo Nguyên
- Nguyễn Tiến Đạt

## 2. Hướng dẫn làm việc
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
## 3. Hướng dẫn tạo cơ sở dữ liệu
- Tải [postgres](https://www.postgresql.org/download/) vào máy tính
- Đổi tên file backend/.env.example thành backend/.env, đồng thời cấu hình các thông số phù hợp với postgres
- Vào thư mục backend và chạy chương trình
```cmd
cd backend
python -m app.core.db
```

# 4. Hướng dẫn sử dụng [uv](https://docs.astral.sh/uv/getting-started/installation/) trong dự án
- Tạo môi trường ảo với [uv](https://docs.astral.sh/uv/pip/environments/#creating-a-virtual-environment) và đồng bộ các thư viện
```cmd
cd /backend
uv env
uv sync
```
- Kích hoạt môi trường ảo
```cmd
.venv\Scripts\activate
```
- chạy backend 
```cmd
fastapi run main.py
```