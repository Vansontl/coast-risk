from __future__ import annotations
from typing import Dict, List
import numpy as np


def weighted_fuzzy_score(vector: Dict[str, float]) -> float:
    return float(0.22 * vector['X1'] + 0.18 * vector['X2'] + 0.17 * vector['X3'] + 0.13 * vector['X4'] + 0.17 * vector['X5'] + 0.13 * vector['X6'])


def train_ann_baseline(train_rows: List[Dict]) -> Dict:
    if not train_rows:
        return {'weights': [0.0] * 6, 'bias': 0.0}
    X = []
    y = []
    for row in train_rows:
        v = row['vector']
        X.append([v['X1'], v['X2'], v['X3'], v['X4'], v['X5'], v['X6'], 1.0])
        y.append(float(row['riskScore']))
    X_arr = np.array(X, dtype=float)
    y_arr = np.array(y, dtype=float)
    beta, *_ = np.linalg.lstsq(X_arr, y_arr, rcond=None)
    return {'weights': [float(x) for x in beta[:-1]], 'bias': float(beta[-1])}


def ann_predict(vector: Dict[str, float], artifact: Dict) -> float:
    xs = [vector['X1'], vector['X2'], vector['X3'], vector['X4'], vector['X5'], vector['X6']]
    return float(sum(w * x for w, x in zip(artifact.get('weights', []), xs)) + artifact.get('bias', 0.0))
