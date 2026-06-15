"""Tests for draft answer grounding (pick/round, catcher names, head-to-head)."""

from __future__ import annotations

import unittest

from components.applied_math_problem_router import BASEBALL_DRAFT, route_suite_question
from components.applied_math_solvers import solve_baseball_draft, solve_suite_question
from components.draft_market_question import extract_draft_compare_players, is_draft_head_to_head_question


class TestDraftGrounding(unittest.TestCase):
    def test_extract_olson_schwarber_from_question(self) -> None:
        q = "Which player would be better to draft, Matt Olson or Kyle Schwarber?"
        self.assertTrue(is_draft_head_to_head_question(q))
        a, b = extract_draft_compare_players(q)
        self.assertIn("olson", a.lower())
        self.assertIn("schwarber", b.lower())

    def test_catcher_market_names_next_available(self) -> None:
        q = "Who is likely to be the next catcher picked in this draft?"
        ctx = {
            "draft_snapshot": {
                "current_pick": 8,
                "draft_round": 1,
                "available_players": [
                    {"player": "Cal Raleigh", "Primary Position": "C", "Market Rank": 35},
                    {"player": "William Contreras", "Primary Position": "C", "Market Rank": 40},
                    {"player": "Adley Rutschman", "Primary Position": "C", "Market Rank": 50},
                ],
                "drafted_players": ["Cal Raleigh"],
            },
            "drafted_players": ["Cal Raleigh"],
            "current_pick": 8,
            "draft_round": 1,
        }
        result = solve_baseball_draft(ctx, q)
        text = (result.short_answer + " " + result.why).lower()
        self.assertEqual(result.computed.get("draft_mode"), "draft_market_prediction")
        self.assertIn("contreras", text)
        self.assertNotIn("pick 19", text)
        self.assertNotIn("no clear remaining", text)

    def test_missing_pick_does_not_invent_pick_19(self) -> None:
        q = "Who is likely to be the next catcher picked in this draft?"
        ctx = {
            "page": "Draft Assistant Simulator",
            "draft_snapshot": {
                "available_players": [
                    {"player": "William Contreras", "Primary Position": "C", "Market Rank": 40},
                ],
            },
        }
        result = solve_baseball_draft(ctx, q)
        self.assertNotIn("pick 19", result.short_answer.lower())
        self.assertNotIn("round **2**", result.short_answer.lower())

    def test_draft_compare_olson_schwarber_grounded(self) -> None:
        q = "Which player would be better to draft, Matt Olson or Kyle Schwarber?"
        ctx = {
            "draft_snapshot": {
                "current_pick": 8,
                "draft_round": 1,
                "available_players": [
                    {"player": "Matt Olson", "Primary Position": "1B", "Market Rank": 30, "Fantasy Edge": 22},
                    {"player": "Kyle Schwarber", "Primary Position": "OF", "Market Rank": 18, "Fantasy Edge": 12},
                ],
            },
            "player_a": "Matt Olson",
            "player_b": "Kyle Schwarber",
            "current_pick": 8,
            "draft_round": 1,
            "needed_positions": ["1B"],
        }
        route = route_suite_question(q, source_app="baseball", context=ctx)
        self.assertEqual(route.problem_type_id, BASEBALL_DRAFT)
        _, result = solve_suite_question(q, source_app="baseball", context=ctx)
        text = (result.short_answer + " " + result.why).lower()
        self.assertEqual(result.computed.get("draft_mode"), "draft_player_compare")
        self.assertIn("olson", text)
        self.assertIn("schwarber", text)
        self.assertNotIn("juan soto", text)

    def test_jose_ramirez_missing_pick_seed_controls_no_crash(self) -> None:
        """Regression: UI seed controls crashed on current_pick=None (deployed fallback)."""
        from components.applied_math_solver_ui import _seed_control_defaults

        q = "Why is Jose Ramirez the best player to draft for me right now?"
        ctx = {
            "page": "Draft Assistant",
            "player": "Jose Ramirez",
            "recommendations": [
                {"Player": "Jose Ramirez", "Market Rank": 12, "Fantasy Edge": 2.1, "Primary Position": "3B"},
            ],
            "available_players": [
                {"Player": "Jose Ramirez", "Primary Position": "3B", "Market Rank": 12},
            ],
            "roster": ["Player A", "Player B"],
        }
        route, result = solve_suite_question(q, source_app="baseball", context=ctx)
        self.assertEqual(route.problem_type_id, BASEBALL_DRAFT)
        self.assertNotIn("current_pick", result.default_controls)
        self.assertFalse(result.computed.get("fallback"))

        class _St:
            pass

        st = _St()
        st.session_state = {}
        params = _seed_control_defaults(st, route, result.default_controls)
        self.assertIn("current_pick", params)
        self.assertEqual(params["current_pick"], 18)
        self.assertIn("ramirez", (result.short_answer or "").lower())
        self.assertNotIn("pick 19", (result.short_answer or "").lower())


if __name__ == "__main__":
    unittest.main()
