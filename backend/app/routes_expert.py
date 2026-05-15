from __future__ import annotations
from pathlib import Path
from uuid import uuid4
from fastapi import APIRouter, UploadFile, File, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
from .config import settings
from .progress_store import create_job, update_job
from .worker_jobs import process_expert_survey_job

router = APIRouter(prefix='/api/expert-surveys', tags=['expert-surveys'])


@router.post('/upload')
async def upload_expert_survey(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    job_id = str(uuid4())
    create_job(job_id, 'expert-survey-upload')
    suffix = Path(file.filename or 'survey.xlsx').suffix or '.xlsx'
    upload_dir = Path(settings.upload_dir).resolve()
    upload_dir.mkdir(parents=True, exist_ok=True)
    save_path = upload_dir / f"expert-survey-{uuid4()}{suffix}"
    content = await file.read()
    save_path.write_bytes(content)
    update_job(job_id, status='running', percent=5, message='Đã nhận file khảo sát, chuẩn bị xử lý nền')
    background_tasks.add_task(process_expert_survey_job, job_id, file.filename, str(save_path))
    return {
        'jobId': job_id,
        'status': 'queued',
        'message': 'File khảo sát đã nhận, backend đang xử lý nền'
    }


@router.get('/template/export')
def export_expert_template():
    template_path = Path(settings.storage_dir).resolve() / 'templates' / 'khao_sat_mau.xlsx'
    if not template_path.exists():
        raise HTTPException(status_code=404, detail='Không tìm thấy file mẫu khảo sát')
    return FileResponse(
        str(template_path),
        filename='khao_sat_mau.xlsx',
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
