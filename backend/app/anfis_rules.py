from __future__ import annotations
from typing import Dict, List
from itertools import product
import numpy as np
from .anfis_membership import evaluate_membership


def _membership_params(membership: str, label: str, center: float, spread: float):
    membership = (membership or 'gaussian').lower()
    center = float(center)
    spread = max(float(spread), 0.35)
    if membership == 'triangular':
        return (label, membership, max(1.0, center - spread), center, min(5.0, center + spread))
    if membership == 'gbell':
        return (label, membership, spread, 2.0, center)
    return (label, membership, center, spread, None)


def build_data_driven_anfis_rules(train_rows: List[Dict], membership: str = 'gaussian', max_rules: int = 4) -> List[Dict]:
    vectors = [row.get('vector') or {} for row in train_rows if row.get('vector')]
    if not vectors:
        return build_default_anfis_rules(membership)
    keys = ['X1', 'X2', 'X3', 'X4', 'X5', 'X6']
    matrix = np.array([[float(v.get(k, 0.0)) for k in keys] for v in vectors], dtype=float)
    n = len(matrix)
    rule_count = max(2, min(max_rules, n))
    quantiles = np.linspace(0, n - 1, rule_count, dtype=int)
    sorted_idx = np.argsort(np.mean(matrix, axis=1))
    selected = matrix[sorted_idx[quantiles]]
    spreads = np.std(matrix, axis=0)
    rules = []
    for idx, proto in enumerate(selected, start=1):
        dominant = np.argsort(proto)[-3:]
        coeff_value = round(1 / 3, 6)
        inputs = {}
        coeffs = {}
        for feature_index in dominant:
            key = keys[int(feature_index)]
            center = float(proto[int(feature_index)])
            spread = float(spreads[int(feature_index)]) if float(spreads[int(feature_index)]) > 0 else 0.5
            label = 'high' if center >= 3.5 else ('low' if center <= 2.5 else 'medium')
            inputs[key] = _membership_params(membership, label, round(center, 6), round(spread, 6))
            coeffs[key] = coeff_value
        rules.append({'name': f'R{idx}', 'inputs': inputs, 'coeffs': coeffs, 'bias': 0.0, 'origin': 'data-driven'})
    return rules


def build_candidate_rule_grid(train_rows: List[Dict], membership: str = 'gaussian') -> List[Dict]:
    vectors = [row.get('vector') or {} for row in train_rows if row.get('vector')]
    if not vectors:
        return build_default_anfis_rules(membership)
    keys = ['X1', 'X2', 'X3', 'X4', 'X5', 'X6']
    matrix = np.array([[float(v.get(k, 0.0)) for k in keys] for v in vectors], dtype=float)
    means = np.mean(matrix, axis=0)
    stds = np.std(matrix, axis=0)
    specs = {}
    for idx, key in enumerate(keys):
        mean = float(means[idx])
        std = max(float(stds[idx]), 0.35)
        specs[key] = {
            'low': _membership_params(membership, 'low', max(1.2, mean - std), std),
            'medium': _membership_params(membership, 'medium', mean, std),
            'high': _membership_params(membership, 'high', min(4.8, mean + std), std),
        }
    candidates = []
    labels = ['low', 'medium', 'high']
    for idx, combo in enumerate(product(labels, repeat=len(keys)), start=1):
        inputs = {key: specs[key][label] for key, label in zip(keys, combo)}
        coeffs = {key: round(1 / len(keys), 6) for key in keys}
        candidates.append({'name': f'CR{idx}', 'inputs': inputs, 'coeffs': coeffs, 'bias': 0.0, 'origin': 'candidate-grid'})
    return candidates


def prune_candidate_rules(candidate_rules: List[Dict], train_rows: List[Dict], max_rules: int = 32, min_mean_weight: float = 0.01) -> List[Dict]:
    if not candidate_rules or not train_rows:
        return candidate_rules[:max_rules]
    scored = []
    for rule in candidate_rules:
        weights = []
        for row in train_rows:
            vector = row.get('vector') or {}
            weight = 1.0
            for key, (_, kind, p1, p2, p3) in rule['inputs'].items():
                weight *= evaluate_membership(kind, float(vector.get(key, 0.0)), p1, p2, p3)
            weights.append(weight)
        mean_weight = float(np.mean(weights)) if weights else 0.0
        scored.append((rule, mean_weight))
    filtered = [item for item in scored if item[1] >= min_mean_weight]
    if not filtered:
        filtered = sorted(scored, key=lambda item: item[1], reverse=True)[:max_rules]
    filtered = sorted(filtered, key=lambda item: item[1], reverse=True)[:max_rules]
    rules = []
    for idx, (rule, score) in enumerate(filtered, start=1):
        rule_copy = {**rule, 'name': f'R{idx}', 'origin': 'pruned-grid', 'mean_weight': round(score, 6)}
        rules.append(rule_copy)
    return rules


