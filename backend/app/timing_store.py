from __future__ import annotations
from threading import Lock
from typing import Dict, Any

_timings: Dict[str, Dict[str, Any]] = {}
_lock = Lock()


def set_timing(job_id: str, data: Dict[str, Any]) -> None:
    with _lock:
        _timings[job_id] = data


def get_timing(job_id: str) -> Dict[str, Any] | None:
    with _lock:
        item = _timings.get(job_id)
        return dict(item) if item else None
