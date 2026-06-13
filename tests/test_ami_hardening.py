"""AMI hardening tests — routing and solver modes for question families."""

from __future__ import annotations

import unittest

from components.applied_math_problem_router import (
    BASEBALL_DRAFT,
    BASEBALL_HISTORICAL,
    BASEBALL_PLAYER_COMPARE,
    BASEBALL_TREND,
    BASEBALL_VALUATION,
    route_suite_question,
)
from components.applied_math_solvers import (
    dispatch_solver,
    solve_baseball_draft,
    solve_baseball_valuation,
)


class TestAmiHardeningFamilies(unittest.TestCase):
    def _draft_ctx(self) -> dict:
        return {
            "draft_snapshot": {
                "current_pick": 6,
                "user_roster": ["Juan Soto", "Elly De La Cruz"],
                "recommended_players": [{"player": "Cal Raleigh", "Primary Position": "C"}],
                "available_players": [{"player": "Bobby Witt Jr.", "Primary Position": "SS", "SB": 50}],
                "category_needs": ["SB", "HR"],
                "needed_positions": ["C", "SS"],
            },
            "category_needs": ["SB", "HR"],
            "needed_positions": ["C", "SS"],
        }

    def test_steals_priority_routes_draft_category_mode(self) -> None:
        ctx = self._draft_ctx()
        route = route_suite_question(
            "Should I prioritize steals right now based on my draft?",
            source_app="baseball",
            context=ctx,
        )
        self.assertEqual(route.problem_type_id, BASEBALL_DRAFT)
        result = solve_baseball_draft(ctx, "Should I prioritize steals right now based on my draft?")
        self.assertEqual(result.computed.get("draft_mode"), "category")

    def test_hitter_pitcher_mode(self) -> None:
        ctx = self._draft_ctx()
        result = solve_baseball_draft(ctx, "Should I take a hitter or pitcher?")
        self.assertEqual(result.computed.get("draft_mode"), "hitter_pitcher")
        self.assertIn("hitter", result.short_answer.lower())

    def test_valuation_routes_with_snapshot(self) -> None:
        ctx = {
            "page": "Valuation",
            "player": "Junior Caminero",
            "valuation_snapshot": {
                "selected_player": "Junior Caminero",
                "top_valuation_players": [
                    {"player": "Junior Caminero", "Valuation_Score": 0.84, "Perf_Score": 72, "Trend_Score": 14},
                ],
            },
        }
        route = route_suite_question("Is this player overvalued or undervalued?", source_app="baseball", context=ctx)
        self.assertEqual(route.problem_type_id, BASEBALL_VALUATION)
        result = solve_baseball_valuation(ctx, "Is this player overvalued or undervalued?")
        self.assertIn("valuation", result.short_answer.lower())

    def test_trend_with_summary_beats_future_accumulation(self) -> None:
        ctx = {
            "page": "Trend Value",
            "player": "Junior Caminero",
            "metrics": ["2B"],
            "trend_summary": {"player": "Junior Caminero", "stat": "2B", "slope": 1.8, "r2": 0.55},
        }
        route = route_suite_question(
            "This player has a good trend. Is he likely to do well next season in doubles?",
            source_app="baseball",
            context=ctx,
        )
        self.assertEqual(route.problem_type_id, BASEBALL_TREND)

    def test_historical_routes_with_snapshot(self) -> None:
        ctx = {
            "page": "Historical Explorer",
            "player": "Barry Bonds",
            "filters_applied": "Years 2000–2007; sort HR",
            "historical_snapshot": {
                "sort_stat": "HR",
                "top_rows": [{"player": "Barry Bonds", "HR": 73}],
            },
        }
        route = route_suite_question(
            "Why does Barry Bonds keep showing up with these filters?",
            source_app="baseball",
            context=ctx,
        )
        self.assertEqual(route.problem_type_id, BASEBALL_HISTORICAL)

    def test_compare_power_routes(self) -> None:
        ctx = {
            "page": "Comparison Tool",
            "player_a": "Juan Soto",
            "player_b": "Aaron Judge",
            "comparison_stats": ["HR"],
        }
        route = route_suite_question(
            "Which player is more valuable for power?",
            source_app="baseball",
            context=ctx,
        )
        self.assertEqual(route.problem_type_id, BASEBALL_PLAYER_COMPARE)


if __name__ == "__main__":
    unittest.main()
