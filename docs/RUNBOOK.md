# RUNBOOK - CoastalRisk WebApp v1

## 1. Kiến trúc chạy hiện tại
- Backend: FastAPI (`backend/`)
- Frontend: static HTML/CSS/JS (`frontend/`)
- Database: PostgreSQL
- Runtime Python: virtualenv trong `backend/.venv`

## 2. Cấu hình PostgreSQL hiện tại
Backend đọc từ `backend/.env`.
Ví dụ đang dùng:

```env
DATABASE_URL=postgresql+psycopg://postgres:123456@127.0.0.1:5432/coastalrisk_webapp_v1
```

## 3. Tạo database nếu chưa có
```powershell
$env:PGPASSWORD='123456'
psql -h 127.0.0.1 -U postgres -d postgres -c "CREATE DATABASE coastalrisk_webapp_v1;"
```

## 4. Tạo môi trường Python
```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\python -m pip install --upgrade pip
.\.venv\Scripts\python -m pip install -r requirements.txt
```

## 5. Chạy backend
```powershell
cd backend
.\.venv\Scripts\python -m uvicorn app.main:app --host 127.0.0.1 --port 8010
```

Health check:
```powershell
.\.venv\Scripts\python -c "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:8010/api/health').read().decode())"
```

## 6. Mở frontend
Mở file:
- `frontend/index.html`

Hoặc phục vụ tĩnh bằng một HTTP server đơn giản nếu cần.

## 7. Quy trình test nhanh A1 -> B3
1. A1: Upload file khảo sát chuyên gia
2. A2: Upload dataset chuẩn
3. A3: Train theo vùng, 80/20 hoặc 70/30
4. A4: Đặt model mặc định
5. B2: Chạy dự báo với X1..X6
6. B3: Xem history, payload, tải Word

## 8. Các endpoint chính
- `GET /api/health`
- `POST /api/expert-surveys/upload`
- `POST /api/datasets/upload`
- `GET /api/datasets`
- `GET /api/datasets/{dataset_id}/rows`
- `POST /api/datasets/{dataset_id}/rows`
- `PUT /api/datasets/rows/{row_id}`
- `DELETE /api/datasets/rows/{row_id}`
- `POST /api/training/run`
- `GET /api/models`
- `POST /api/models/{model_id}/set-default`
- `POST /api/predictions/run`
- `GET /api/reports/history`
- `GET /api/reports/history/{history_id}/report-payload`
- `GET /api/reports/history/{history_id}/export-docx`

## 9. Ghi chú
- Nếu PostgreSQL chưa sẵn sàng, có thể tạm dùng SQLite bằng cách đổi `DATABASE_URL` trong `.env`.
- Với Windows terminal, khi in JSON chứa tiếng Việt, nên đặt:
```powershell
$env:PYTHONIOENCODING='utf-8'
```
