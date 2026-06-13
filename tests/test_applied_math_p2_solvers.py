"""P2 solvers — draft pick and matchup edge."""

from __future__ import annotations

import unittest

from components.applied_math_problem_router import BASEBALL_DRAFT, NBA_MATCHUP_EDGE, route_suite_question
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
