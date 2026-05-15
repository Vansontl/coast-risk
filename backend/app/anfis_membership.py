from __future__ import annotations
from math import exp
import numpy as np


def gaussian_membership(x: float, center: float, sigma: float) -> float:
    sigma = max(float(sigma), 0.1)
    return exp(-((float(x) - float(center)) ** 2) / (2 * sigma ** 2))


def gaussian_derivatives(x: float, center: float, sigma: float) -> tuple[float, float, float]:
    sigma = max(float(sigma), 0.1)
    x = float(x)
    mu = gaussian_membership(x, center, sigma)
    dmu_dc = mu * ((x - float(center)) / (sigma ** 2))
    dmu_dsigma = mu * (((x - float(center)) ** 2) / (sigma ** 3))
    return mu, dmu_dc, dmu_dsigma


def generalized_bell_membership(x: float, a: float, b: float, c: float) -> float:
    a = max(float(a), 0.1)
    b = max(float(b), 0.1)
    return 1.0 / (1.0 + abs((float(x) - float(c)) / a) ** (2 * b))


def gbell_derivatives(x: float, a: float, b: float, c: float) -> tuple[float, float, float, float]:
    x = float(x)
    a = max(float(a), 0.1)
    b = max(float(b), 0.1)
    c = float(c)
    eps = 1e-8
    diff = x - c
    abs_ratio = max(abs(diff) / a, eps)
    power = abs_ratio ** (2 * b)
    mu = 1.0 / (1.0 + power)
    common = -1.0 / ((1.0 + power) ** 2)
    dpower_da = -(2 * b / a) * power
    dpower_db = 2 * power * np.log(abs_ratio)
    sign = 0.0 if abs(diff) < eps else (1.0 if diff > 0 else -1.0)
    dpower_dc = -(2 * b / a) * (abs_ratio ** (2 * b - 1)) * sign
    dmu_da = common * dpower_da
    dmu_db = common * dpower_db
    dmu_dc = common * dpower_dc
    return mu, dmu_da, dmu_db, dmu_dc


def triangular_membership(x: float, a: float, b: float, c: float) -> float:
    x = float(x)
    a, b, c = float(a), float(b), float(c)
    if x <= a or x >= c:
        return 0.0
    if x == b:
        return 1.0
    if x < b:
        return (x - a) / max(b - a, 0.1)
    return (c - x) / max(c - b, 0.1)


def triangular_derivatives(x: float, a: float, b: float, c: float) -> tuple[float, float, float, float]:
    x = float(x)
    a, b, c = float(a), float(b), float(c)
    left_span = max(b - a, 0.1)
    right_span = max(c - b, 0.1)
    if x <= a or x >= c or x == b:
        return triangular_membership(x, a, b, c), 0.0, 0.0, 0.0
    if x < b:
        mu = (x - a) / left_span
        dmu_da = (x - b) / (left_span ** 2)
        dmu_db = -(x - a) / (left_span ** 2)
        dmu_dc = 0.0
        return mu, dmu_da, dmu_db, dmu_dc
    mu = (c - x) / right_span
    dmu_da = 0.0
    dmu_db = (c - x) / (right_span ** 2)
    dmu_dc = (x - b) / (right_span ** 2)
    return mu, dmu_da, dmu_db, dmu_dc


def evaluate_membership(kind: str, x: float, p1: float, p2: float, p3: float | None = None) -> float:
    kind = (kind or 'gaussian').lower()
    if kind == 'gbell':
        return generalized_bell_membership(x, p1, p2, p3 if p3 is not None else p1)
    if kind == 'triangular':
        return triangular_membership(x, p1, p2, p3 if p3 is not None else p2)
    return gaussian_membership(x, p1, p2)
