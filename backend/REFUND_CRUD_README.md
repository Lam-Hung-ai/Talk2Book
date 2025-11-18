# Refund CRUD - Hướng Dẫn Sử Dụng

## ✅ Đã tạo các file:

```
backend/app/
├── schemas/refund.py          # ✅ Pydantic schemas
├── repositories/refund.py     # ✅ Repository với CRUD
├── services/refund.py         # ✅ Business logic layer
└── api/v1/endpoints/refund.py # ✅ API endpoints
```

---

## 🎯 Tính năng RefundRepository

### Kế thừa từ BaseCRUD + SearchableRepository:
- ✅ Tất cả CRUD cơ bản (get, create, update, delete, get_multi, get_count)
- ✅ Tìm kiếm linh hoạt (search, count_search)

### Methods đặc biệt cho Refund:
- ✅ `get_by_payment_id(payment_id)` - Lấy refunds của một payment
- ✅ `get_by_status(status)` - Lấy refunds theo trạng thái
- ✅ `count_by_status(status)` - Đếm theo status
- ✅ `count_by_payment_id(payment_id)` - Đếm refunds của payment
- ✅ `get_total_refund_amount_by_payment(payment_id, status)` - Tính tổng tiền hoàn
- ✅ `update_status(refund_id, new_status)` - Cập nhật trạng thái
- ✅ `get_pending_refunds()` - Lấy refunds đang chờ
- ✅ `get_approved_refunds()` - Lấy refunds đã duyệt

---

## 🔒 Business Logic (RefundService)

### Validations:
1. **Khi tạo refund mới:**
   - ✅ Payment phải tồn tại
   - ✅ Amount > 0
   - ✅ Amount không vượt quá payment amount
   - ✅ Tổng refund (bao gồm cả refund mới) không vượt quá payment amount

2. **Khi cập nhật refund:**
   - ✅ Validate amount nếu có thay đổi

3. **Khi complete refund:**
   - ✅ Chỉ complete được refund đã approved

4. **Khi delete refund:**
   - ✅ Chỉ xóa được refund pending hoặc rejected

### Workflow actions:
- ✅ `approve_refund()` - Duyệt refund
- ✅ `reject_refund()` - Từ chối refund
- ✅ `complete_refund()` - Hoàn thành refund (sau khi approved)

---

## 📡 API Endpoints

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| POST | `/api/v1/refunds/` | Tạo refund mới |
| GET | `/api/v1/refunds/search/` | Tìm kiếm refunds |
| GET | `/api/v1/refunds/pending/` | Lấy refunds đang chờ |
| GET | `/api/v1/refunds/approved/` | Lấy refunds đã duyệt |
| GET | `/api/v1/refunds/payment/{payment_id}` | Lấy refunds của payment |
| GET | `/api/v1/refunds/payment/{payment_id}/stats` | Thống kê refunds của payment |
| GET | `/api/v1/refunds/{refund_id}` | Lấy refund theo ID |
| GET | `/api/v1/refunds/` | Lấy tất cả refunds |
| PUT | `/api/v1/refunds/{refund_id}` | Cập nhật refund |
| PATCH | `/api/v1/refunds/{refund_id}/status` | Cập nhật status |
| PATCH | `/api/v1/refunds/{refund_id}/approve` | Duyệt refund |
| PATCH | `/api/v1/refunds/{refund_id}/reject` | Từ chối refund |
| PATCH | `/api/v1/refunds/{refund_id}/complete` | Hoàn thành refund |
| DELETE | `/api/v1/refunds/{refund_id}` | Xóa refund |

---

## 🚀 Đăng ký Router

Thêm vào `app/api/v1/router.py`:

```python
from app.api.v1.endpoints import refund

api_router.include_router(refund.router, prefix="/refunds", tags=["Refunds"])
```

---

## 🧪 Ví dụ Sử Dụng

### 1. Tạo Refund mới
```bash
POST /api/v1/refunds/
Content-Type: application/json

{
  "payment_id": 123,
  "amount": 500000,
  "reason": "Khách hàng yêu cầu hủy đơn",
  "status": "pending"
}
```

### 2. Duyệt Refund
```bash
PATCH /api/v1/refunds/1/approve
```

### 3. Hoàn thành Refund (sau khi đã approve)
```bash
PATCH /api/v1/refunds/1/complete
```

### 4. Lấy thống kê refunds của payment
```bash
GET /api/v1/refunds/payment/123/stats

Response:
{
  "payment_id": 123,
  "total_refunds": 2,
  "total_refund_amount": 1000000,
  "completed_amount": 500000,
  "pending_amount": 500000
}
```

### 5. Tìm kiếm refunds
```bash
GET /api/v1/refunds/search/?q=hủy+đơn&skip=0&limit=20
```

---

## 📊 Trạng thái Refund

| Status | Mô tả |
|--------|-------|
| `pending` | Đang chờ xử lý |
| `approved` | Đã được duyệt |
| `rejected` | Đã từ chối |
| `completed` | Đã hoàn thành |
| `cancelled` | Đã hủy |

---

## 🔄 Workflow Refund

```
1. Tạo refund (status: pending)
   ↓
2a. Approve → (status: approved)
    ↓
    Complete → (status: completed) ✅
    
2b. Reject → (status: rejected) ❌
```

---

## ⚠️ Lưu ý

1. **Không thể refund nhiều hơn payment amount**
2. **Tổng tất cả refunds completed không được vượt quá payment amount**
3. **Chỉ complete được refund đã approved**
4. **Chỉ xóa được refund pending hoặc rejected**
5. Refund amount phải > 0

---

## 📝 Checklist

- [x] Tạo schema (refund.py)
- [x] Tạo repository (refund.py)
- [x] Tạo service layer (refund.py)
- [x] Tạo API endpoints (refund.py)
- [x] Thêm validations
- [x] Thêm workflow actions (approve, reject, complete)
- [ ] Đăng ký router trong router.py
- [ ] Test các endpoints

---

**Hoàn thành!** 🎉
