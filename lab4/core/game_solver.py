"""
Модуль игр: принятие решений в условиях неопределенности.

Три классических критерия для выбора количества операторов:
  - Вальд (максимин): пессимистический, фокус на худшем случае
  - Гурвиц (альфа-критерий): взвешенный оптимизм/пессимизм
  - Байес (ожидаемое значение): использует вероятности сценариев
"""

import numpy as np
from typing import List, Tuple

from core.queue_math import calculate_mm_c_metrics


def build_cost_matrix(
    lambda_scenarios: List[float],
    strategies: List[int],
    mu: float,
    salary_per_op: float,
    penalty_factor: float,
) -> np.ndarray:
    """Построение матрицы затрат для игры с природой."""
    rows = len(strategies)
    cols = len(lambda_scenarios)
    matrix = np.zeros((rows, cols))

    for i, c in enumerate(strategies):
        for j, lam in enumerate(lambda_scenarios):
            metrics = calculate_mm_c_metrics(lam, mu, c)
            penalty = penalty_factor * metrics.p_wait
            matrix[i, j] = c * salary_per_op + penalty

    return matrix


def apply_wald(matrix: np.ndarray) -> Tuple[int, float]:
    """Критерий Вальда: выбор стратегии с минимальными затратами в худшем случае."""
    worst_case = matrix.max(axis=1)
    best_idx = int(np.argmin(worst_case))
    return best_idx, float(worst_case[best_idx])


def apply_hurwicz(matrix: np.ndarray, alpha: float) -> Tuple[int, float]:
    """Критерий Гурвица: H(стратегия) = alpha * лучший + (1 - alpha) * худший."""
    if not (0.0 <= alpha <= 1.0):
        raise ValueError("alpha должно быть в [0, 1]")
    best_case = matrix.min(axis=1)
    worst_case = matrix.max(axis=1)
    hurwicz = alpha * best_case + (1.0 - alpha) * worst_case
    best_idx = int(np.argmin(hurwicz))
    return best_idx, float(hurwicz[best_idx])


def apply_bayes(matrix: np.ndarray, probabilities: List[float]) -> Tuple[int, float]:
    """Критерий Байеса: минимизация ожидаемых затрат."""
    probs = np.array(probabilities, dtype=float)
    if not np.isclose(probs.sum(), 1.0, atol=1e-3):
        raise ValueError("Вероятности сценариев должны в сумме давать 1.0")
    if np.any(probs < 0):
        raise ValueError("Все вероятности должны быть неотрицательными")

    expected = matrix @ probs
    best_idx = int(np.argmin(expected))
    return best_idx, float(expected[best_idx])


def full_analysis(
    lambda_scenarios: List[float],
    strategies: List[int],
    mu: float,
    salary_per_op: float,
    penalty_factor: float,
    probabilities: List[float],
    alpha: float = 0.6,
) -> dict:
    """Запуск всех трех критериев и возврат результатов."""
    matrix = build_cost_matrix(
        lambda_scenarios, strategies, mu, salary_per_op, penalty_factor
    )

    wald_idx, wald_val = apply_wald(matrix)
    hurwicz_idx, hurw_val = apply_hurwicz(matrix, alpha)
    bayes_idx, bayes_val = apply_bayes(matrix, probabilities)

    return {
        "matrix": matrix,
        "wald": {"c": strategies[wald_idx], "cost": wald_val},
        "hurwicz": {"c": strategies[hurwicz_idx], "cost": hurw_val, "alpha": alpha},
        "bayes": {
            "c": strategies[bayes_idx],
            "cost": bayes_val,
            "probs": probabilities,
        },
    }
