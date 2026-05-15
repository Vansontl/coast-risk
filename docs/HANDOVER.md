# HANDOVER - CoastalRisk WebApp v1

## 1. Mục tiêu bàn giao
`coastalrisk_webapp_v1` là bản webapp chuẩn hóa mới của hệ thống CoastalRisk, phát triển từ logic nghiệp vụ đã khóa ở `coastalrisk_blueprint_v5`.

## 2. Những gì hiện đã có
### Backend
- A1: Upload khảo sát chuyên gia, parse P/I/C, tính R, xếp hạng
- A2: Upload dataset, validate, lưu PostgreSQL, CRUD dòng dữ liệu
- A3: Train/test theo vùng, split 70/30 hoặc 80/20, metrics
- A4: Model registry, metadata, set default
- B2: Predict theo model + X1..X6
- B3: Lưu history, xem payload, export Word

### Frontend
- Có màn cho A1, A2, A3, A4, B2, B3
- Đã nối trực tiếp với backend FastAPI
- Đã qua nhiều vòng polish UI/UX để giảm lỗi thao tác

## 3. Runtime hiện tại
- Backend: FastAPI
- Frontend: static HTML/CSS/JS
- Database: PostgreSQL
- Python env: `backend/.venv`

## 4. Cách chạy nhanh
Xem `docs/RUNBOOK.md`

## 5. Những gì còn nên làm ở vòng sau
- Tối ưu giao diện đẹp hơn nữa
- Hoàn thiện report Word gần hơn bản `v5`
- Viết hướng dẫn sử dụng ngắn cho người dùng cuối
- Cân nhắc đóng gói frontend bằng web server gọn hơn nếu triển khai thật

## 6. Commit mốc chính
- `52cdf67` - khởi tạo webapp scaffold
- `03e255c` - A1 backend
- `af89ab6` - A2 upload/validate/store
- `d0af0e6` - A2 CRUD
- `7735f53` - A3 training
- `cfa55fb` - A4/B2 backend
- `0bd6cc0` - B3 backend
- `9876a76` - frontend A1/A2
- `1cbac94` - frontend A3/A4
- `b167c8a` - frontend B2/B3
- `0e5e33f` - export Word thật
- `9df7bcf` - nâng report + runbook
