"""P2 solvers — draft pick and matchup edge."""

from __future__ import annotations

import unittest

from components.applied_math_problem_router import BASEBALL_DRAFT, BASEBALL_FUTURE_ACCUMULATION, NBA_MATCHUP_EDGE, route_suite_question
from components.applied_math_solvers import (
    dispatch_solver,
    solve_baseball_draft,
    solve_nba_matchup_edge,
    solve_suite_question,
)


class TestDraftPickSolver(unittest.TestCase):
    def test_worth_it_when_adp_later_than_pick(self) -> None:
        result = solve_baseball_draft(
            {
                "player": "Corbin Carroll",
                "draft_projection": "Round 1-2 borderline, ADP 18",
                "draft_round": 2,
                "current_pick": 15,
            },
            "Is this player worth a Round 2 pick?",
            current_pick=15,
            adp=18,
        )
        self.assertIn("worth", result.short_answer.lower())
        self.assertTrue(result.live_metrics)
        self.assertIn("rank_edge", result.computed)
        self.assertGreater(result.computed["rank_edge"], 0)

    def test_avoid_when_reaching(self) -> None:
        result = solve_baseball_draft(
            {"player": "Test Player", "draft_projection": "ADP 40"},
            "Should I draft this player here?",
            current_pick=50,
            adp=40,
        )
        self.assertIn("avoid", result.short_answer.lower())

    def test_who_should_draft_next_uses_roster_context(self) -> None:
        ctx = {
            "draft_snapshot": {
                "current_pick": 18,
                "draft_round": 2,
                "user_roster": ["Aaron Judge", "Juan Soto"],
                "recommended_players": [
                    {"player": "Elly De La Cruz"},
                    {"player": "Corbin Carroll"},
                ],
                "sleepers": [{"player": "Junior Caminero"}],
                "scoring_settings": {"draft_format": "Rotisserie"},
            },
            "current_pick": 18,
            "roster": ["Aaron Judge", "Juan Soto"],
            "recommended_players": ["Elly De La Cruz", "Corbin Carroll"],
            "ami_guidance": "Answer using live draft context",
        }
        result = solve_baseball_draft(ctx, "Who should I draft next?")
        self.assertIn("Elly De La Cruz", result.short_answer)
        self.assertTrue(
            "category" in result.why.lower()
            or "roster" in result.why.lower()
            or "fit" in result.why.lower()
        )
        coach = result.computed.get("coach_sections")
        self.assertIsInstance(coach, dict)
        self.assertIn("key_variables", coach)
        self.assertGreater(len(coach["key_variables"]), 2)

    def test_sleeper_question_explains_uncertainty(self) -> None:
        ctx = {
            "draft_snapshot": {
                "current_pick": 24,
                "draft_round": 2,
                "sleepers": [{"player": "Junior Caminero"}],
            },
            "sleepers": ["Junior Caminero"],
            "player": "Junior Caminero",
        }
        result = solve_baseball_draft(ctx, "How do I think about sleepers?")
        coach = result.computed.get("coach_sections") or {}
        framing = str(coach.get("analyst_framing") or "")
        self.assertTrue("upside" in framing.lower() or "probability" in result.short_answer.lower())

    def test_roster_needs_uses_position_gaps(self) -> None:
        ctx = {
            "draft_snapshot": {
                "current_pick": 6,
                "user_roster": ["Juan Soto", "Elly De La Cruz"],
                "recommended_players": [{"player": "Cal Raleigh", "Primary Position": "C"}],
                "needed_positions": ["C", "SS"],
                "category_needs": ["HR", "SB"],
            },
            "needed_positions": ["C", "SS"],
            "category_needs": ["HR", "SB"],
            "roster": ["Juan Soto", "Elly De La Cruz"],
        }
        result = solve_baseball_draft(ctx, "What does my roster need?")
        self.assertEqual(result.computed.get("draft_mode"), "roster_needs")
        self.assertIn("C", result.short_answer)
        self.assertIn("SS", result.short_answer)
        self.assertNotIn("ADP 2", result.short_answer)

    def test_best_values_ranks_multiple_players(self) -> None:
        ctx = {
            "draft_snapshot": {
                "current_pick": 6,
                "best_available_players": [
                    {"player": "Cal Raleigh", "Fantasy Edge": 7, "Market Rank": 35},
                    {"player": "Bobby Witt Jr.", "Fantasy Edge": -3, "Market Rank": 12},
                ],
                "available_players": [
                    {"player": "Cal Raleigh", "Fantasy Edge": 7},
                    {"player": "Junior Caminero", "Fantasy Edge": 5},
                ],
            },
            "current_pick": 6,
        }
        result = solve_baseball_draft(ctx, "Who are the best values left?")
        self.assertEqual(result.computed.get("draft_mode"), "best_values")
        self.assertIn("Cal Raleigh", result.short_answer)
        self.assertIn("Bobby Witt", result.short_answer)

    def test_sleeper_names_candidate_from_snapshot(self) -> None:
        ctx = {
            "sleepers_snapshot": {
                "sleeper_candidates": [
                    {"player": "Junior Caminero", "Fantasy Edge": 42, "Market Rank": 95},
                ],
                "drafted_exclusions": ["Aaron Judge", "Juan Soto"],
                "roster_needs": ["C", "SS"],
            },
            "sleeper_candidates": ["Junior Caminero"],
        }
        result = solve_baseball_draft(ctx, "Should I take this sleeper?")
        self.assertEqual(result.computed.get("draft_mode"), "sleeper")
        self.assertIn("Junior Caminero", result.short_answer)
        self.assertNotIn("this sleeper", result.short_answer.lower())

    def test_sleeper_ranking_lists_upside_safety_balanced(self) -> None:
        ctx = {
            "routing_hint": "sleeper_ranking",
            "intent": "sleeper_ranking_analysis",
            "sleeper_candidates": [
                {
                    "player": "Nathan Lukes",
                    "Fantasy Edge": 226,
                    "Market Rank": 350,
                    "Model Rank": 120,
                    "ADP": 326,
                    "Expert Std Dev": 10.0,
                    "Current Production Score": 0.72,
                    "Projected OPS": 0.78,
                },
                {
                    "player": "Isaac Collins",
                    "Fantasy Edge": 140,
                    "Market Rank": 280,
                    "Model Rank": 160,
                    "ADP": 270,
                    "Expert Std Dev": 35.0,
                    "Current Production Score": 0.55,
                    "Projected OPS": 0.74,
                },
            ],
        }
        q = "Which sleeper has the best combination of upside and safety?"
        result = solve_baseball_draft(ctx, q)
        self.assertEqual(result.computed.get("draft_mode"), "sleeper_ranking")
        ans = result.short_answer
        self.assertIn("Top upside", ans)
        self.assertIn("Safest", ans)
        self.assertIn("Best balanced", ans)
        self.assertIn("Nathan Lukes", ans)

    def test_player_why_evaluates_named_player_against_board(self) -> None:
        ctx = {
            "question_player": "Jose Ramirez",
            "player": "Jose Ramirez",
            "draft_snapshot": {
                "current_pick": 6,
                "draft_round": 2,
                "user_roster": ["Juan Soto", "Elly De La Cruz"],
                "recommended_players": [
                    {"player": "Cal Raleigh", "Primary Position": "C", "Fantasy Edge": 7},
                    {"player": "Jose Ramirez", "Primary Position": "3B", "Fantasy Edge": 4, "Market Rank": 22},
                ],
                "available_players": [
                    {"player": "Jose Ramirez", "Primary Position": "3B", "Fantasy Edge": 4},
                    {"player": "Bobby Witt Jr.", "Primary Position": "SS"},
                ],
                "canonical_drafted_players": ["Aaron Judge", "Juan Soto", "Corbin Carroll"],
            },
            "needed_positions": ["C", "SS"],
            "category_needs": ["HR", "SB"],
            "draft_status": {"player": "Jose Ramirez", "is_drafted": False, "on_user_roster": False},
            "current_pick": 6,
        }
        result = solve_baseball_draft(
            ctx,
            "Why is Jose Ramirez the best player to draft for me right now?",
        )
        self.assertEqual(result.computed.get("draft_mode"), "player_why")
        self.assertIn("Jose Ramirez", result.short_answer)
        self.assertTrue(
            "cal raleigh" in result.short_answer.lower()
            or "better fit" in result.short_answer.lower()
            or "strong pick" in result.short_answer.lower()
        )

    def test_team_fit_question_anchors_named_player(self) -> None:
        ctx = {
            "question_player": "Eric Wagaman",
            "draft_snapshot": {
                "current_pick": 12,
                "draft_round": 2,
                "user_roster": ["Aaron Judge"],
                "recommended_players": [
                    {"player": "Nathan Lukes", "Fantasy Edge": 226, "Market Rank": 350},
                    {"player": "Eric Wagaman", "Fantasy Edge": 18, "Market Rank": 140, "Primary Position": "1B"},
                ],
                "available_players": [
                    {"player": "Eric Wagaman", "Fantasy Edge": 18, "Market Rank": 140, "Primary Position": "1B"},
                    {"player": "Nathan Lukes", "Fantasy Edge": 226},
                ],
            },
            "needed_positions": ["1B"],
            "category_needs": ["HR"],
            "current_pick": 12,
        }
        q = "Would Eric Wagaman help my team if I draft him?"
        result = solve_baseball_draft(ctx, q)
        self.assertEqual(result.computed.get("draft_mode"), "player_why")
        self.assertIn("Eric Wagaman", result.short_answer)
        self.assertNotIn("Nathan Lukes", result.short_answer.split("Eric Wagaman")[0])

    def test_team_fit_sleeper_question_anchors_named_player(self) -> None:
        ctx = {
            "question_player": "Eric Wagaman",
            "sleepers": [{"player": "Nathan Lukes", "Fantasy Edge": 226}],
            "sleeper_candidates": [
                {"player": "Nathan Lukes", "Fantasy Edge": 226, "Market Rank": 350},
                {"player": "Eric Wagaman", "Fantasy Edge": 18, "Market Rank": 140, "Primary Position": "1B"},
            ],
            "draft_snapshot": {
                "user_roster": ["Aaron Judge"],
                "recommended_players": [
                    {"player": "Nathan Lukes", "Fantasy Edge": 226},
                    {"player": "Eric Wagaman", "Fantasy Edge": 18, "Primary Position": "1B"},
                ],
            },
            "needed_positions": ["1B"],
        }
        q = "Would Eric Wagaman help my fantasy team as a sleeper?"
        result = solve_baseball_draft(ctx, q)
        self.assertEqual(result.computed.get("draft_mode"), "player_why")
        self.assertTrue(result.short_answer.strip().startswith("**Eric Wagaman**"))

    def test_format_need_list_describes_roster_needs(self) -> None:
        from components.applied_math_solvers import _format_need_list

        label = _format_need_list(["C", "1B", "2B", "3B", "SS", "OF"], [])
        self.assertIn("Your roster still has needs", label)
        self.assertNotIn("C/1B/2B", label)

    def test_player_why_comparison_avoids_self_peer(self) -> None:
        ctx = {
            "question_player": "Eric Wagaman",
            "sleepers_snapshot": {"sleeper_candidates": []},
            "draft_snapshot": {
                "user_roster": ["Aaron Judge"],
                "recommended_players": [
                    {"player": "Eric Wagaman", "Fantasy Edge": 202, "Market Rank": 284, "Model Rank": 82},
                    {"player": "Isaac Collins", "Fantasy Edge": 40, "Market Rank": 200, "Model Rank": 160},
                ],
                "available_players": [
                    {"player": "Eric Wagaman", "Fantasy Edge": 202, "Market Rank": 284, "Model Rank": 82},
                    {"player": "Isaac Collins", "Fantasy Edge": 40, "Market Rank": 200, "Model Rank": 160},
                ],
            },
            "needed_positions": ["C", "1B", "2B"],
            "current_pick": 18,
        }
        result = solve_baseball_draft(ctx, "Would Eric Wagaman help my fantasy team as a sleeper?")
        coach = result.computed.get("coach_sections") or {}
        tradeoffs = str(coach.get("tradeoffs") or "")
        self.assertIn("Isaac Collins", tradeoffs)
        self.assertNotIn("Eric Wagaman vs **Eric Wagaman**", tradeoffs)
        self.assertNotIn("vs **Eric Wagaman** trades", tradeoffs)

    def test_projected_rank_control_uses_model_rank(self) -> None:
        ctx = {
            "question_player": "Eric Wagaman",
            "sleeper_candidates": [
                {
                    "player": "Eric Wagaman",
                    "Fantasy Edge": 202,
                    "Market Rank": 284,
                    "Model Rank": 82,
                    "ADP": 284,
                }
            ],
            "draft_snapshot": {
                "recommended_players": [
                    {
                        "player": "Eric Wagaman",
                        "Fantasy Edge": 202,
                        "Market Rank": 284,
                        "Model Rank": 82,
                        "ADP": 284,
                    }
                ],
            },
            "current_pick": 18,
        }
        result = solve_baseball_draft(ctx, "Would Eric Wagaman help my fantasy team as a sleeper?")
        controls = result.default_controls or {}
        self.assertEqual(controls.get("projected_rank"), 82)
        self.assertEqual(int(controls.get("adp", 0)), 284)

    def test_risk_question_mentions_variance(self) -> None:
        ctx = {
            "draft_snapshot": {
                "current_pick": 18,
                "user_roster": ["Aaron Judge"],
                "recommended_players": [{"player": "Corbin Carroll"}],
            },
            "current_pick": 18,
        }
        result = solve_baseball_draft(ctx, "Should I take a risky player?")
        coach = result.computed.get("coach_sections") or {}
        self.assertIn("variance", str(coach.get("analyst_framing") or "").lower())

    def test_draft_routes_with_snapshot_without_projection(self) -> None:
        ctx = {
            "draft_snapshot": {
                "current_pick": 18,
                "recommended_players": [{"player": "Corbin Carroll"}],
            },
            "current_pick": 18,
        }
        route = route_suite_question(
            "Who should I draft next?",
            source_app="baseball",
            context=ctx,
        )
        self.assertEqual(route.problem_type_id, BASEBALL_DRAFT)
        self.assertIn("draft_snapshot", route.available_fields)

    def _draft_market_ctx(self) -> dict:
        return {
            "draft_snapshot": {
                "current_pick": 7,
                "draft_round": 2,
                "my_next_pick": 18,
                "user_roster": ["Juan Soto", "Elly De La Cruz"],
                "canonical_drafted_players": [
                    "Aaron Judge",
                    "Juan Soto",
                    "Corbin Carroll",
                    "Mookie Betts",
                    "Elly De La Cruz",
                    "Cal Raleigh",
                ],
                "available_players": [
                    {"player": "Cal Raleigh", "Primary Position": "C", "Market Rank": 35},
                    {"player": "William Contreras", "Primary Position": "C", "Market Rank": 40},
                    {"player": "Adley Rutschman", "Primary Position": "C", "Market Rank": 50},
                    {"player": "Will Smith", "Primary Position": "C", "Market Rank": 55},
                    {"player": "Bobby Witt Jr.", "Primary Position": "SS", "Market Rank": 12},
                ],
                "recommended_players": [
                    {"player": "William Contreras", "Primary Position": "C", "Market Rank": 40},
                ],
                "needed_positions": ["C", "SS"],
                "position_scarcity": 2.8,
            },
            "player_a": "Julio Rodriguez",
            "player_b": "Aaron Judge",
            "_ami_comparison_context": {"HR": "Julio 30 vs Judge 40"},
            "current_pick": 7,
            "needed_positions": ["C", "SS"],
            "position_scarcity": 2.8,
        }

    def test_next_catcher_routes_draft_not_future_accumulation(self) -> None:
        q = "Who is likely to be the next catcher picked in this draft?"
        ctx = self._draft_market_ctx()
        route = route_suite_question(q, source_app="baseball", context=ctx)
        self.assertEqual(route.problem_type_id, BASEBALL_DRAFT)
        self.assertNotEqual(route.problem_type_id, BASEBALL_FUTURE_ACCUMULATION)

    def test_next_catcher_solver_uses_board_not_comparison(self) -> None:
        q = "Who is likely to be the next catcher picked in this draft?"
        ctx = self._draft_market_ctx()
        result = solve_baseball_draft(ctx, q)
        self.assertEqual(result.computed.get("draft_mode"), "draft_market_prediction")
        low = result.short_answer.lower()
        self.assertIn("cal raleigh", low)
        self.assertIn("william contreras", low)
        self.assertNotIn("julio", low)

    def test_position_run_solver_mode(self) -> None:
        ctx = self._draft_market_ctx()
        result = solve_baseball_draft(ctx, "Which position is likely to run next?")
        self.assertEqual(result.computed.get("draft_mode"), "draft_market_prediction")
        self.assertTrue("run" in result.short_answer.lower() or "catcher" in result.short_answer.lower())

    def test_make_it_back_solver_mode(self) -> None:
        ctx = self._draft_market_ctx()
        ctx["question_player"] = "William Contreras"
        result = solve_baseball_draft(ctx, "Will William Contreras make it back to me?")
        self.assertEqual(result.computed.get("draft_mode"), "draft_timing_decision")
        self.assertIn("William Contreras", result.short_answer)

    def test_contreras_now_or_wait_timing_mode(self) -> None:
        ctx = self._draft_market_ctx()
        ctx["draft_snapshot"]["current_pick"] = 8
        ctx["draft_snapshot"]["draft_round"] = 4
        ctx["draft_snapshot"]["my_next_pick"] = 18
        ctx["current_pick"] = 8
        ctx["draft_round"] = 4
        ctx["question_player"] = "William Contreras"
        result = solve_baseball_draft(
            ctx,
            "Should I select William Contreras as a catcher now or wait for a later round?",
        )
        self.assertEqual(result.computed.get("draft_mode"), "draft_timing_decision")
        low = result.short_answer.lower()
        self.assertNotIn("fair price", low)
        self.assertTrue("now" in low or "wait" in low)
        self.assertIn("contreras", low)
        self.assertIn("round **4**", low)
        self.assertNotIn("should i select", low)
        self.assertTrue("survival" in low or "gone" in low)

    def test_timing_extracts_player_name_not_question(self) -> None:
        from components.applied_math_solvers import _extract_player_from_question_text

        name = _extract_player_from_question_text(
            "Should I select William Contreras as a catcher now or wait for a later round?"
        )
        self.assertEqual(name, "William Contreras")

    def test_timing_extracts_contreras_at_c_for_pick(self) -> None:
        from components.applied_math_solvers import _extract_player_from_question_text

        name = _extract_player_from_question_text(
            "Should I draft William Contreras at C for pick 8 or wait for a later round?"
        )
        self.assertEqual(name, "William Contreras")

    def test_contreras_at_c_timing_surfaces_catcher_pool(self) -> None:
        ctx = self._draft_market_ctx()
        ctx["draft_snapshot"]["current_pick"] = 8
        ctx["draft_snapshot"]["draft_round"] = 4
        ctx["draft_snapshot"]["my_next_pick"] = 18
        ctx["current_pick"] = 8
        ctx["draft_round"] = 4
        ctx["draft_snapshot"]["available_players"].extend(
            [
                {"player": "Shea Langeliers", "Primary Position": "C", "Market Rank": 45},
                {"player": "Salvador Perez", "Primary Position": "C", "Market Rank": 52},
                {"player": "Yainer Diaz", "Primary Position": "C", "Market Rank": 58},
            ]
        )
        result = solve_baseball_draft(
            ctx,
            "Should I draft William Contreras at C for pick 8 or wait for a later round?",
        )
        self.assertEqual(result.computed.get("draft_mode"), "draft_timing_decision")
        low = (result.short_answer + " " + result.why).lower()
        self.assertIn("william contreras", low)
        self.assertNotIn("at c for pick", low)
        self.assertTrue(
            "langeliers" in low or "perez" in low or "diaz" in low or "catcher" in low
        )
        self.assertNotIn("0 position options", low)

    def test_draft_review_uses_round_from_snapshot(self) -> None:
        ctx = self._draft_market_ctx()
        ctx["draft_snapshot"]["current_pick"] = 44
        ctx["draft_snapshot"]["draft_round"] = 4
        ctx["current_pick"] = 44
        ctx["draft_round"] = 4
        ctx["draft_snapshot"]["user_roster"] = [
            "Aaron Judge",
            "Anthony Volpe",
            "Cal Raleigh",
        ]
        ctx["draft_snapshot"]["user_roster_detail"] = [
            {"player": "Aaron Judge", "Primary Position": "OF"},
            {"player": "Anthony Volpe", "Primary Position": "SS"},
            {"player": "Cal Raleigh", "Primary Position": "C"},
        ]
        ctx["draft_snapshot"]["roster_position_index"] = {
            "aaron judge": "OF",
            "anthony volpe": "SS",
            "cal raleigh": "C",
        }
        ctx["player_position_index"] = ctx["draft_snapshot"]["roster_position_index"]
        result = solve_baseball_draft(ctx, "How would you rate my picks so far?")
        self.assertEqual(result.computed.get("draft_mode"), "draft_review")
        self.assertIn("round **4**", result.short_answer.lower())
        self.assertIn("**of**: aaron judge", result.short_answer.lower())
        self.assertIn("**ss**: anthony volpe", result.short_answer.lower())
        self.assertIn("**c**: cal raleigh", result.short_answer.lower())

    def test_catcher_run_solver_mode(self) -> None:
        ctx = self._draft_market_ctx()
        result = solve_baseball_draft(ctx, "Is a catcher run coming?")
        self.assertEqual(result.computed.get("draft_mode"), "draft_market_prediction")
        self.assertIn("catcher", result.short_answer.lower())

    def test_contreras_catcher_why_explains_position_not_overall_rec(self) -> None:
        ctx = self._draft_market_ctx()
        ctx["draft_snapshot"]["recommended_players"] = [
            {"player": "Jose Ramirez", "Primary Position": "3B", "Market Rank": 8, "Fantasy Edge": 12},
            {"player": "Kyle Schwarber", "Primary Position": "OF", "Market Rank": 14, "Fantasy Edge": 10},
            {"player": "Matt Olson", "Primary Position": "1B", "Market Rank": 16, "Fantasy Edge": 9},
        ]
        ctx["draft_snapshot"]["available_players"].extend(
            [
                {"player": "Shea Langeliers", "Primary Position": "C", "Market Rank": 45},
                {"player": "Salvador Perez", "Primary Position": "C", "Market Rank": 52},
            ]
        )
        ctx["question_player"] = "William Contreras"
        q = "Why is William Contreras the best catcher to draft now?"
        result = solve_baseball_draft(ctx, q)
        self.assertEqual(result.computed.get("draft_mode"), "player_why")
        text = (result.short_answer + " " + result.why).lower()
        self.assertIn("william contreras", text)
        self.assertIn("catcher", text)
        self.assertNotIn("jose ramirez is the better fit", text)
        self.assertTrue(
            "langeliers" in text or "perez" in text or "highest-ranked" in text or "sits above" in text
        )

    def test_player_why_catcher_surfaces_drafted_count_in_direct(self) -> None:
        ctx = self._draft_market_ctx()
        ctx["draft_snapshot"]["user_roster"] = ["Juan Soto", "Elly De La Cruz", "Cal Raleigh"]
        ctx["draft_snapshot"]["recommended_players"] = [
            {"player": "Jose Ramirez", "Primary Position": "3B", "Market Rank": 8},
        ]
        ctx["question_player"] = "William Contreras"
        result = solve_baseball_draft(
            ctx,
            "Why is William Contreras the best catcher to draft right now?",
        )
        self.assertEqual(result.computed.get("draft_mode"), "player_why")
        low = result.short_answer.lower()
        self.assertIn("cal raleigh", low)
        self.assertTrue("already drafted" in low or "1" in result.short_answer)
        self.assertIn("highest-ranked", low)

    def test_draft_review_not_fair_price(self) -> None:
        ctx = self._draft_market_ctx()
        ctx["draft_snapshot"]["user_roster"] = [
            "Aaron Judge",
            "Francisco Lindor",
            "Cal Raleigh",
            "Juan Soto",
        ]
        ctx["draft_snapshot"]["current_pick"] = 8
        ctx["current_pick"] = 8
        result = solve_baseball_draft(ctx, "How would you rate my picks so far?")
        self.assertEqual(result.computed.get("draft_mode"), "draft_review")
        low = result.short_answer.lower()
        self.assertIn("grade", low)
        self.assertNotIn("fair price", low)
        self.assertNotIn("jose ramirez at pick", low)

    def test_positions_left_routes_roster_needs(self) -> None:
        ctx = self._draft_market_ctx()
        ctx["draft_snapshot"]["user_roster"] = [
            "Aaron Judge",
            "Anthony Volpe",
            "Cal Raleigh",
        ]
        ctx["draft_snapshot"]["user_roster_detail"] = [
            {"player": "Aaron Judge", "Primary Position": "OF"},
            {"player": "Anthony Volpe", "Primary Position": "SS"},
            {"player": "Cal Raleigh", "Primary Position": "C"},
        ]
        ctx["draft_snapshot"]["roster_position_index"] = {
            "aaron judge": "OF",
            "anthony volpe": "SS",
            "cal raleigh": "C",
        }
        ctx["player_position_index"] = ctx["draft_snapshot"]["roster_position_index"]
        ctx["draft_snapshot"]["needed_positions"] = ["3B", "1B", "OF"]
        ctx["needed_positions"] = ["3B", "1B", "OF"]
        result = solve_baseball_draft(ctx, "What positions do I have left to draft?")
        self.assertEqual(result.computed.get("draft_mode"), "roster_needs")
        low = result.short_answer.lower()
        self.assertIn("3b", low)
        self.assertIn("**of**: aaron judge", low)
        self.assertIn("**ss**: anthony volpe", low)
        self.assertIn("**c**: cal raleigh", low)
        coach = result.computed.get("coach_sections") or {}
        framing = str(coach.get("analyst_framing") or "").lower()
        self.assertIn("3", framing)
        self.assertIn("position groups", framing)
        self.assertNotIn("fair price", low)

    def test_ramirez_vs_contreras_analyst_compare(self) -> None:
        ctx = self._draft_market_ctx()
        ctx["draft_snapshot"]["recommended_players"] = [
            {"player": "Jose Ramirez", "Primary Position": "3B", "Market Rank": 8, "Fantasy Edge": 12},
        ]
        ctx["draft_snapshot"]["available_players"].extend(
            [
                {"player": "Jose Ramirez", "Primary Position": "3B", "Market Rank": 8},
                {"player": "Shea Langeliers", "Primary Position": "C", "Market Rank": 45},
                {"player": "Matt Chapman", "Primary Position": "3B", "Market Rank": 55},
            ]
        )
        result = solve_baseball_draft(
            ctx,
            "Should I draft William Contreras or Jose Ramirez?",
        )
        self.assertEqual(result.computed.get("draft_mode"), "draft_player_compare")
        low = result.short_answer.lower()
        self.assertIn("ramirez", low)
        self.assertTrue(
            "stronger overall" in low or "best remaining" in low or "premium" in low
        )

    def test_best_available_catcher_ranks_pool(self) -> None:
        ctx = self._draft_market_ctx()
        ctx["draft_snapshot"]["available_players"].extend(
            [
                {"player": "Shea Langeliers", "Primary Position": "C", "Market Rank": 45},
                {"player": "Salvador Perez", "Primary Position": "C", "Market Rank": 52},
            ]
        )
        ctx["draft_snapshot"]["draft_room_board"] = [
            {"player": "Cal Raleigh", "Primary Position": "C", "Team": "Team B"},
            {"player": "William Contreras", "Primary Position": "C", "Team": ""},
        ]
        q = "Who is the best available catcher?"
        result = solve_baseball_draft(ctx, q)
        self.assertEqual(result.computed.get("draft_mode"), "position_best_available")
        text = (result.short_answer + " " + result.why).lower()
        self.assertIn("william contreras", text)
        self.assertIn("langeliers", text)
        self.assertIn("cal raleigh", text)
        self.assertNotIn("jose ramirez", text)

    def test_player_why_catcher_no_generic_roster_fit_leak(self) -> None:
        ctx = self._draft_market_ctx()
        ctx["draft_snapshot"]["recommended_players"] = [
            {"player": "Jose Ramirez", "Primary Position": "3B", "Market Rank": 8},
        ]
        ctx["draft_snapshot"]["available_players"].extend(
            [
                {"player": "Shea Langeliers", "Primary Position": "C", "Market Rank": 45, "Fantasy Edge": -8},
                {"player": "Salvador Perez", "Primary Position": "C", "Market Rank": 52, "Fantasy Edge": -12},
            ]
        )
        ctx["draft_snapshot"]["draft_room_board"] = [
            {"player": "Cal Raleigh", "Primary Position": "C"},
        ]
        ctx["question_player"] = "William Contreras"
        result = solve_baseball_draft(
            ctx,
            "Why is William Contreras the best catcher to draft right now?",
        )
        text = (result.short_answer + " " + result.why + " " + str(result.computed.get("coach_sections"))).lower()
        self.assertEqual(result.computed.get("draft_mode"), "player_why")
        self.assertNotIn("that closes 1b/2b", text)
        self.assertNotIn("hr + rbi on your roster", text)
        self.assertTrue("langeliers" in text or "perez" in text or "highest-ranked" in text or "sits above" in text)
        coach = result.computed.get("coach_sections") or {}
        drafted_framing = str(coach.get("analyst_framing") or "").lower()
        self.assertIn("cal raleigh", drafted_framing)

    def test_next_best_catcher_mode(self) -> None:
        ctx = self._draft_market_ctx()
        result = solve_baseball_draft(ctx, "Who is the next best catcher?")
        self.assertEqual(result.computed.get("draft_mode"), "position_best_available")
        self.assertIn("catcher", result.short_answer.lower())

    def test_draft_routes_and_dispatches(self) -> None:
        route = route_suite_question(
            "Is Corbin Carroll worth a Round 2 pick?",
            source_app="baseball",
            context={
                "player": "Corbin Carroll",
                "draft_projection": "ADP 18",
                "draft_round": 2,
                "current_pick": 15,
            },
        )
        self.assertEqual(route.problem_type_id, BASEBALL_DRAFT)
        ctx = {
            "player": "Corbin Carroll",
            "draft_projection": "ADP 18",
            "draft_round": 2,
            "current_pick": 15,
        }
        result = dispatch_solver(route, "Is Corbin Carroll worth a Round 2 pick?", ctx)
        self.assertEqual(result.problem_type_id, BASEBALL_DRAFT)
        self.assertIn("ADP", result.calculation)


