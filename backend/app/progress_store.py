from __future__ import annotations
from threading import Lock
from typing import Dict, Any
from time import time

_jobs: Dict[str, Dict[str, Any]] = {}
_lock = Lock()


def create_job(job_id: str, kind: str) -> None:
    now = time()
    with _lock:
        _jobs[job_id] = {
            'jobId': job_id,
            'kind': kind,
            'status': 'queued',
            'percent': 0,
            'message': 'Đang chờ xử lý',
            'result': None,
            'error': None,
            'startedAt': now,
            'updatedAt': now,
            'finishedAt': None,
            'etaSeconds': None,
        }


def update_job(job_id: str, *, status: str | None = None, percent: int | None = None, message: str | None = None, result: Any = None, error: str | None = None) -> None:
    with _lock:
        job = _jobs.get(job_id)
        if not job:
            return
        if status is not None:
            job['status'] = status
        if percent is not None:
            job['percent'] = percent
        if message is not None:
            job['message'] = message
        if result is not None:
            job['result'] = result
        if error is not None:
            job['error'] = error
        now = time()
        job['updatedAt'] = now
        started_at = job.get('startedAt') or now
        current_percent = job.get('percent') or 0
        elapsed = max(now - started_at, 0.001)
        if current_percent > 0 and current_percent < 100:
            total_est = elapsed / (current_percent / 100)
            job['etaSeconds'] = max(round(total_est - elapsed), 0)
        elif current_percent >= 100:
            job['etaSeconds'] = 0
            job['finishedAt'] = now


def get_job(job_id: str) -> Dict[str, Any] | None:
    with _lock:
        job = _jobs.get(job_id)
        return dict(job) if job else None
