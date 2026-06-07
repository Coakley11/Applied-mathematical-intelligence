"""Tests for P0/P1 broad-question solver fixes."""

from __future__ import annotations

import unittest

from components.applied_math_problem_router import (
    BASEBALL_PLAYER_COMPARE,
    BASEBALL_PROJECTION,
    INVESTMENT_CONCENTRATION,
    INVESTMENT_MACRO,
    NBA_INVERSE_STAT_CHASE,
    NBA_WIN_PROBABILITY,
    route_suite_question,
)
from components.applied_math_solvers import (
    solve_baseball_player_compare,
    solve_baseball_projection_realism,
    solve_investment_concentration,
    solve_investment_macro_stress,
    solve_nba_inverse_stat_chase,
    solve_nba_win_probability,
    solve_suite_question,
)


class TestConcentrationRouting(unittest.TestCase):
    def test_concentrated_routes_to_concentration_not_macro(self) -> None:
        route = route_suite_question(
            "Is the portfolio too concentrated?",
            source_app="investment",
            context={
                "holdings": ["AAPL", "MSFT", "VTI"],
                "current_weights": {"AAPL": "28%", "MSFT": "22%", "VTI": "50%"},
            },
        )
        self.assertEqual(route.problem_type_id, INVESTMENT_CONCENTRATION)

    def test_rate_inside_concentrated_does_not_trigger_macro(self) -> None:
        from components.applied_math_problem_router import _topics

        topics = _topics("Is the portfolio too concentrated?")
        self.assertNotIn("macro", topics)


class TestPlayerCompare(unittest.TestCase):
    def test_judge_leads_when_ops_higher(self) -> None:
        result = solve_baseball_player_compare(
            {
                "player_a": "Juan Soto",
                "player_b": "Aaron Judge",
                "_ami_comparison_context": {
                    "OPS": "Soto 1.02 vs Judge 1.08",
                    "WAR": "Soto 7.2 vs Judge 8.1",
                },
            },
            "Is Soto likely to surpass Judge?",
        )
        self.assertIn("Judge", result.short_answer)
        self.assertGreater(result.computed["score_b"], result.computed["score_a"])


class TestWinProbability(unittest.TestCase):
    def test_reasonableness_verdict_not_echo(self) -> None:
        result = solve_nba_win_probability(
            {"team": "Knicks", "win_probability": "62%"},
            "Is this playoff probability reasonable?",
        )
        self.assertNotEqual(result.short_answer.strip(), "62%")
        self.assertIn("favored", result.short_answer.lower())
        self.assertEqual(result.live_metrics.get("Edge band"), "Solid Edge")

    def test_heavy_favorite_band(self) -> None:
        result = solve_nba_win_probability(
            {"win_probability": "78%"},
            "Is 78% reasonable?",
        )
        self.assertIn("heavy favorite", result.short_answer.lower())


class TestConcentrationSolver(unittest.TestCase):
    def test_hhi_and_verdict(self) -> None:
        result = solve_investment_concentration(
            {
                "current_weights": {"AAPL": "28%", "MSFT": "22%", "VTI": "50%"},
            },
            "Is the portfolio too concentrated?",
            max_single_pct=25.0,
            max_top3_pct=60.0,
        )
        self.assertGreater(result.computed["hhi"], 0)
        self.assertAlmostEqual(result.computed["top1_pct"], 50.0, places=0)
        self.assertIn("exceed", result.short_answer.lower())
        self.assertTrue(result.live_metrics.get("HHI"))


class TestInverseStatChase(unittest.TestCase):
    def test_games_needed(self) -> None:
        result = solve_nba_inverse_stat_chase(
            {
                "stat_gap": {
                    "player": "Jalen Brunson",
                    "comparison": "Allan Houston",
                    "stat": "rebounds",
                    "gap": 24,
                    "current_value": 30,
                    "target_value": 54,
                },
            },
            "How many games would Brunson need to pass Allan Houston?",
            expected_rate=4.0,
        )
        self.assertEqual(result.computed["games_needed"], 6)
        self.assertIn("6", result.short_answer)
        self.assertTrue(result.sensitivity_rows)

    def test_inverse_route(self) -> None:
        route = route_suite_question(
            "How many games would Brunson need to pass Allan Houston in rebounds?",
            source_app="nba",
            context={"stat_gap": {"gap": 24, "current_value": 30, "target_value": 54}},
        )
        self.assertEqual(route.problem_type_id, NBA_INVERSE_STAT_CHASE)


class TestMacroStress(unittest.TestCase):
    def test_scenario_calculation(self) -> None:
        result = solve_investment_macro_stress(
            {
                "expected_return": 8.2,
                "volatility": 12.1,
                "macro_outlook": "Recession probability 30%",
                "health_score": 75,
            },
            "How sensitive is this portfolio to recession assumptions?",
            return_shock=-3.0,
            vol_shock=4.0,
        )
        self.assertAlmostEqual(result.computed["stressed_return"], 5.2, places=1)
        self.assertAlmostEqual(result.computed["stressed_vol"], 16.1, places=1)
        self.assertIn("5.2", result.calculation)
        self.assertTrue(result.live_metrics)


class TestProjectionRealism(unittest.TestCase):
    def test_unlikely_projection(self) -> None:
        route = route_suite_question(
            "Is this projection realistic?",
            source_app="baseball",
            context={
                "player": "Aaron Judge",
                "projection": {"stat": "HR", "projected": 58, "previous": 37, "career_avg": 35},
            },
        )
        self.assertEqual(route.problem_type_id, BASEBALL_PROJECTION)
        result = solve_baseball_projection_realism(
            {
                "player": "Aaron Judge",
                "projection": {"stat": "HR", "projected": 58, "previous": 37, "career_avg": 35},
            },
            "Is this projection realistic?",
        )
        self.assertIn(result.computed["verdict"].lower(), ("aggressive", "unlikely"))
        self.assertTrue(result.live_metrics)


class TestSuiteIntegration(unittest.TestCase):
    def test_concentration_end_to_end(self) -> None:
        route, result = solve_suite_question(
            "Is the portfolio too concentrated?",
            source_app="investment",
            context={"current_weights": {"NVDA": "35%", "VTI": "65%"}},
        )
        self.assertEqual(route.problem_type_id, INVESTMENT_CONCENTRATION)
        self.assertTrue(result.short_answer)
        self.assertTrue(result.default_controls)

    def test_compare_end_to_end(self) -> None:
        route, result = solve_suite_question(
            "Is Soto better than Judge?",
            source_app="baseball",
            context={
                "player_a": "Juan Soto",
                "player_b": "Aaron Judge",
                "_ami_comparison_context": {"OPS": "1.02 vs 1.08"},
            },
        )
        self.assertEqual(route.problem_type_id, BASEBALL_PLAYER_COMPARE)
        self.assertIn("Judge", result.short_answer)


if __name__ == "__main__":
    unittest.main()
