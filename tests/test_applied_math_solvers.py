"""Tests for Applied Math problem router and rule-based solvers."""

from __future__ import annotations

import unittest

from components.applied_math_problem_router import (
    BASEBALL_TREND,
    INVESTMENT_REBALANCE,
    INVESTMENT_RISK_RETURN,
    NBA_STAT_CHASE,
    GENERIC_FALLBACK,
    GENERIC_INTERACTIVE,
    ProblemRoute,
    route_suite_question,
)
from components.applied_math_solvers import (
    SolverResult,
    dispatch_solver,
    solve_baseball_trend,
    solve_investment_rebalance,
    solve_investment_risk_return,
    solve_nba_stat_chase,
    solve_suite_question,
)


class TestProblemRouter(unittest.TestCase):
    def test_nba_stat_chase_route(self) -> None:
        route = route_suite_question(
            "Will Jalen Brunson pass Allan Houston in playoff rebounds?",
            source_app="nba",
            context={"stat_gap": {"gap": 12, "current_value": 8, "target_value": 20}},
        )
        self.assertEqual(route.problem_type_id, NBA_STAT_CHASE)
        self.assertIn("stat_gap.gap", route.available_fields)

    def test_baseball_trend_route(self) -> None:
        route = route_suite_question(
            "Is Lorenzo Cain's HR trend meaningful?",
            source_app="baseball",
            context={"player": "Lorenzo Cain", "metrics": ["HR"]},
        )
        self.assertEqual(route.problem_type_id, BASEBALL_TREND)
        self.assertIn("trend_summary.slope", route.missing_fields)

    def test_trend_value_page_routes_projection_question(self) -> None:
        route = route_suite_question(
            "What are Ben Rice's expected statistics for 2026 based on these trends?",
            source_app="baseball",
            context={
                "page": "Trend Value",
                "player": "Ben Rice",
                "metrics": ["HR", "OPS"],
                "trend_summary": {"player": "Ben Rice", "stat": "HR", "slope": 1.2, "r2": 0.48},
            },
        )
        self.assertEqual(route.problem_type_id, BASEBALL_TREND)
        self.assertNotEqual(route.problem_type_id, "baseball_player_compare")

    def test_investment_rebalance_route(self) -> None:
        route = route_suite_question(
            "Should I rebalance?",
            source_app="investment",
            context={"rebalance_drift": {"VTI": "+5.0pp"}},
        )
        self.assertEqual(route.problem_type_id, INVESTMENT_REBALANCE)


class TestNbaStatChaseSolver(unittest.TestCase):
    def test_computes_gap_and_required_rate(self) -> None:
        result = solve_nba_stat_chase(
            {
                "stat_gap": {
                    "player": "Jalen Brunson",
                    "comparison": "Allan Houston",
                    "stat": "rebounds",
                    "current_value": 8,
                    "target_value": 20,
                    "gap": 12,
                    "games_remaining": 4,
                }
            },
            "Will Brunson pass Allan Houston in playoff rebounds?",
            games_remaining=4,
            expected_rate=3.0,
        )
        self.assertEqual(result.computed["gap"], 12.0)
        self.assertAlmostEqual(result.computed["required_rate"], 3.0)
        self.assertIn("3.00", result.calculation)
        self.assertIn("Toss-up", result.result)

    def test_conclusion_changes_with_games_remaining(self) -> None:
        ctx = {
            "stat_gap": {
                "player": "Jalen Brunson",
                "comparison": "Allan Houston",
                "stat": "rebounds",
                "gap": 12,
                "current_value": 8,
                "target_value": 20,
            }
        }
        easy = solve_nba_stat_chase(ctx, "pass?", games_remaining=6, expected_rate=3.0)
        hard = solve_nba_stat_chase(ctx, "pass?", games_remaining=2, expected_rate=2.0)
        self.assertAlmostEqual(easy.computed["required_rate"], 2.0)
        self.assertAlmostEqual(hard.computed["required_rate"], 6.0)
        self.assertNotEqual(easy.result, hard.result)

    def test_missing_games_remaining_is_partial(self) -> None:
        result = solve_nba_stat_chase(
            {"stat_gap": {"gap": 12, "current_value": 8, "target_value": 20}},
            "pass?",
        )
        self.assertTrue(result.partial)
        self.assertIn("games_remaining", result.missing_fields[0])


