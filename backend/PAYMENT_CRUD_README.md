# Payment CRUD Repository - Hướng Dẫn Sử Dụng

## 📁 Cấu trúc Files đã tạo

```
backend/app/
├── models/
│   └── payment_model.py          # Model Payment (đã có sẵn)
├── schemas/
│   └── payment.py                # ✅ MỚI - Pydantic schemas
├── repositories/
│   └── payment.py                # ✅ MỚI - Repository với CRUD
├── services/
│   └── payment.py                # ✅ MỚI - Business logic layer
└── api/v1/endpoints/
    └── payment.py                # ✅ MỚI - API endpoints
```

## 🎯 Tính năng PaymentRepository

### Kế thừa từ BaseCRUD:
- ✅ `get(id)` - Lấy payment theo ID
- ✅ `get_or_404(id)` - Lấy hoặc raise 404
- ✅ `get_multi(skip, limit, **filters)` - Lấy nhiều records
- ✅ `get_count(**filters)` - Đếm số lượng
- ✅ `create(obj_in)` - Tạo mới
- ✅ `update(db_obj, obj_in)` - Cập nhật
- ✅ `delete(id)` - Xóa

### Kế thừa từ SearchableRepository:
- ✅ `search(query, search_columns, ...)` - Tìm kiếm linh hoạt
- ✅ `count_search(...)` - Đếm kết quả tìm kiếm

### Methods đặc biệt cho Payment:
- ✅ `get_by_user_id(user_id)` - Lấy payments của user
- ✅ `get_by_booking_id(booking_id)` - Lấy payments theo booking
- ✅ `get_by_status(status)` - Lấy payments theo trạng thái
- ✅ `get_by_gateway(gateway)` - Lấy payments theo gateway
- ✅ `get_user_payments_by_status(user_id, status)` - Kết hợp filter
- ✅ `count_by_user_id(user_id)` - Đếm payments của user
- ✅ `count_by_status(status)` - Đếm theo status
- ✅ `get_total_amount_by_user(user_id, status)` - Tính tổng tiền
- ✅ `update_status(payment_id, new_status)` - Cập nhật trạng thái

## 🚀 Cách Sử Dụng

### 1. Đăng ký Router trong `app/api/v1/router.py`

```python
from fastapi import APIRouter
from app.api.v1.endpoints import user, payment  # ← Thêm import

api_router = APIRouter()
api_router.include_router(user.router, prefix="/users", tags=["Users"])
api_router.include_router(payment.router, prefix="/payments", tags=["Payments"])  # ← Thêm dòng này
```

### 2. Sử dụng trong Service/API

```python
from sqlmodel.ext.asyncio.session import AsyncSession
from app.repositories.payment import PaymentRepository

async def some_function(db: AsyncSession):
    repo = PaymentRepository(db)
    
    # Tạo payment mới
    from app.schemas.payment import PaymentCreate
    payment_data = PaymentCreate(
        user_id="uuid-here",
        gateway="VNPay",
        amount=100000,
        currency="VND",
        status="pending"
    )
    payment = await repo.create(payment_data)
    
    # Lấy payments của user
    user_payments = await repo.get_by_user_id(user_id="uuid-here")
    
    # Tìm kiếm
    results = await repo.search(
        query="VNPay",
        search_columns=["gateway", "status"]
    )
    
    # Cập nhật status
    updated = await repo.update_status(payment_id=1, new_status="completed")
    
    # Thống kê
    total = await repo.get_total_amount_by_user(
        user_id="uuid-here",
        status="completed"
    )
```

## 📡 API Endpoints

Sau khi đăng ký router, bạn có thể sử dụng các endpoints:

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| POST | `/api/v1/payments/` | Tạo payment mới |
| GET | `/api/v1/payments/{id}` | Lấy payment theo ID |
| GET | `/api/v1/payments/` | Lấy danh sách payments |
| GET | `/api/v1/payments/user/{user_id}` | Lấy payments của user |
| GET | `/api/v1/payments/user/{user_id}/stats` | Thống kê payments của user |
| PUT | `/api/v1/payments/{id}` | Cập nhật payment |
| PATCH | `/api/v1/payments/{id}/status` | Cập nhật status |
| DELETE | `/api/v1/payments/{id}` | Xóa payment |
| GET | `/api/v1/payments/search/` | Tìm kiếm payments |

## 🧪 Ví dụ Request/Response

### Tạo Payment mới
```bash
POST /api/v1/payments/
Content-Type: application/json

{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "booking_id": 123,
  "gateway": "VNPay",
  "amount": 1500000,
  "currency": "VND",
  "status": "pending"
}
```

### Lấy payments của user với filter
```bash
GET /api/v1/payments/user/550e8400-e29b-41d4-a716-446655440000?status=completed&skip=0&limit=10
```

### Tìm kiếm
```bash
GET /api/v1/payments/search/?q=VNPay&skip=0&limit=20
```

### Cập nhật status
```bash
PATCH /api/v1/payments/1/status?new_status=completed
```

## 🔍 Testing với Swagger UI

Sau khi chạy server, truy cập:
```
http://localhost:8000/docs
```

Bạn sẽ thấy tất cả endpoints trong section **Payments** để test trực tiếp.

## ⚠️ Lưu ý

1. **Status values hợp lệ**: `pending`, `completed`, `failed`, `refunded`, `cancelled`
2. **Gateway examples**: `VNPay`, `Momo`, `ZaloPay`, `Stripe`, `PayPal`
3. Amount phải > 0
4. user_id phải tồn tại trong bảng users (có foreign key constraint)

## 📝 Checklist Triển khai

- [x] Tạo schema (payment.py)
- [x] Tạo repository (payment.py) 
- [x] Tạo service layer (payment.py)
- [x] Tạo API endpoints (payment.py)
- [ ] Đăng ký router trong router.py
- [ ] Test các endpoints
- [ ] Thêm authentication/authorization nếu cần

---

**Tác giả**: Generated from BaseCRUD & SearchableRepository pattern
**Ngày tạo**: 2025-11-12
