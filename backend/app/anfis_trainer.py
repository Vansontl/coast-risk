from __future__ import annotations
import json
from typing import Dict, List
import numpy as np
from .anfis_rules import build_default_anfis_rules, build_data_driven_anfis_rules, build_candidate_rule_grid, prune_candidate_rules
from .anfis_inference import anfis_infer
from .anfis_membership import gaussian_derivatives, gbell_derivatives, triangular_derivatives


def serialize_rules(rules: List[Dict]) -> List[Dict]:
    return json.loads(json.dumps(rules, ensure_ascii=False))


def _clip(value: float, low: float, high: float) -> float:
    return max(low, min(high, float(value)))


def fit_rule_premise(rule: Dict, train_rows: List[Dict], artifact: Dict, epoch_factor: float = 1.0, premise_lr: float = 0.05) -> Dict:
    if not train_rows:
        return rule
    rule_keys = list(rule['inputs'].keys())
    grad_center = {k: [] for k in rule_keys}
    grad_shape = {k: [] for k in rule_keys}
    for row in train_rows:
        pred = anfis_infer(row['vector'], artifact)['score']
        err = float(row['riskScore']) - pred
        for k in rule_keys:
            label, kind, p1, p2, p3 = rule['inputs'][k]
            x = float(row['vector'].get(k, p1))
            ref = p2 if kind == 'triangular' else (p3 if kind == 'gbell' else p1)
            grad_center[k].append(err * (x - ref))
            grad_shape[k].append(err * abs(x - ref))

    for key, value in list(rule['inputs'].items()):
        label, kind, p1, p2, p3 = value
        samples = [float(row['vector'].get(key, p1)) for row in train_rows if row.get('vector') and key in row['vector']]
        if not samples:
            continue
        arr = np.array(samples, dtype=float)
        mean = float(np.mean(arr))
        std = float(np.std(arr)) if float(np.std(arr)) > 0 else 0.5
        center_grad = _clip(float(np.mean(grad_center.get(key) or [0.0])), -10.0, 10.0)
        shape_grad = _clip(float(np.mean(grad_shape.get(key) or [0.0])), -10.0, 10.0)
        center_delta = _clip(premise_lr * center_grad * epoch_factor * 0.005, -0.2, 0.2)
        shape_delta = _clip(premise_lr * shape_grad * epoch_factor * 0.002, -0.15, 0.15)
        if kind == 'triangular':
            d_a = []
            d_b = []
            d_c = []
            for row in train_rows:
                pred = anfis_infer(row['vector'], artifact)['score']
                err = _clip(float(row['riskScore']) - pred, -2.0, 2.0)
                x = float(row['vector'].get(key, p2))
                _, dmu_da, dmu_db, dmu_dc = triangular_derivatives(x, p1, p2, p3)
                d_a.append(_clip(err * dmu_da, -10.0, 10.0))
                d_b.append(_clip(err * dmu_db, -10.0, 10.0))
                d_c.append(_clip(err * dmu_dc, -10.0, 10.0))
            a_grad = _clip(float(np.mean(d_a or [0.0])), -10.0, 10.0)
            b_grad = _clip(float(np.mean(d_b or [0.0])), -10.0, 10.0)
            c_grad = _clip(float(np.mean(d_c or [0.0])), -10.0, 10.0)
            a_step = _clip(premise_lr * a_grad * 0.01, -0.12, 0.12)
            b_step = _clip(premise_lr * b_grad * 0.01, -0.12, 0.12)
            c_step = _clip(premise_lr * c_grad * 0.01, -0.12, 0.12)
            left = _clip(p1 + ((mean - 1.0) - p1) * epoch_factor + a_step, 1.0, 5.0)
            peak = _clip(p2 + (mean - p2) * epoch_factor + b_step, 1.0, 5.0)
            right = _clip(p3 + ((mean + 1.0) - p3) * epoch_factor + c_step, 1.0, 5.0)
            if left > peak:
                left = max(1.0, peak - 0.2)
            if right < peak:
                right = min(5.0, peak + 0.2)
            rule['inputs'][key] = (label, kind, round(left, 6), round(peak, 6), round(right, 6))
        elif kind == 'gbell':
            d_a = []
            d_b = []
            d_c = []
            for row in train_rows:
                pred = anfis_infer(row['vector'], artifact)['score']
                err = _clip(float(row['riskScore']) - pred, -2.0, 2.0)
                x = float(row['vector'].get(key, p3))
                _, dmu_da, dmu_db, dmu_dc = gbell_derivatives(x, p1, p2, p3)
                d_a.append(_clip(err * dmu_da, -10.0, 10.0))
                d_b.append(_clip(err * dmu_db, -10.0, 10.0))
                d_c.append(_clip(err * dmu_dc, -10.0, 10.0))
            a_grad = _clip(float(np.mean(d_a or [0.0])), -10.0, 10.0)
            b_grad = _clip(float(np.mean(d_b or [0.0])), -10.0, 10.0)
            c_grad = _clip(float(np.mean(d_c or [0.0])), -10.0, 10.0)
            a_step = _clip(premise_lr * a_grad * 0.01, -0.1, 0.1)
            b_step = _clip(premise_lr * b_grad * 0.01, -0.1, 0.1)
            c_step = _clip(premise_lr * c_grad * 0.01, -0.15, 0.15)
            a = _clip(p1 + (max(0.35, std) - p1) * epoch_factor + a_step, 0.1, 3.0)
            b = _clip(p2 + b_step, 0.1, 5.0)
            c = _clip(p3 + (mean - p3) * epoch_factor + c_step, 1.0, 5.0)
            rule['inputs'][key] = (label, kind, round(a, 6), round(b, 6), round(c, 6))
        else:
            d_center = []
            d_sigma = []
            for row in train_rows:
                pred = anfis_infer(row['vector'], artifact)['score']
                err = _clip(float(row['riskScore']) - pred, -2.0, 2.0)
                x = float(row['vector'].get(key, p1))
                _, dmu_dc, dmu_dsigma = gaussian_derivatives(x, p1, p2)
                d_center.append(_clip(err * dmu_dc, -10.0, 10.0))
                d_sigma.append(_clip(err * dmu_dsigma, -10.0, 10.0))
            center_grad_exact = _clip(float(np.mean(d_center or [0.0])), -10.0, 10.0)
            sigma_grad_exact = _clip(float(np.mean(d_sigma or [0.0])), -10.0, 10.0)
            center_step = _clip(premise_lr * center_grad_exact * 0.01, -0.15, 0.15)
            sigma_step = _clip(premise_lr * sigma_grad_exact * 0.01, -0.1, 0.1)
            center = _clip(p1 + (mean - p1) * epoch_factor + center_step, 1.0, 5.0)
            sigma = _clip(p2 + (max(0.35, std) - p2) * epoch_factor + sigma_step, 0.1, 3.0)
            rule['inputs'][key] = (label, kind, round(center, 6), round(sigma, 6), None)
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


