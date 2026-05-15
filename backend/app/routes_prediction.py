from __future__ import annotations
import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .database import get_db
from .models import Region, TrainedModel, PredictionHistory
from .schemas import PredictRequest
from .services_training import load_model_artifact
from .anfis_inference import anfis_infer
from .services_recommendation import build_risk_recommendations
from .services_risk_labeling import derive_risk_matrix_from_vector

router = APIRouter(prefix='/api/predictions', tags=['predictions'])


def score_to_level(score: float) -> str:
    if score < 2:
        return 'Thấp'
    if score < 3:
        return 'Trung bình'
    if score < 4:
        return 'Cao'
    return 'Rất cao'


@router.post('/run')
def run_prediction(payload: PredictRequest, db: Session = Depends(get_db)):
    region = db.query(Region).filter(Region.name == payload.region).first()
    if not region:
        raise HTTPException(status_code=404, detail='Region not found')

    model = db.query(TrainedModel).filter(TrainedModel.model_name == payload.model_name, TrainedModel.region_id == region.id).first()
    if not model:
        raise HTTPException(status_code=404, detail='Model not found')

    required = ['X1', 'X2', 'X3', 'X4', 'X5', 'X6']
    if any(key not in payload.inputs for key in required):
        raise HTTPException(status_code=400, detail='Missing X1..X6 inputs')
    if any(float(payload.inputs.get(key, 0) or 0) <= 0 for key in required):
        raise HTTPException(status_code=400, detail='Dữ liệu đầu vào nội bộ chưa hợp lệ. Anh hãy xử lý hồ sơ đầu vào trước khi dự báo.')

    artifact = load_model_artifact(model.artifact_path)
    inference = anfis_infer(payload.inputs, artifact)
    score = inference['score']
    level = score_to_level(score)

    risk_matrix = derive_risk_matrix_from_vector(payload.inputs)
    recommendations = build_risk_recommendations(payload.inputs, score, level, payload.project_stage, risk_matrix)

    history = PredictionHistory(
        region_id=region.id,
        model_id=model.id,
        project_name=(payload.project_name or 'prediction-session').strip() or 'prediction-session',
        project_location=None,
        input_json=json.dumps(payload.inputs, ensure_ascii=False),
        result_json=json.dumps({'score': score, 'level': level, 'recommendations': recommendations}, ensure_ascii=False),
    )
    db.add(history)
    db.commit()

    return {
        'modelName': model.model_name,
        'score': score,
        'riskLevel': level,
        'ruleDetails': inference.get('details', []),
        'recommendations': recommendations,
        'riskMatrix': (recommendations or {}).get('_riskMatrix') or (recommendations or {}).get('riskMatrix'),
    }
