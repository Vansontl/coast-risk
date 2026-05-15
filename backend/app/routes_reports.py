from __future__ import annotations
import json
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from .config import settings
from .database import get_db
from .models import PredictionHistory, TrainedModel, Region
from pathlib import Path
from .services_report_export import build_report_docx, build_training_report_docx, build_membership_compare_report_docx

router = APIRouter(prefix='/api/reports', tags=['reports'])


def serialize_history(item: PredictionHistory):
    result = json.loads(item.result_json)
    recommendations = result.get('recommendations') or {}
    return {
        'id': item.id,
        'projectName': item.project_name,
        'projectLocation': item.project_location,
        'regionId': item.region_id,
        'modelId': item.model_id,
        'inputs': json.loads(item.input_json),
        'result': result,
        'projectStage': recommendations.get('projectStage'),
        'createdAt': item.created_at.isoformat(),
    }


def build_payload(item: PredictionHistory, db: Session):
    model = db.query(TrainedModel).filter(TrainedModel.id == item.model_id).first() if item.model_id else None
    region = db.query(Region).filter(Region.id == item.region_id).first() if item.region_id else None
    result = json.loads(item.result_json)
    inputs = json.loads(item.input_json)
    metrics = json.loads(model.metrics_json) if model and model.metrics_json else {}

    dominant_factor = None
    if inputs:
        try:
            dominant_factor = max(inputs.items(), key=lambda kv: float(kv[1]))[0]
        except Exception:
            dominant_factor = None

    recommendations = result.get('recommendations') or {}
    return {
        'reportDate': datetime.utcnow().date().isoformat(),
        'projectName': item.project_name,
        'projectLocation': item.project_location,
        'region': region.name if region else None,
        'modelName': model.model_name if model else None,
        'modelType': model.model_type if model else None,
        'projectStage': recommendations.get('projectStage'),
        'inputs': inputs,
        'result': result,
        'metrics': metrics,
        'dominantFactor': dominant_factor,
        'recommendations': recommendations,
        'riskMatrix': recommendations.get('riskMatrix') or result.get('riskMatrix'),
        'summary': recommendations.get('summary') or f"Công trình {item.project_name} có điểm rủi ro {result.get('score')}, mức rủi ro {result.get('level')}.",
    }


@router.get('/history')
def list_history(db: Session = Depends(get_db)):
    items = db.query(PredictionHistory).order_by(PredictionHistory.id.desc()).all()
    return [serialize_history(item) for item in items]


@router.get('/history/{history_id}')
def get_history_detail(history_id: int, db: Session = Depends(get_db)):
    item = db.query(PredictionHistory).filter(PredictionHistory.id == history_id).first()
    if not item:
        raise HTTPException(status_code=404, detail='History not found')
    return serialize_history(item)


@router.delete('/history/{history_id}')
def delete_history(history_id: int, db: Session = Depends(get_db)):
    item = db.query(PredictionHistory).filter(PredictionHistory.id == history_id).first()
    if not item:
        raise HTTPException(status_code=404, detail='History not found')
    db.delete(item)
    db.commit()
    return {'ok': True, 'deletedHistoryId': history_id}


@router.get('/history/{history_id}/report-payload')
def get_report_payload(history_id: int, db: Session = Depends(get_db)):
    item = db.query(PredictionHistory).filter(PredictionHistory.id == history_id).first()
    if not item:
        raise HTTPException(status_code=404, detail='History not found')
    return build_payload(item, db)


@router.get('/history/{history_id}/export-docx')
def export_report_docx(history_id: int, db: Session = Depends(get_db)):
    item = db.query(PredictionHistory).filter(PredictionHistory.id == history_id).first()
    if not item:
        raise HTTPException(status_code=404, detail='History not found')
    try:
        payload = build_payload(item, db)
        file_name, output_path = build_report_docx(payload, settings.report_dir)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f'Không xuất được báo cáo Word: {exc}')
    return FileResponse(output_path, filename=file_name, media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')


@router.get('/models/{model_id}/export-training-docx')
def export_training_report_docx(model_id: int, db: Session = Depends(get_db)):
    model = db.query(TrainedModel).filter(TrainedModel.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail='Model not found')
    region = db.query(Region).filter(Region.id == model.region_id).first()
    metrics = json.loads(model.metrics_json) if model.metrics_json else {}
    if model.artifact_path and not Path(model.artifact_path).exists():
        raise HTTPException(status_code=404, detail='Không tìm thấy artifact của model để xuất báo cáo huấn luyện')
    try:
        artifact = json.loads(Path(model.artifact_path).read_text(encoding='utf-8')) if model.artifact_path else {}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f'Không đọc được artifact của model: {exc}')
    payload = {
        'modelName': model.model_name,
        'region': region.name if region else None,
        'metrics': metrics,
        'artifact': artifact,
        'ruleInitMode': metrics.get('rule_init_mode') or artifact.get('rule_init'),
        'reportDate': datetime.utcnow().date().isoformat(),
    }
    try:
        file_name, output_path = build_training_report_docx(payload, settings.report_dir)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f'Không xuất được báo cáo huấn luyện: {exc}')
    return FileResponse(output_path, filename=file_name, media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')


@router.get('/memberships/export-compare-docx')
def export_membership_compare_docx(db: Session = Depends(get_db)):
    models = db.query(TrainedModel).filter(TrainedModel.artifact_path.isnot(None)).all()
    grouped = {}
    for model in models:
        metrics = json.loads(model.metrics_json) if model.metrics_json else {}
        membership = metrics.get('membership', 'gaussian')
        grouped.setdefault(membership, []).append((model, metrics))
    groups = []
    for membership, items in grouped.items():
        best_model, best_metrics = max(items, key=lambda pair: float(pair[1].get('r2', -999)))
        groups.append({
            'membership': membership,
            'count': len(items),
            'bestModel': best_model.model_name,
            'r2': best_metrics.get('r2'),
            'mae': best_metrics.get('mae'),
            'rmse': best_metrics.get('rmse'),
        })
    payload = {'reportDate': datetime.utcnow().date().isoformat(), 'groups': groups}
    file_name, output_path = build_membership_compare_report_docx(payload, settings.report_dir)
    return FileResponse(output_path, filename=file_name, media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
