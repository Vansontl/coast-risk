# Triển khai CoastalRisk WebApp bằng Dokploy

## 1) Chuẩn bị repo GitHub
Đưa toàn bộ mã nguồn lên GitHub, nhưng KHÔNG đẩy các file bí mật như `backend/.env`.

## 2) Tạo file môi trường trên VPS / Dokploy
Sử dụng các biến tối thiểu:

```env
POSTGRES_DB=coastalrisk_webapp_v1
POSTGRES_USER=postgres
POSTGRES_PASSWORD=doi_mat_khau_manh
CORS_ORIGINS=https://ten-mien-frontend-cua-anh,https://api.ten-mien-cua-anh
```

Có thể tham chiếu mẫu:
- `backend/.env.dokploy.example`

## 3) Tạo project trong Dokploy
- Source: GitHub repo
- Build type: Docker Compose
- Compose file: `compose.yaml`

## 4) Dữ liệu bền vững
Compose đã dùng volume:
- `postgres_data`
- `backend_storage`

Backend có entrypoint để tự tạo thư mục storage và tự copy lại template Excel vào volume lúc khởi động nếu volume còn trống.

## 5) Reverse proxy / domain
Khuyến nghị:
- frontend dùng domain chính
- backend dùng subdomain API riêng
- không cần mở port public trực tiếp nếu Dokploy reverse proxy qua domain

## 6) Healthcheck
Đã cấu hình sẵn:
- PostgreSQL healthcheck
- backend healthcheck `/api/health`
- frontend healthcheck HTTP `/`

## 7) Lưu ý quan trọng
- Backend hiện tự tạo bảng khi khởi động qua `Base.metadata.create_all(bind=engine)`
- Nếu dùng domain riêng, bắt buộc cập nhật `CORS_ORIGINS`
- Nếu sau này muốn tách storage riêng trên host/VPS, chỉ cần mount volume tương ứng cho `backend_storage`
