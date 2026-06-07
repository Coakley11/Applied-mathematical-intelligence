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
