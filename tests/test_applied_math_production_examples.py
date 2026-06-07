"""Tests for Applied Math build marker and production example flows."""

from __future__ import annotations

import unittest

from applied_math_build_info import (
    SOLVER_BUILD_MARKER,
    SOLVER_UI_VERSION,
    build_info_lines,
)
from components.applied_math_problem_router import (
    BASEBALL_PLAYER_COMPARE,
    BASEBALL_TREND,
    INVESTMENT_REBALANCE,
    NBA_STAT_CHASE,
    route_suite_question,
)
from components.applied_math_solvers import (
    dispatch_solver,
    solve_baseball_trend,
    solve_investment_rebalance,
    solve_nba_stat_chase,
)


class TestBuildInfo(unittest.TestCase):
    def test_build_marker_present(self) -> None:
        self.assertTrue(SOLVER_BUILD_MARKER)
        self.assertTrue(SOLVER_UI_VERSION)
        lines = build_info_lines()
        self.assertGreaterEqual(len(lines), 5)
        self.assertTrue(any("build marker" in ln for ln in lines))


class TestProductionExamples(unittest.TestCase):
    def test_nba_brunson_stat_chase(self) -> None:
        route = route_suite_question(
            "Will Brunson pass Allan Houston in playoff rebounds?",
            source_app="nba",
            context={
                "stat_gap": {
                    "player": "Jalen Brunson",
                    "comparison": "Allan Houston",
                    "stat": "rebounds",
                    "gap": 12,
                    "current_value": 8,
                    "target_value": 20,
                    "games_remaining": 4,
                    "rate_needed": 4.8,
                }
            },
        )
        self.assertEqual(route.problem_type_id, NBA_STAT_CHASE)
        result = solve_nba_stat_chase(
            {
                "stat_gap": {
                    "gap": 12,
                    "games_remaining": 4,
                    "current_value": 8,
                    "target_value": 20,
                }
            },
            "Will Brunson pass Allan Houston in playoff rebounds?",
            games_remaining=4,
            expected_rate=4.8,
        )
        self.assertTrue(result.conclusion)
        self.assertIsNotNone(result.confidence_pct)
        self.assertTrue(result.reasons)
        self.assertAlmostEqual(result.computed["required_rate"], 3.0)

    def test_baseball_cain_trend(self) -> None:
        route = route_suite_question(
            "Is Lorenzo Cain's HR trend meaningful?",
            source_app="baseball",
            context={
                "player": "Lorenzo Cain",
                "metrics": ["HR"],
                "trend_summary": {"slope": 1.2, "r2": 0.64, "direction": "up", "stat": "HR"},
            },
        )
        self.assertEqual(route.problem_type_id, BASEBALL_TREND)
        result = solve_baseball_trend(
            {
                "player": "Lorenzo Cain",
                "metrics": ["HR"],
                "trend_summary": {"slope": 1.2, "r2": 0.64, "direction": "up", "stat": "HR"},
            },
            "Is Lorenzo Cain's HR trend meaningful?",
        )
        self.assertIn("meaningful", result.conclusion.lower())
        self.assertTrue(result.reasons)
        self.assertTrue(result.sensitivity_rows)

    def test_baseball_noisy_trend_plain_english(self) -> None:
        result = solve_baseball_trend(
            {
                "player": "Lorenzo Cain",
                "metrics": ["HR"],
                "trend_summary": {"slope": 0.8, "r2": 0.15, "direction": "up", "stat": "HR"},
            },
            "Is Lorenzo Cain's HR trend meaningful?",
        )
        self.assertIn("meaningful if", (result.short_answer or result.conclusion).lower())
        self.assertIn("Noisy", result.live_metrics.get("Trend verdict", ""))
        self.assertIn("slope", (result.why or result.reasons[0]).lower())

    def test_investment_rebalance(self) -> None:
        route = route_suite_question(
            "Should I rebalance this portfolio?",
            source_app="investment",
            context={"rebalance_drift": {"VTI": "+6.0pp", "BND": "-4.0pp"}},
        )
        self.assertEqual(route.problem_type_id, INVESTMENT_REBALANCE)
        result = solve_investment_rebalance(
            {"rebalance_drift": {"VTI": "+6.0pp", "BND": "-4.0pp"}},
            "Should I rebalance this portfolio?",
        )
        self.assertIn("rebalance", (result.short_answer or result.conclusion).lower())
        self.assertTrue(result.live_metrics)
        self.assertTrue(result.reasons)

    def test_soto_vs_judge(self) -> None:
        route = route_suite_question(
            "Was Soto better than Judge?",
            source_app="baseball",
            context={"player_a": "Juan Soto", "player_b": "Aaron Judge"},
        )
        self.assertEqual(route.problem_type_id, BASEBALL_PLAYER_COMPARE)
        result = dispatch_solver(
            route,
            "Was Soto better than Judge?",
            {"player_a": "Juan Soto", "player_b": "Aaron Judge"},
        )
        self.assertTrue(result.conclusion)
        self.assertTrue(result.math_idea)
        self.assertTrue(result.data_would_improve)


if __name__ == "__main__":
    unittest.main()
