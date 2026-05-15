from __future__ import annotations
import json
import random
from math import sqrt, exp
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np


def clamp_likert(value: float) -> float:
    return max(1.0, min(5.0, round(float(value), 2)))


def map_wave_height_to_likert(value: float) -> float:
    n = float(value or 0)
    if n < 1: return 1
    if n < 2: return 2
    if n < 3: return 3
    if n < 4: return 4
    return 5


def map_wind_speed_to_likert(value: float) -> float:
    n = float(value or 0)
    if n < 6: return 1
    if n < 10: return 2
    if n < 14: return 3
    if n < 18: return 4
    return 5


def map_weak_layer_to_likert(value: float) -> float:
    n = float(value or 0)
    if n < 2: return 1
    if n < 5: return 2
    if n < 10: return 3
    if n < 20: return 4
    return 5


def avg(values: List[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def build_grouped_vector(row: Dict) -> Dict[str, float]:
    x1 = avg([
        map_wave_height_to_likert(row.get('waveHeight')),
        clamp_likert(row.get('tideMode')),
        map_wind_speed_to_likert(row.get('windSpeed')),
        clamp_likert(row.get('stormLevel')),
    ])
    x2 = avg([
        clamp_likert(row.get('soilType')),
        map_weak_layer_to_likert(row.get('weakLayer')),
        clamp_likert(row.get('slideRisk')),
        clamp_likert(row.get('surveyQuality', 3)),
    ])
    x3 = avg([clamp_likert(row.get('techComplex')), clamp_likert(row.get('constructionDiff')), clamp_likert(row.get('equipmentDepend')), clamp_likert(row.get('techError'))])
    x4 = avg([clamp_likert(row.get('materialSupply')), clamp_likert(row.get('equipmentMobilize')), clamp_likert(row.get('transportRisk')), clamp_likert(row.get('resourceShortage'))])
    x5 = avg([clamp_likert(row.get('siteManage')), clamp_likert(row.get('coordinationRisk')), clamp_likert(row.get('scheduleRisk')), clamp_likert(row.get('issueHandling'))])
    x6 = avg([clamp_likert(row.get('laborSafety')), clamp_likert(row.get('marineSafety')), clamp_likert(row.get('environmentRisk')), clamp_likert(row.get('emergencyResponse'))])
    return {'X1': round(x1, 4), 'X2': round(x2, 4), 'X3': round(x3, 4), 'X4': round(x4, 4), 'X5': round(x5, 4), 'X6': round(x6, 4)}


def split_rows(rows: List[Dict], split_ratio: float) -> Tuple[List[Dict], List[Dict]]:
    items = rows[:]
    random.Random(42).shuffle(items)
    split_index = max(1, round(len(items) * split_ratio))
    train = items[:split_index]
    test = items[split_index:]
    if not test and len(train) > 1:
        test = [train.pop()]
    return train, test


def split_train_val_test(rows: List[Dict], train_ratio: float = 0.7, val_ratio: float = 0.15) -> Tuple[List[Dict], List[Dict], List[Dict]]:
    items = rows[:]
    random.Random(42).shuffle(items)
    n = len(items)
    train_end = max(1, round(n * train_ratio))
    val_end = min(n, train_end + max(1, round(n * val_ratio)))
    train = items[:train_end]
    val = items[train_end:val_end]
    test = items[val_end:]
    if not val and len(train) > 1:
        val = [train.pop()]
    if not test and len(val) > 1:
        test = [val.pop()]
    elif not test and len(train) > 1:
        test = [train.pop()]
    return train, val, test


def calculate_metrics(actuals: List[float], preds: List[float]) -> Dict[str, float]:
    n = len(actuals)
    mae = sum(abs(a - p) for a, p in zip(actuals, preds)) / n
    rmse = sqrt(sum((a - p) ** 2 for a, p in zip(actuals, preds)) / n)
    mean_actual = sum(actuals) / n
    ss_res = sum((a - p) ** 2 for a, p in zip(actuals, preds))
    ss_tot = sum((a - mean_actual) ** 2 for a in actuals)
    r2 = 0.0 if ss_tot == 0 else 1 - ss_res / ss_tot
    return {'mae': round(mae, 6), 'rmse': round(rmse, 6), 'r2': round(r2, 6)}


def parse_payload_json(payload_json: str | None) -> Dict:
    if not payload_json:
        return {}
    return json.loads(payload_json)


def gaussian_membership(x: float, center: float, sigma: float) -> float:
    sigma = max(float(sigma), 0.1)
    return exp(-((float(x) - float(center)) ** 2) / (2 * sigma ** 2))


def build_default_anfis_rules() -> List[Dict]:
    return [
        {'name': 'R1', 'inputs': {'X1': ('high', 4.2, 0.9), 'X2': ('high', 4.0, 0.9), 'X5': ('high', 4.1, 0.9)}, 'coeffs': {'X1': 0.36, 'X2': 0.32, 'X5': 0.32}, 'bias': 0.0},
        {'name': 'R2', 'inputs': {'X3': ('high', 4.1, 0.9), 'X4': ('high', 4.0, 0.9), 'X6': ('high', 4.0, 0.9)}, 'coeffs': {'X3': 0.35, 'X4': 0.30, 'X6': 0.35}, 'bias': 0.0},
        {'name': 'R3', 'inputs': {'X1': ('medium', 3.0, 0.8), 'X3': ('high', 4.0, 0.9), 'X6': ('high', 4.0, 0.9)}, 'coeffs': {'X1': 0.25, 'X3': 0.38, 'X6': 0.37}, 'bias': 0.0},
        {'name': 'R4', 'inputs': {'X2': ('high', 4.0, 0.9), 'X4': ('medium', 3.0, 0.8), 'X5': ('high', 4.0, 0.9)}, 'coeffs': {'X2': 0.34, 'X4': 0.28, 'X5': 0.38}, 'bias': 0.0},
    ]


def anfis_infer(vector: Dict[str, float], artifact: Dict) -> Dict:
    rules = artifact.get('rules', [])
    details = []
    weights = []
    consequents = []
    for rule in rules:
        mu_values = []
        for key, (_, center, sigma) in rule['inputs'].items():
            mu = gaussian_membership(vector[key], center, sigma)
            mu_values.append(mu)
        weight = 1.0
        for mu in mu_values:
            weight *= mu
        consequent = sum(rule['coeffs'].get(k, 0.0) * vector.get(k, 0.0) for k in rule['coeffs']) + rule.get('bias', 0.0)
        weights.append(weight)
        consequents.append(consequent)
        details.append({'rule': rule['name'], 'weight': weight, 'consequent': consequent})
    total_weight = sum(weights) or 1e-9
    normalized = [w / total_weight for w in weights]
    output = sum(wb * f for wb, f in zip(normalized, consequents))
    for detail, wb in zip(details, normalized):
        detail['normalized_weight'] = wb
    return {'score': round(output, 4), 'details': details}


def fit_rule_premise(rule: Dict, train_rows: List[Dict], epoch_factor: float = 1.0) -> Dict:
    if not train_rows:
        return rule
    for key, value in list(rule['inputs'].items()):
        label, center, sigma = value
        samples = [float(row['vector'].get(key, center)) for row in train_rows if row.get('vector') and key in row['vector']]
        if not samples:
            continue
        arr = np.array(samples, dtype=float)
        mean = float(np.mean(arr))
        std = float(np.std(arr))
        if label == 'high':
            target_center = max(center, mean)
        elif label == 'medium':
            target_center = (center + mean) / 2
        else:
            target_center = mean
        new_center = center + (target_center - center) * epoch_factor
        target_sigma = max(0.35, std if std > 0 else sigma)
        new_sigma = sigma + (target_sigma - sigma) * epoch_factor
        rule['inputs'][key] = (label, round(new_center, 6), round(new_sigma, 6))
    return rule


def fit_rule_consequents(rule: Dict, train_rows: List[Dict]) -> Dict:
    feature_keys = list(rule['coeffs'].keys())
    if not train_rows:
        return rule
    X = []
    y = []
    for row in train_rows:
        vector = row['vector']
        X.append([float(vector.get(k, 0.0)) for k in feature_keys] + [1.0])
        y.append(float(row['riskScore']))
    X_arr = np.array(X, dtype=float)
    y_arr = np.array(y, dtype=float)
    try:
        beta, *_ = np.linalg.lstsq(X_arr, y_arr, rcond=None)
        for idx, key in enumerate(feature_keys):
            rule['coeffs'][key] = round(float(beta[idx]), 6)
        rule['bias'] = round(float(beta[-1]), 6)
        rule['status'] = 'Learned'
    except Exception:
        rule['status'] = 'Fallback'
    return rule


def dataset_loss(rows: List[Dict], artifact: Dict) -> float:
    if not rows:
        return 0.0
    errors = []
    for row in rows:
        pred = anfis_infer(row['vector'], artifact)['score']
        errors.append((float(row['riskScore']) - pred) ** 2)
    return float(np.mean(errors)) if errors else 0.0


def serialize_rules(rules: List[Dict]) -> List[Dict]:
    return json.loads(json.dumps(rules, ensure_ascii=False))


def train_anfis_artifact(train_rows: List[Dict], test_rows: List[Dict] | None = None, epochs: int = 5, patience: int = 2) -> Dict:
    rules = build_default_anfis_rules()
    history = []
    epoch_snapshots = []
    artifact = {'type': 'ANFIS-Sugeno', 'membership': 'gaussian', 'rules': rules}
    best_snapshot = None
    best_test_loss = None
    best_epoch = 0
    no_improve = 0

    for epoch in range(1, epochs + 1):
        epoch_factor = epoch / epochs
        learned_rules = []
        for rule in rules:
            rule = fit_rule_premise(rule, train_rows, epoch_factor=epoch_factor)
            rule = fit_rule_consequents(rule, train_rows)
            learned_rules.append(rule)
        artifact = {
            'type': 'ANFIS-Sugeno',
            'membership': 'gaussian',
            'rules': learned_rules,
        }
        train_loss = dataset_loss(train_rows, artifact)
        test_loss = dataset_loss(test_rows or [], artifact)
        history.append({'epoch': epoch, 'train_loss': round(train_loss, 6), 'test_loss': round(test_loss, 6)})
        snapshot = {'epoch': epoch, 'rules': serialize_rules(learned_rules)}
        epoch_snapshots.append(snapshot)

        if best_test_loss is None or test_loss < best_test_loss:
            best_test_loss = test_loss
            best_snapshot = snapshot
            best_epoch = epoch
            no_improve = 0
        else:
            no_improve += 1

        rules = learned_rules
        if no_improve >= patience:
            break

    final_rules = best_snapshot['rules'] if best_snapshot else rules
    artifact = {
        'type': 'ANFIS-Sugeno',
        'membership': 'gaussian',
        'rules': final_rules,
        'history': history,
        'epochs': len(history),
        'epoch_snapshots': epoch_snapshots,
        'best_epoch': best_epoch,
        'best_test_loss': round(best_test_loss, 6) if best_test_loss is not None else None,
        'early_stopped': no_improve >= patience,
    }
    return artifact


def save_model_artifact(artifact_dir: str, model_name: str, artifact: Dict) -> str:
    out_dir = Path(artifact_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f'{model_name}.json'
    path.write_text(json.dumps(artifact, ensure_ascii=False, indent=2), encoding='utf-8')
    return str(path)


def load_model_artifact(path: str | None) -> Dict:
    if not path:
        raise FileNotFoundError('Model artifact path missing')
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f'Model artifact not found: {path}')
    return json.loads(file_path.read_text(encoding='utf-8'))
