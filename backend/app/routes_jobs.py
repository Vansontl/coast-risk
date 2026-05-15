from __future__ import annotations
from fastapi import APIRouter, HTTPException
from .progress_store import get_job
from .timing_store import get_timing

router = APIRouter(prefix='/api/jobs', tags=['jobs'])


@router.get('/{job_id}')
def read_job(job_id: str):
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail='Job not found')
    timing = get_timing(job_id)
    if timing:
        job['timing'] = timing
    return job
