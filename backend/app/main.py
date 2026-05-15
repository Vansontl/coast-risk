from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .database import Base, engine
from .schemas import HealthResponse
from .routes_expert import router as expert_router
from .routes_dataset import router as dataset_router
from .routes_training import router as training_router
from .routes_models import router as models_router
from .routes_prediction import router as prediction_router
from .routes_reports import router as reports_router
from .routes_jobs import router as jobs_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.app_name)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(expert_router)
app.include_router(dataset_router)
app.include_router(training_router)
app.include_router(models_router)
app.include_router(prediction_router)
app.include_router(reports_router)
app.include_router(jobs_router)


@app.get('/api/health', response_model=HealthResponse)
def health():
    return HealthResponse(status='ok', app=settings.app_name)


@app.get('/api/overview')
def overview():
    return {
        'modules': ['A1', 'A2', 'A3', 'A4', 'B2', 'B3'],
        'status': 'scaffold-ready',
        'implemented': [
            'A1 upload+parse',
            'A2 upload+validate+store+crud',
            'A3 split+metrics+model-metadata',
            'A4 model-registry+default+metadata',
            'B2 prediction-run+history-store',
            'B3 history+detail+delete+report-payload',
            'A1/A2 backend progress jobs',
        ],
    }
