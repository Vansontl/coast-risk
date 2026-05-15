# Architecture - CoastalRisk WebApp v1

## Stack mục tiêu
- Frontend: Web app (HTML/CSS/JS trước, có thể nâng cấp React sau)
- Backend: FastAPI
- Database: PostgreSQL
- ORM: SQLAlchemy
- ML: TensorFlow/Keras
- Reporting: Python report service

## Domain modules
- A1: expert-surveys
- A2: datasets
- A3: training
- A4: models
- B1/B2: prediction
- B3: reports-history

## Nguyên tắc
1. Business logic đi về backend
2. Frontend chỉ giữ UI state
3. PostgreSQL là persistence chính thức
4. Không phụ thuộc Electron
5. Mọi API phải bám đặc tả chuẩn v5
