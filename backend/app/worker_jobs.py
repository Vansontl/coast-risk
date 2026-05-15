from __future__ import annotations
import json
from time import perf_counter
from sqlalchemy.orm import Session
from .database import SessionLocal
from .models import Region, Dataset, DatasetRow
from .progress_store import update_job
from .services_expert import parse_expert_survey_excel
from .services_dataset import parse_dataset_excel
from .timing_store import set_timing


def _get_or_create_region(db: Session, name: str) -> Region:
    region = db.query(Region).filter(Region.name == name).first()
    if region:
        return region
    region = Region(name=name)
    db.add(region)
    db.commit()
    db.refresh(region)
    return region


def process_expert_survey_job(job_id: str, file_name: str, save_path: str) -> None:
    t0 = perf_counter()
    try:
        update_job(job_id, status='running', percent=10, message='Đang xử lý khảo sát chuyên gia')
        parsed = parse_expert_survey_excel(save_path, progress=lambda p, m: update_job(job_id, status='running', percent=p, message=m))
        result = {
            'jobId': job_id,
            'file_name': file_name,
            'stored_path': save_path,
            **parsed,
        }
        set_timing(job_id, {'kind': 'expert', 'totalSeconds': round(perf_counter() - t0, 4), 'responseCount': parsed.get('response_count', 0), 'factorCount': len(parsed.get('results', []))})
        update_job(job_id, status='done', percent=100, message='Hoàn tất xử lý khảo sát', result=result)
    except Exception as exc:
        update_job(job_id, status='failed', percent=0, message='Lỗi xử lý khảo sát', error=str(exc))


def process_dataset_job(job_id: str, file_name: str, save_path: str) -> None:
    db = SessionLocal()
    t0 = perf_counter()
    try:
        update_job(job_id, status='running', percent=10, message='Đang xử lý dataset')
        t_parse_start = perf_counter()
        parsed = parse_dataset_excel(save_path, progress=lambda p, m: update_job(job_id, status='running', percent=p, message=m))
        t_parse = perf_counter() - t_parse_start
        validation = parsed['validation']
        rows = validation['rows']
        region_name = rows[0]['region'] if rows else 'Chưa xác định'
        region = _get_or_create_region(db, region_name)

        update_job(job_id, status='running', percent=82, message='Đang chuẩn bị lưu dữ liệu vào PostgreSQL')
        db.query(Dataset).filter(Dataset.region_id == region.id, Dataset.is_active == True).update({'is_active': False})
        db.commit()

        dataset = Dataset(region_id=region.id, name=file_name or 'uploaded-dataset', is_active=True)
        db.add(dataset)
        db.commit()
        db.refresh(dataset)

        total = len(rows)
        batch_size = 200
        t_db_start = perf_counter()
        for start in range(0, total, batch_size):
            chunk = rows[start:start + batch_size]
            batch = [DatasetRow(
                dataset_id=dataset.id,
                project_id=str(row['projectId']),
                project_name=str(row['projectName']),
                region_name=str(row.get('region')) if row.get('region') is not None else None,
                wave_height=float(row['waveHeight']) if row.get('waveHeight') is not None else None,
                tide_mode=float(row['tideMode']) if row.get('tideMode') is not None else None,
                wind_speed=float(row['windSpeed']) if row.get('windSpeed') is not None else None,
                storm_level=float(row['stormLevel']) if row.get('stormLevel') is not None else None,
                soil_type=float(row['soilType']) if row.get('soilType') is not None else None,
                weak_layer=float(row['weakLayer']) if row.get('weakLayer') is not None else None,
                slide_risk=float(row['slideRisk']) if row.get('slideRisk') is not None else None,
                survey_quality=float(row['surveyQuality']) if row.get('surveyQuality') is not None else None,
                tech_complex=float(row['techComplex']) if row.get('techComplex') is not None else None,
                construction_diff=float(row['constructionDiff']) if row.get('constructionDiff') is not None else None,
                equipment_depend=float(row['equipmentDepend']) if row.get('equipmentDepend') is not None else None,
                tech_error=float(row['techError']) if row.get('techError') is not None else None,
                material_supply=float(row['materialSupply']) if row.get('materialSupply') is not None else None,
                equipment_mobilize=float(row['equipmentMobilize']) if row.get('equipmentMobilize') is not None else None,
                transport_risk=float(row['transportRisk']) if row.get('transportRisk') is not None else None,
                resource_shortage=float(row['resourceShortage']) if row.get('resourceShortage') is not None else None,
                site_manage=float(row['siteManage']) if row.get('siteManage') is not None else None,
                coordination_risk=float(row['coordinationRisk']) if row.get('coordinationRisk') is not None else None,
                schedule_risk=float(row['scheduleRisk']) if row.get('scheduleRisk') is not None else None,
                issue_handling=float(row['issueHandling']) if row.get('issueHandling') is not None else None,
                labor_safety=float(row['laborSafety']) if row.get('laborSafety') is not None else None,
                marine_safety=float(row['marineSafety']) if row.get('marineSafety') is not None else None,
                environment_risk=float(row['environmentRisk']) if row.get('environmentRisk') is not None else None,
                emergency_response=float(row['emergencyResponse']) if row.get('emergencyResponse') is not None else None,
                payload_json=json.dumps(row, ensure_ascii=False),
                risk_score=float(row['riskScore']),
                risk_level=str(row['riskLevel'])
            ) for row in chunk]
            db.bulk_save_objects(batch)
            db.commit()
            percent = 82 + int(((start + len(chunk)) / max(total, 1)) * 17)
            update_job(job_id, status='running', percent=min(percent, 99), message=f'Đã lưu {start + len(chunk)}/{total} dòng dataset')
        t_db = perf_counter() - t_db_start

        result = {
            'jobId': job_id,
            'file_name': file_name,
            'sheet_name': parsed['sheet_name'],
            'dataset_id': dataset.id,
            'validation': {
                'ok': validation['ok'],
                'missing': validation['missing'],
                'count': validation['count'],
                'rowCount': len(rows),
            }
        }
        set_timing(job_id, {
            'kind': 'dataset',
            'parseSeconds': round(t_parse, 4),
            'dbSeconds': round(t_db, 4),
            'totalSeconds': round(perf_counter() - t0, 4),
            'rowCount': len(rows),
            'batchSize': batch_size,
        })
        update_job(job_id, status='done', percent=100, message='Hoàn tất import dataset', result=result)
    except Exception as exc:
        update_job(job_id, status='failed', percent=0, message='Lỗi xử lý dataset', error=str(exc))
    finally:
        db.close()