class TestBaseballTrendSolver(unittest.TestCase):
    def test_strong_trend(self) -> None:
        result = solve_baseball_trend(
            {
                "player": "Lorenzo Cain",
                "metrics": ["HR"],
                "trend_summary": {"slope": 1.2, "r2": 0.64, "direction": "up"},
            },
            "Is this trend meaningful?",
            min_slope=0.5,
            min_r2=0.35,
        )
        self.assertTrue(result.computed["meaningful"])
        self.assertEqual(result.computed["strength"], "strong")
        self.assertIn("Meaningful", result.result)

    def test_noisy_trend(self) -> None:
        result = solve_baseball_trend(
            {
                "trend_summary": {"slope": 0.8, "r2": 0.15, "direction": "up"},
            },
            "Is this trend meaningful?",
            min_slope=0.5,
            min_r2=0.35,
        )
        self.assertEqual(result.computed["strength"], "noisy")
        self.assertIn("Noisy", result.result)

    def test_weak_trend(self) -> None:
        result = solve_baseball_trend(
            {
                "trend_summary": {"slope": 0.1, "r2": 0.2, "direction": "flat"},
            },
            "Is this trend meaningful?",
        )
        self.assertEqual(result.computed["strength"], "weak")
        self.assertIn("Weak", result.result)


class TestInvestmentRebalanceSolver(unittest.TestCase):
    def test_overweight_underweight_detection(self) -> None:
        result = solve_investment_rebalance(
            {
                "rebalance_drift": {"VTI": "+6.0pp", "BND": "-4.0pp"},
                "health_score": 70,
            },
            "Should I rebalance?",
            drift_threshold=5.0,
        )
        self.assertEqual(result.computed["overweight"][0], "VTI")
        self.assertEqual(result.computed["underweight"][0], "BND")
        self.assertIn("Rebalance", result.result)

    def test_threshold_monitor(self) -> None:
        result = solve_investment_rebalance(
            {"rebalance_drift": {"VTI": "+3.0pp"}},
            "Should I rebalance?",
            drift_threshold=5.0,
        )
        self.assertIn("Monitor", result.result)


class TestInvestmentRiskReturnSolver(unittest.TestCase):
    def test_sharpe_interpretation(self) -> None:
        result = solve_investment_risk_return(
            {
                "expected_return": 8.0,
                "volatility": 12.0,
                "sharpe_ratio": 0.7,
                "max_drawdown": -18.0,
            },
            "Is this return worth the volatility?",
            min_sharpe=0.5,
            max_volatility=15.0,
        )
        self.assertIn("worth", result.result.lower())
        self.assertIn("0.7", result.calculation)

    def test_high_volatility_warning(self) -> None:
        result = solve_investment_risk_return(
            {"expected_return": 10.0, "volatility": 22.0, "sharpe_ratio": 0.45},
            "Is this return worth the volatility?",
            max_volatility=15.0,
        )
        self.assertIn("exceeds", result.interpretation.lower())


class TestConclusionEngine(unittest.TestCase):
    def test_nba_stat_chase_conclusion_and_sensitivity(self) -> None:
        result = solve_nba_stat_chase(
            {
                "stat_gap": {
                    "player": "Jalen Brunson",
                    "comparison": "Allan Houston",
                    "stat": "rebounds",
                    "gap": 12,
                    "current_value": 8,
                    "target_value": 20,
                    "games_remaining": 4,
                }
            },
            "Will Brunson pass Allan Houston in playoff rebounds?",
            games_remaining=4,
            expected_rate=4.8,
        )
        self.assertIn("probably yes", (result.short_answer or result.conclusion).lower())
        self.assertTrue(result.live_metrics.get("Required rate"))
        self.assertGreaterEqual(result.confidence_pct or 0, 50)
        self.assertTrue(result.reasons)
        self.assertTrue(result.sensitivity_rows)
        self.assertTrue(result.pivot_assumption)

    def test_rebalance_conclusion_yes(self) -> None:
        result = solve_investment_rebalance(
            {"rebalance_drift": {"VTI": "+6.0pp", "BND": "-4.0pp"}},
            "Should I rebalance?",
            drift_threshold=5.0,
        )
        self.assertIn("rebalance", (result.short_answer or result.conclusion).lower())
        self.assertIn("Rebalance", result.live_metrics.get("Action", ""))
        self.assertGreaterEqual(result.confidence_pct or 0, 75)
        self.assertTrue(result.sensitivity_rows)

    def test_player_compare_broad_question(self) -> None:
        route = route_suite_question(
            "Is Soto likely to surpass Judge?",
            source_app="baseball",
            context={"player_a": "Juan Soto", "player_b": "Aaron Judge"},
        )
        # "Surpass" is a forecast question — routes to future accumulation, not static compare.
        from components.applied_math_problem_router import BASEBALL_FUTURE_ACCUMULATION

        self.assertEqual(route.problem_type_id, BASEBALL_FUTURE_ACCUMULATION)
        result = dispatch_solver(
            route,
            "Is Soto likely to surpass Judge?",
            {"player_a": "Juan Soto", "player_b": "Aaron Judge"},
        )
        self.assertTrue(result.live_metrics)
        self.assertIn("project", (result.short_answer or result.conclusion).lower())

    def test_finalize_fills_confidence_from_route(self) -> None:
        route, result = solve_suite_question(
            "Is this trend meaningful?",
            source_app="baseball",
            context={
                "trend_summary": {"slope": 1.2, "r2": 0.64, "direction": "up", "stat": "HR"},
            },
        )
        self.assertIsNotNone(result.confidence_pct)
        self.assertTrue(result.conclusion)


