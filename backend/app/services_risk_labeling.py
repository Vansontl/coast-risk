from __future__ import annotations
from typing import Any, Dict


def _blank(v: Any) -> bool:
    return v is None or str(v).strip() == ''


def _to_float(v: Any) -> float | None:
    if _blank(v):
        return None
    try:
        return float(v)
    except Exception:
        return None


def _clamp_scale(v: Any) -> float | None:
    n = _to_float(v)
    if n is None:
        return None
    return max(1.0, min(5.0, round(n, 2)))


def _map_wave(v: Any) -> float | None:
    n = _to_float(v)
    if n is None:
        return None
    if n < 1: return 1.0
    if n < 2: return 2.0
    if n < 3: return 3.0
    if n < 4: return 4.0
    return 5.0


def _map_wind(v: Any) -> float | None:
    n = _to_float(v)
    if n is None:
        return None
    if n < 6: return 1.0
    if n < 10: return 2.0
    if n < 14: return 3.0
    if n < 18: return 4.0
    return 5.0


def _map_weak(v: Any) -> float | None:
    n = _to_float(v)
    if n is None:
        return None
    if n < 2: return 1.0
    if n < 5: return 2.0
    if n < 10: return 3.0
    if n < 20: return 4.0
    return 5.0


def _avg(vals: list[float | None]) -> float | None:
    nums = [v for v in vals if v is not None]
    if not nums:
        return None
    return round(sum(nums) / len(nums), 4)


def derive_internal_vector(data: Dict[str, Any]) -> Dict[str, float | None]:
    return {
        'X1': _avg([_map_wave(data.get('waveHeight')), _clamp_scale(data.get('tideMode')), _map_wind(data.get('windSpeed')), _clamp_scale(data.get('stormLevel'))]),
        'X2': _avg([_clamp_scale(data.get('soilType')), _map_weak(data.get('weakLayer')), _clamp_scale(data.get('slideRisk')), _clamp_scale(data.get('surveyQuality'))]),
        'X3': _avg([_clamp_scale(data.get('techComplex')), _clamp_scale(data.get('constructionDiff')), _clamp_scale(data.get('equipmentDepend')), _clamp_scale(data.get('techError'))]),
        'X4': _avg([_clamp_scale(data.get('materialSupply')), _clamp_scale(data.get('equipmentMobilize')), _clamp_scale(data.get('transportRisk')), _clamp_scale(data.get('resourceShortage'))]),
        'X5': _avg([_clamp_scale(data.get('siteManage')), _clamp_scale(data.get('coordinationRisk')), _clamp_scale(data.get('scheduleRisk')), _clamp_scale(data.get('issueHandling'))]),
        'X6': _avg([_clamp_scale(data.get('laborSafety')), _clamp_scale(data.get('marineSafety')), _clamp_scale(data.get('environmentRisk')), _clamp_scale(data.get('emergencyResponse'))]),
    }


def infer_risk_level(score: float) -> str:
    if score < 1.0:
        return 'Thấp'
    if score < 2.0:
        return 'Trung bình'
    if score < 3.2:
        return 'Cao'
    return 'Rất cao'


def _likelihood_score(vector: Dict[str, float | None]) -> float | None:
    return _avg([vector.get('X1'), vector.get('X2'), vector.get('X3'), vector.get('X4'), vector.get('X5')])


def _impact_score(vector: Dict[str, float | None]) -> float | None:
    return _avg([vector.get('X2'), vector.get('X3'), vector.get('X5'), vector.get('X6')])


def derive_risk_matrix_from_vector(vector: Dict[str, Any]) -> Dict[str, float | None]:
    likelihood = _likelihood_score(vector)
    impact = _impact_score(vector)
    matrix_score = round((likelihood or 0) * (impact or 0), 4) if likelihood is not None and impact is not None else 0.0
    return {
        'likelihood': likelihood,
        'impact': impact,
        'matrixScore': matrix_score,
    }


def auto_label_risk(data: Dict[str, Any]) -> Dict[str, Any]:
    vector = derive_internal_vector(data)
    risk_matrix = derive_risk_matrix_from_vector(vector)
    matrix_score = risk_matrix.get('matrixScore') or 0.0
    score = round(matrix_score / 5.0, 4) if matrix_score else 0.0
    level = infer_risk_level(score) if matrix_score else ''
    labeled = dict(data)
    labeled['riskScore'] = score
    labeled['riskLevel'] = level
    labeled['_internalVector'] = vector
    labeled['_riskMatrix'] = risk_matrix
    labeled['riskMatrix'] = labeled['_riskMatrix']
    return labeled
