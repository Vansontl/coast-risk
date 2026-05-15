from __future__ import annotations
import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .database import get_db
from .models import Region, TrainedModel

router = APIRouter(prefix='/api/models', tags=['models'])


@router.get('')
def list_models(region: str | None = None, include_legacy: bool = False, db: Session = Depends(get_db)):
    query = db.query(TrainedModel)
    if region:
        region_obj = db.query(Region).filter(Region.name == region).first()
        if not region_obj:
            return []
        query = query.filter(TrainedModel.region_id == region_obj.id)
    if not include_legacy:
        query = query.filter(TrainedModel.artifact_path.isnot(None))
    models = query.order_by(TrainedModel.id.desc()).all()
    return [
        {
            'id': m.id,
            'modelName': m.model_name,
            'modelType': m.model_type,
            'metrics': json.loads(m.metrics_json),
            'isDefault': m.is_default,
            'createdAt': m.created_at.isoformat(),
            'artifactPath': m.artifact_path,
            'isLegacy': m.artifact_path is None,
        }
        for m in models
    ]


@router.get('/default/{region_name}')
def get_default_model(region_name: str, db: Session = Depends(get_db)):
    region = db.query(Region).filter(Region.name == region_name).first()
    if not region:
        raise HTTPException(status_code=404, detail='Region not found')
    model = db.query(TrainedModel).filter(TrainedModel.region_id == region.id, TrainedModel.is_default == True).order_by(TrainedModel.id.desc()).first()
    if not model:
        raise HTTPException(status_code=404, detail='Default model not found')
    return {
        'id': model.id,
        'modelName': model.model_name,
        'modelType': model.model_type,
        'metrics': json.loads(model.metrics_json),
        'isDefault': model.is_default,
        'createdAt': model.created_at.isoformat(),
    }


@router.post('/{model_id}/set-default')
def set_default_model(model_id: int, db: Session = Depends(get_db)):
    model = db.query(TrainedModel).filter(TrainedModel.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail='Model not found')
    db.query(TrainedModel).filter(TrainedModel.region_id == model.region_id).update({'is_default': False})
    model.is_default = True
    db.commit()
    db.refresh(model)
    return {'ok': True, 'modelId': model.id, 'modelName': model.model_name}


@router.get('/{model_id}')
def get_model_metadata(model_id: int, db: Session = Depends(get_db)):
    model = db.query(TrainedModel).filter(TrainedModel.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail='Model not found')
    return {
        'id': model.id,
        'modelName': model.model_name,
        'modelType': model.model_type,
        'metrics': json.loads(model.metrics_json),
        'isDefault': model.is_default,
        'artifactPath': model.artifact_path,
        'createdAt': model.created_at.isoformat(),
    }