def train_anfis_artifact(train_rows: List[Dict], val_rows: List[Dict] | None = None, test_rows: List[Dict] | None = None, epochs: int = 5, patience: int = 2, membership: str = 'gaussian', premise_lr: float = 0.05, rule_init_mode: str = 'data-driven') -> Dict:
    rule_init_mode = (rule_init_mode or 'data-driven').lower()
    candidate_rule_count = None
    pruned_rule_count = None
    if rule_init_mode == 'seed':
        rules = build_default_anfis_rules(membership)
    elif rule_init_mode in ('full-grid', 'candidate-grid', 'pruned-grid'):
        candidate_rules = build_candidate_rule_grid(train_rows, membership=membership)
        candidate_rule_count = len(candidate_rules)
        rules = prune_candidate_rules(candidate_rules, train_rows, max_rules=32, min_mean_weight=0.01)
        pruned_rule_count = len(rules)
        rule_init_mode = 'pruned-grid'
    else:
        rules = build_data_driven_anfis_rules(train_rows, membership=membership, max_rules=4)
    history = []
    epoch_snapshots = []
    artifact = {'type': 'ANFIS-Sugeno', 'membership': membership, 'rules': rules}
    best_snapshot = None
    best_test_loss = None
    best_epoch = 0
    no_improve = 0
    for epoch in range(1, epochs + 1):
        epoch_factor = epoch / epochs
        learned_rules = []
        pre_artifact = {'type': 'ANFIS-Sugeno', 'membership': membership, 'rules': rules}
        for rule in rules:
            rule = fit_rule_premise(rule, train_rows, pre_artifact, epoch_factor=epoch_factor, premise_lr=premise_lr)
            rule = fit_rule_consequents(rule, train_rows)
            learned_rules.append(rule)
        artifact = {'type': 'ANFIS-Sugeno', 'membership': membership, 'rules': learned_rules}
        train_loss = dataset_loss(train_rows, artifact)
        val_loss = dataset_loss(val_rows or [], artifact)
        test_loss = dataset_loss(test_rows or [], artifact)
        history.append({'epoch': epoch, 'train_loss': round(train_loss, 6), 'val_loss': round(val_loss, 6), 'test_loss': round(test_loss, 6)})
        premise_snapshot = {}
        for rule in learned_rules:
            premise_snapshot[rule['name']] = {
                key: {'label': value[0], 'kind': value[1], 'p1': value[2], 'p2': value[3], 'p3': value[4]}
                for key, value in rule['inputs'].items()
            }
        snapshot = {'epoch': epoch, 'rules': serialize_rules(learned_rules), 'premise': premise_snapshot}
        epoch_snapshots.append(snapshot)
        compare_loss = val_loss if val_rows else test_loss
        if best_test_loss is None or compare_loss < best_test_loss:
            best_test_loss = compare_loss
            best_snapshot = snapshot
            best_epoch = epoch
            no_improve = 0
        else:
            no_improve += 1
        rules = learned_rules
        if no_improve >= patience:
            break
    final_rules = best_snapshot['rules'] if best_snapshot else rules
    return {'type': 'ANFIS-Sugeno', 'membership': membership, 'premise_lr': premise_lr, 'rule_init': rule_init_mode, 'candidate_rule_count': candidate_rule_count, 'pruned_rule_count': pruned_rule_count or len(final_rules), 'rules': final_rules, 'history': history, 'epochs': len(history), 'epoch_snapshots': epoch_snapshots, 'best_epoch': best_epoch, 'best_test_loss': round(best_test_loss, 6) if best_test_loss is not None else None, 'early_stopped': no_improve >= patience}
