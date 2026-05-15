from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from .database import get_db
from .models import Dataset, DatasetRow, Region, TrainedModel
from .schemas import TrainingRequest
from .config import settings
from .services_training import parse_payload_json, build_grouped_vector, split_rows, split_train_val_test, calculate_metrics, save_model_artifact
from .anfis_trainer import train_anfis_artifact
from .anfis_inference import anfis_infer
from .baseline_models import weighted_fuzzy_score, train_ann_baseline, ann_predict

router = APIRouter(prefix='/api/training', tags=['training'])


@router.post('/run')
def run_training(payload: TrainingRequest, db: Session = Depends(get_db)):
    region_value = (payload.region or '').strip()
    region = db.query(Region).filter(Region.name == region_value).first()
    if not region and region_value.isdigit():
        region = db.query(Region).filter(Region.id == int(region_value)).first()
    if not region:
        raise HTTPException(status_code=404, detail='Region not found')

    dataset = db.query(Dataset).filter(Dataset.region_id == region.id, Dataset.is_active == True).order_by(Dataset.id.desc()).first()
    if not dataset:
        raise HTTPException(status_code=404, detail='Active dataset not found for region')

    dataset_rows = db.query(DatasetRow).filter(DatasetRow.dataset_id == dataset.id).all()
    if len(dataset_rows) < 2:
        raise HTTPException(status_code=400, detail='Need at least 2 dataset rows for training')

    rows = []
    for item in dataset_rows:
        payload_data = parse_payload_json(item.payload_json)
        vector = build_grouped_vector(payload_data)
        rows.append({
            'projectId': item.project_id,
            'vector': vector,
            'riskScore': float(item.risk_score),
        })

    train_rows, val_rows, test_rows = split_train_val_test(rows, train_ratio=payload.split_ratio, val_ratio=0.15)
    artifact = train_anfis_artifact(train_rows, val_rows, test_rows, epochs=payload.epochs, patience=payload.patience, membership=payload.membership, premise_lr=payload.premise_lr, rule_init_mode=payload.rule_init_mode)
    preds = [anfis_infer(row['vector'], artifact)['score'] for row in test_rows]
    actuals = [row['riskScore'] for row in test_rows]
    metrics = calculate_metrics(actuals, preds)
    ann_artifact = train_ann_baseline(train_rows)
    ann_preds = [ann_predict(row['vector'], ann_artifact) for row in test_rows]
    ann_metrics = calculate_metrics(actuals, ann_preds)
    fuzzy_preds = [weighted_fuzzy_score(row['vector']) for row in test_rows]
    fuzzy_metrics = calculate_metrics(actuals, fuzzy_preds)

    model_name = f"model_{payload.region.replace(' ', '_').lower()}_{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}"
    artifact_path = save_model_artifact(settings.model_dir, model_name, artifact)
    model = TrainedModel(
        region_id=region.id,
        model_name=model_name,
        model_type='ANFIS-Sugeno',
        metrics_json=json.dumps({
            'split_ratio': payload.split_ratio,
            'membership': payload.membership,
            'rule_init_mode': payload.rule_init_mode,
            'train_count': len(train_rows),
            'val_count': len(val_rows),
            'test_count': len(test_rows),
            **metrics,
            'epochs': artifact.get('epochs', 0),
            'history': artifact.get('history', []),
            'best_epoch': artifact.get('best_epoch'),
            'best_test_loss': artifact.get('best_test_loss'),
            'early_stopped': artifact.get('early_stopped', False),
            'baseline_compare': {
                'ann': ann_metrics,
                'fuzzy': fuzzy_metrics,
                'anfis': metrics,
            },
        }, ensure_ascii=False),
        artifact_path=artifact_path,
        is_default=False,
    )
    db.add(model)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail=f'Model persistence conflict: {exc.__class__.__name__}')
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f'Model persistence failed: {exc.__class__.__name__}: {exc}')
    db.refresh(model)

    return {
        'region': region.name,
        'datasetId': dataset.id,
        'modelName': model_name,
        'trainCount': len(train_rows),
        'valCount': len(val_rows),
        'testCount': len(test_rows),
        'metrics': {
            **metrics,
            'membership': payload.membership,
            'rule_init_mode': payload.rule_init_mode,
            'epochs': artifact.get('epochs', 0),
            'history': artifact.get('history', []),
            'best_epoch': artifact.get('best_epoch'),
            'best_test_loss': artifact.get('best_test_loss'),
            'early_stopped': artifact.get('early_stopped', False),
            'baseline_compare': {
                'ann': ann_metrics,
                'fuzzy': fuzzy_metrics,
                'anfis': metrics,
            },
        },
        'artifact': artifact,
    }


@router.get('/models/{model_id}/report-payload')
def get_training_report_payload(model_id: int, db: Session = Depends(get_db)):
    model = db.query(TrainedModel).filter(TrainedModel.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail='Model not found')
    region = db.query(Region).filter(Region.id == model.region_id).first()
    metrics = json.loads(model.metrics_json) if model.metrics_json else {}
    artifact = parse_payload_json(Path(model.artifact_path).read_text(encoding='utf-8')) if model.artifact_path else {}
    return {
        'modelName': model.model_name,
        'region': region.name if region else None,
        'metrics': metrics,
        'artifact': artifact,
        'reportDate': datetime.utcnow().date().isoformat(),
    }
