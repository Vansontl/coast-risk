from pydantic import BaseModel
from typing import Any, Dict, List, Optional


class DatasetUploadResponse(BaseModel):
    jobId: str
    status: str
    message: str


class HealthResponse(BaseModel):
    status: str
    app: str


class ExpertSurveyResult(BaseModel):
    factor: str
    group: str
    P: float
    I: float
    C: float
    R: float


class DatasetRowPayload(BaseModel):
    projectId: str
    region: str
    projectName: str
    riskScore: float
    riskLevel: str
    data: Dict[str, Any]


class DatasetRowUpsert(BaseModel):
    projectId: str
    projectName: str
    riskScore: float
    riskLevel: str
    data: Dict[str, Any]


class TrainingRequest(BaseModel):
    region: str
    split_ratio: float
    membership: str = 'gaussian'
    epochs: int = 5
    patience: int = 2
    premise_lr: float = 0.05
    rule_init_mode: str = 'data-driven'


class PredictRequest(BaseModel):
    region: str
    model_name: str
    inputs: Dict[str, float]
    project_stage: Optional[str] = None
    project_name: Optional[str] = None
