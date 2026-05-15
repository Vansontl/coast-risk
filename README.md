# CoastalRisk WebApp v1

Webapp nghiên cứu/ứng dụng cho CoastalRisk ANFIS, hỗ trợ quy trình A1 → A4 và B1 → B3, có huấn luyện mô hình, dự báo rủi ro, giải thích suy luận và xuất báo cáo Word.

## 1) Cấu trúc dự án
- `backend/` — FastAPI API, logic ANFIS, lưu trữ dữ liệu, báo cáo
- `frontend/` — giao diện web tĩnh
- `docs/` — runbook và ghi chú kỹ thuật
- `deploy/` — cấu hình triển khai Docker / Dokploy
- `compose.yaml` — triển khai đầy đủ frontend + backend + PostgreSQL

## 2) Chạy local nhanh
### Backend
```powershell
./run_backend.ps1
```
API mặc định: `http://127.0.0.1:8010`

### Frontend
```powershell
./run_frontend.ps1
```
Web mặc định: `http://127.0.0.1:3010`

## 3) Triển khai lên GitHub + Dokploy
### File đã chuẩn bị
- `Dockerfile.backend`
- `Dockerfile.frontend`
- `compose.yaml`
- `.dockerignore`
- `deploy/nginx/default.conf`
- `deploy/DOKPLOY.md`
- `backend/.env.production.example`
- `backend/.env.dokploy.example`
- `backend/docker-entrypoint.sh`

### Quy trình khuyến nghị
1. Tạo repo GitHub và push source code.
2. Không push `backend/.env`, `.venv/`, file test tạm, dữ liệu runtime.
3. Trong Dokploy, tạo app từ GitHub repo bằng `compose.yaml`.
4. Cấu hình biến môi trường production theo `backend/.env.dokploy.example`.
5. Gắn domain/subdomain và cập nhật `CORS_ORIGINS` cho đúng.

## 4) Dữ liệu mẫu và file template
Hai file mẫu Excel phục vụ import/export hiện nằm trong:
- `backend/storage/templates/du_lieu_mau.xlsx`
- `backend/storage/templates/khao_sat_mau.xlsx`

Bản production đã được chuẩn bị để:
- copy template vào image lúc build
- tự bootstrapping lại về `/app/storage/templates/` khi container backend khởi động lần đầu

=> vì vậy vẫn có thể giữ `backend/storage/` ngoài Git, miễn là anh xử lý riêng 2 file template này khi build/push source.

## 5) Ghi chú production
- Backend tự tạo bảng khi khởi động qua `Base.metadata.create_all(bind=engine)`.
- Compose mặc định dùng PostgreSQL 16.
- Frontend được phục vụ qua Nginx.
- Backend được chạy bằng `uvicorn app.main:app --host 0.0.0.0 --port 8010`.

## 6) Tài liệu vận hành
Xem thêm:
- `docs/RUNBOOK.md`
- `deploy/DOKPLOY.md`
