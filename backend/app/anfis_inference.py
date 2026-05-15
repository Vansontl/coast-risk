from __future__ import annotations
from typing import Dict
from .anfis_membership import evaluate_membership


def anfis_infer(vector: Dict[str, float], artifact: Dict) -> Dict:
    rules = artifact.get('rules', [])
    details = []
    weights = []
    consequents = []
    for rule in rules:
        mu_values = []
        for key, (_, kind, p1, p2, p3) in rule['inputs'].items():
            mu = evaluate_membership(kind, vector[key], p1, p2, p3)
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