class TestMatchupEdgeSolver(unittest.TestCase):
    def test_meaningful_edge_with_probability_and_advantages(self) -> None:
        result = solve_nba_matchup_edge(
            {
                "team": "Knicks",
                "opponent": "Celtics",
                "series_probability": "62%",
                "matchup_advantages": ["Size edge in frontcourt", "Turnover pressure"],
            },
            "Do the Knicks have a real edge?",
            prob_threshold_pp=6.0,
        )
        self.assertIn("edge", result.short_answer.lower())
        self.assertTrue(result.live_metrics)
        self.assertIn("edge_pp", result.computed)

    def test_injury_lowers_edge(self) -> None:
        base = solve_nba_matchup_edge(
            {"team": "Knicks", "opponent": "Celtics", "series_probability": "55%"},
            "Is this matchup edge meaningful?",
            injury_adjustment_pp=0.0,
        )
        hurt = solve_nba_matchup_edge(
            {
                "team": "Knicks",
                "opponent": "Celtics",
                "series_probability": "55%",
                "injury_summary": "Star guard doubtful",
            },
            "How much does injury risk change the matchup?",
            injury_adjustment_pp=10.0,
        )
        self.assertLess(hurt.computed["edge_pp"], base.computed["edge_pp"])

    def test_matchup_routes_and_dispatches(self) -> None:
        ctx = {
            "team": "Knicks",
            "opponent": "Celtics",
            "matchup_advantages": ["Pace advantage"],
            "series_probability": "58%",
        }
        route = route_suite_question(
            "Is this matchup edge meaningful?",
            source_app="nba",
            context=ctx,
        )
        self.assertEqual(route.problem_type_id, NBA_MATCHUP_EDGE)
        result = dispatch_solver(route, "Is this matchup edge meaningful?", ctx)
        self.assertIn("edge", result.math_idea.lower())
        self.assertTrue(result.computed.get("edge_score") is not None)


class TestP2EndToEnd(unittest.TestCase):
    def test_draft_end_to_end(self) -> None:
        _, result = solve_suite_question(
            "Should I wait one more round?",
            source_app="baseball",
            context={"player": "Corbin Carroll", "draft_projection": "ADP 18", "current_pick": 14},
        )
        self.assertTrue(result.short_answer)
        self.assertIn("draft", result.math_idea.lower())

    def test_matchup_paraphrase(self) -> None:
        ctx = {
            "team": "Knicks",
            "opponent": "Celtics",
            "series_probability": "60%",
            "matchup_advantages": ["Frontcourt size"],
        }
        route = route_suite_question(
            "Is this matchup edge meaningful?",
            source_app="nba",
            context=ctx,
        )
        self.assertEqual(route.problem_type_id, NBA_MATCHUP_EDGE)


if __name__ == "__main__":
    unittest.main()