def build_default_anfis_rules(membership: str = 'gaussian') -> List[Dict]:
    membership = (membership or 'gaussian').lower()
    if membership == 'triangular':
        return [
            {'name': 'R1', 'inputs': {'X1': ('high', membership, 3.6, 4.4, 5.0), 'X2': ('high', membership, 3.5, 4.2, 5.0), 'X5': ('high', membership, 3.6, 4.3, 5.0)}, 'coeffs': {'X1': 0.36, 'X2': 0.32, 'X5': 0.32}, 'bias': 0.0},
            {'name': 'R2', 'inputs': {'X3': ('high', membership, 3.5, 4.2, 5.0), 'X4': ('high', membership, 3.5, 4.1, 5.0), 'X6': ('high', membership, 3.5, 4.1, 5.0)}, 'coeffs': {'X3': 0.35, 'X4': 0.30, 'X6': 0.35}, 'bias': 0.0},
            {'name': 'R3', 'inputs': {'X1': ('medium', membership, 2.0, 3.0, 4.0), 'X3': ('high', membership, 3.5, 4.2, 5.0), 'X6': ('high', membership, 3.5, 4.1, 5.0)}, 'coeffs': {'X1': 0.25, 'X3': 0.38, 'X6': 0.37}, 'bias': 0.0},
            {'name': 'R4', 'inputs': {'X2': ('high', membership, 3.5, 4.2, 5.0), 'X4': ('medium', membership, 2.0, 3.0, 4.0), 'X5': ('high', membership, 3.6, 4.3, 5.0)}, 'coeffs': {'X2': 0.34, 'X4': 0.28, 'X5': 0.38}, 'bias': 0.0},
        ]
    if membership == 'gbell':
        return [
            {'name': 'R1', 'inputs': {'X1': ('high', membership, 0.9, 2.0, 4.2), 'X2': ('high', membership, 0.9, 2.0, 4.0), 'X5': ('high', membership, 0.9, 2.0, 4.1)}, 'coeffs': {'X1': 0.36, 'X2': 0.32, 'X5': 0.32}, 'bias': 0.0},
            {'name': 'R2', 'inputs': {'X3': ('high', membership, 0.9, 2.0, 4.1), 'X4': ('high', membership, 0.9, 2.0, 4.0), 'X6': ('high', membership, 0.9, 2.0, 4.0)}, 'coeffs': {'X3': 0.35, 'X4': 0.30, 'X6': 0.35}, 'bias': 0.0},
            {'name': 'R3', 'inputs': {'X1': ('medium', membership, 0.8, 2.0, 3.0), 'X3': ('high', membership, 0.9, 2.0, 4.0), 'X6': ('high', membership, 0.9, 2.0, 4.0)}, 'coeffs': {'X1': 0.25, 'X3': 0.38, 'X6': 0.37}, 'bias': 0.0},
            {'name': 'R4', 'inputs': {'X2': ('high', membership, 0.9, 2.0, 4.0), 'X4': ('medium', membership, 0.8, 2.0, 3.0), 'X5': ('high', membership, 0.9, 2.0, 4.0)}, 'coeffs': {'X2': 0.34, 'X4': 0.28, 'X5': 0.38}, 'bias': 0.0},
        ]
    return [
        {'name': 'R1', 'inputs': {'X1': ('high', membership, 4.2, 0.9, None), 'X2': ('high', membership, 4.0, 0.9, None), 'X5': ('high', membership, 4.1, 0.9, None)}, 'coeffs': {'X1': 0.36, 'X2': 0.32, 'X5': 0.32}, 'bias': 0.0},
        {'name': 'R2', 'inputs': {'X3': ('high', membership, 4.1, 0.9, None), 'X4': ('high', membership, 4.0, 0.9, None), 'X6': ('high', membership, 4.0, 0.9, None)}, 'coeffs': {'X3': 0.35, 'X4': 0.30, 'X6': 0.35}, 'bias': 0.0},
        {'name': 'R3', 'inputs': {'X1': ('medium', membership, 3.0, 0.8, None), 'X3': ('high', membership, 4.0, 0.9, None), 'X6': ('high', membership, 4.0, 0.9, None)}, 'coeffs': {'X1': 0.25, 'X3': 0.38, 'X6': 0.37}, 'bias': 0.0},
        {'name': 'R4', 'inputs': {'X2': ('high', membership, 4.0, 0.9, None), 'X4': ('medium', membership, 3.0, 0.8, None), 'X5': ('high', membership, 4.0, 0.9, None)}, 'coeffs': {'X2': 0.34, 'X4': 0.28, 'X5': 0.38}, 'bias': 0.0},
    ]