class TestGenericFallback(unittest.TestCase):
    def test_unknown_app_uses_generic(self) -> None:
        route, result = solve_suite_question(
            "What should I do?",
            source_app="unknown",
            context={},
        )
        self.assertIn(route.problem_type_id, (GENERIC_FALLBACK, GENERIC_INTERACTIVE))
        self.assertTrue(result.partial)


class TestDispatch(unittest.TestCase):
    def test_dispatch_matches_route(self) -> None:
        route = route_suite_question(
            "Should I rebalance?",
            source_app="investment",
            context={"rebalance_drift": {"VTI": "+5.0pp"}},
        )
        result = dispatch_solver(route, "Should I rebalance?", {"rebalance_drift": {"VTI": "+5.0pp"}})
        self.assertEqual(result.problem_type_id, INVESTMENT_REBALANCE)

    def test_dispatch_returns_solver_result_not_tuple(self) -> None:
        route = route_suite_question(
            "Should I rebalance?",
            source_app="investment",
            context={"rebalance_drift": {"VTI": "+5.0pp"}},
        )
        out = dispatch_solver(route, "Should I rebalance?", {"rebalance_drift": {"VTI": "+5.0pp"}})
        self.assertIsInstance(out, SolverResult)
        self.assertFalse(isinstance(out, tuple))


class TestResolveSuiteSolver(unittest.TestCase):
    def test_resolve_returns_route_and_solver_result(self) -> None:
        from components.applied_math_solver_ui import resolve_suite_solver

        route, result = resolve_suite_solver(
            "Should I rebalance?",
            source_app="investment",
            context={"rebalance_drift": {"VTI": "+6.0pp", "BND": "-4.0pp"}},
        )
        self.assertEqual(route.problem_type_id, INVESTMENT_REBALANCE)
        self.assertIsInstance(result, SolverResult)
        self.assertIn("Rebalance", result.result)

    def test_solve_suite_question_matches_ui_path(self) -> None:
        route, result = solve_suite_question(
            "Will Jalen Brunson pass Allan Houston in playoff rebounds?",
            source_app="nba",
            context={
                "stat_gap": {
                    "gap": 12,
                    "current_value": 8,
                    "target_value": 20,
                    "games_remaining": 4,
                }
            },
            params={"games_remaining": 4, "expected_rate": 3.0},
        )
        self.assertIsInstance(route, ProblemRoute)
        self.assertIsInstance(result, SolverResult)
        self.assertAlmostEqual(result.computed.get("required_rate"), 3.0)

    def test_rebalance_data_used_capped(self) -> None:
        result = solve_investment_rebalance(
            {
                "rebalance_drift": {"VTI": "+6.0pp", "BND": "-4.0pp", "QQQ": "+8.0pp"},
                "current_weights": {"QQQ": "35.0%", "VTI": "45.0%"},
                "target_weights": {"QQQ": "25.0%", "VTI": "40.0%"},
                "health_score": 78,
                "objective": "Long-term growth",
            },
            "Should I rebalance?",
        )
        self.assertLessEqual(len(result.data_used), 5)
        self.assertIn("drift", result.calculation.lower())
        self.assertNotIn("holdings", " ".join(result.data_used).lower())

    def test_coach_fields_present(self) -> None:
        result = solve_nba_stat_chase(
            {"stat_gap": {"gap": 12, "games_remaining": 4, "current_value": 8, "target_value": 20}},
            "Will Brunson pass?",
            games_remaining=4,
            expected_rate=3.0,
        )
        self.assertTrue(result.math_idea)
        self.assertTrue(result.variables)
        self.assertLessEqual(len(result.data_used), 5)
        from components.applied_math_solver_ui import resolve_suite_solver
        from components.applied_math_solvers import dispatch_solver as real_dispatch
        import components.applied_math_solvers as solvers_mod

        def _boom(*_args, **_kwargs):
            raise RuntimeError("simulated dispatch failure")

        solvers_mod.dispatch_solver = _boom
        try:
            route, result = resolve_suite_solver(
                "Is this trend meaningful?",
                source_app="baseball",
                context={"player": "Test", "metrics": ["HR"]},
            )
            self.assertTrue(result.partial)
            self.assertTrue(result.computed.get("fallback") or "Partial" in (result.result or ""))
        finally:
            solvers_mod.dispatch_solver = real_dispatch


if __name__ == "__main__":
    unittest.main()
