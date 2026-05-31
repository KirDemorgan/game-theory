"""
Тесты для модуля game_solver.
"""

import numpy as np
import pytest
from core.game_solver import (
    build_cost_matrix,
    apply_wald,
    apply_hurwicz,
    apply_bayes,
    full_analysis,
)

LAMBDAS = [20.0, 50.0, 85.0]
STRATEGIES = [3, 5, 7, 9, 11]
MU = 12.0
SALARY = 35.0
PENALTY = 150.0
PROBS = [0.3, 0.5, 0.2]


@pytest.fixture
def cost_matrix():
    return build_cost_matrix(LAMBDAS, STRATEGIES, MU, SALARY, PENALTY)


class TestBuildCostMatrix:

    def test_shape(self, cost_matrix):
        assert cost_matrix.shape == (len(STRATEGIES), len(LAMBDAS))

    def test_all_positive(self, cost_matrix):
        assert np.all(cost_matrix >= 0)

    def test_more_operators_increase_salary_cost(self):
        mat = build_cost_matrix([0.0], STRATEGIES, MU, SALARY, penalty_factor=0.0)
        for i in range(len(STRATEGIES) - 1):
            assert mat[i + 1, 0] > mat[i, 0]

    def test_higher_lambda_increases_cost(self, cost_matrix):
        idx_c5 = STRATEGIES.index(5)
        assert cost_matrix[idx_c5, 2] >= cost_matrix[idx_c5, 0]

    def test_enough_operators_cap_penalty(self):
        mat = build_cost_matrix([20.0], [20], MU, SALARY, PENALTY)
        m = mat[0, 0]
        assert abs(m - 20 * SALARY) < 1.0


class TestWald:

    def test_returns_tuple(self, cost_matrix):
        result = apply_wald(cost_matrix)
        assert isinstance(result, tuple) and len(result) == 2

    def test_index_in_range(self, cost_matrix):
        idx, _ = apply_wald(cost_matrix)
        assert 0 <= idx < len(STRATEGIES)

    def test_pessimistic_picks_minimax(self, cost_matrix):
        idx, val = apply_wald(cost_matrix)
        worst_cases = cost_matrix.max(axis=1)
        assert val == pytest.approx(worst_cases[idx], abs=1e-6)
        assert val == pytest.approx(worst_cases.min(), abs=1e-6)

    def test_consistent_with_manual(self, cost_matrix):
        worst = cost_matrix.max(axis=1)
        expected_idx = int(np.argmin(worst))
        idx, val = apply_wald(cost_matrix)
        assert idx == expected_idx
        assert abs(val - worst[expected_idx]) < 1e-9


class TestHurwicz:

    def test_alpha_zero_equals_wald(self, cost_matrix):
        wald_idx, _ = apply_wald(cost_matrix)
        hurw_idx, _ = apply_hurwicz(cost_matrix, alpha=0.0)
        assert wald_idx == hurw_idx

    def test_alpha_one_optimistic(self, cost_matrix):
        idx, val = apply_hurwicz(cost_matrix, alpha=1.0)
        best = cost_matrix.min(axis=1)
        assert idx == int(np.argmin(best))

    def test_alpha_midpoint(self, cost_matrix):
        idx, val = apply_hurwicz(cost_matrix, alpha=0.6)
        assert 0 <= idx < len(STRATEGIES)
        assert val > 0

    def test_invalid_alpha_raises(self, cost_matrix):
        with pytest.raises(ValueError):
            apply_hurwicz(cost_matrix, alpha=1.5)
        with pytest.raises(ValueError):
            apply_hurwicz(cost_matrix, alpha=-0.1)


class TestBayes:

    def test_uniform_probs(self, cost_matrix):
        uniform = [1.0 / len(LAMBDAS)] * len(LAMBDAS)
        idx, val = apply_bayes(cost_matrix, uniform)
        expected_costs = cost_matrix @ np.array(uniform)
        assert idx == int(np.argmin(expected_costs))
        assert abs(val - expected_costs[idx]) < 1e-9

    def test_custom_probs(self, cost_matrix):
        idx, val = apply_bayes(cost_matrix, PROBS)
        assert 0 <= idx < len(STRATEGIES)

    def test_probs_not_summing_to_one_raises(self, cost_matrix):
        with pytest.raises(ValueError):
            apply_bayes(cost_matrix, [0.3, 0.3, 0.3])

    def test_negative_prob_raises(self, cost_matrix):
        with pytest.raises(ValueError):
            apply_bayes(cost_matrix, [-0.1, 0.6, 0.5])


class TestFullAnalysis:

    def test_returns_all_keys(self):
        result = full_analysis(LAMBDAS, STRATEGIES, MU, SALARY, PENALTY, PROBS)
        assert "matrix" in result
        assert "wald" in result
        assert "hurwicz" in result
        assert "bayes" in result

    def test_all_recommended_c_in_strategies(self):
        result = full_analysis(LAMBDAS, STRATEGIES, MU, SALARY, PENALTY, PROBS)
        for key in ("wald", "hurwicz", "bayes"):
            assert result[key]["c"] in STRATEGIES

    def test_hurwicz_alpha_stored(self):
        result = full_analysis(
            LAMBDAS, STRATEGIES, MU, SALARY, PENALTY, PROBS, alpha=0.7
        )
        assert result["hurwicz"]["alpha"] == 0.7
