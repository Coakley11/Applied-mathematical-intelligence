"""Answer-quality regression tests for the three real AMI test questions.

These exercise the solver-side (route + solve) with synthetic context that mirrors
what the baseball Trend / Comparison / Draft send hooks produce, so we lock in:

  * trend two-player comparison -> reasoned answer (not a bare "attach data" stub)
  * historical age-window comparison -> correct workflow + age-aware restatement
  * roster weakness -> roster_needs workflow (not a pick-value recommendation)
  * explanation rendering uses real category names (no placeholder "stat (X)")
"""
from __future__ import annotations

import unittest

from components.applied_math_problem_router import (
    BASEBALL_HISTORICAL,
    BASEBALL_PLAYER_COMPARE,
    route_suite_question,
)
from components.applied_math_solvers import (
    _collect_comparison_rows,
    solve_baseball_player_compare,
    solve_suite_question,
)


def _solve(question: str, ctx: dict):
    result = solve_suite_question(question, source_app="baseball", context=ctx)
    return result[1] if isinstance(result, tuple) else result


class TestTrendTwoPlayerComparison(unittest.TestCase):
    Q = "Is Kameron Misner a better pick than Stone Garrett even though he has a lower trend in OPS?"
    CTX = {
        "source_app": "baseball",
        "source_page": "Trend Value",
        "page": "Trend Value",
        "player_a": "Kameron Misner",
        "player_b": "Stone Garrett",
        "players": ["Kameron Misner", "Stone Garrett"],
        "player": "Kameron Misner",
        "trend_comparison_mode": True,
        "metrics": ["OPS"],
    }

    def test_routes_to_player_comparison(self) -> None:
        route = route_suite_question(self.Q, source_app="baseball", context=self.CTX)
        self.assertEqual(route.problem_type_id, BASEBALL_PLAYER_COMPARE)

    def test_restatement_mentions_trends_and_both_players(self) -> None:
        route = route_suite_question(self.Q, source_app="baseball", context=self.CTX)
        r = route.intent_restatement.lower()
        self.assertIn("trend", r)
        self.assertIn("kameron misner", r)
        self.assertIn("stone garrett", r)

    def test_answer_is_reasoned_not_attach_stub(self) -> None:
        res = _solve(self.Q, self.CTX)
        ans = (res.short_answer or "")
        self.assertNotEqual(ans.strip(), "Attach OPS/WAR/HR comparison from the Comparison Tool.")
        self.assertIn("Kameron Misner", ans)
        self.assertIn("Stone Garrett", ans)
        self.assertIn("OPS", ans)

    def test_data_driven_verdict_with_trend_metrics(self) -> None:
        """When per-player trend metrics are attached, give a direct numeric verdict."""
        ctx = dict(self.CTX)
        ctx["trend_comparison"] = {
            "metric": "OPS",
            "player_a": {
                "player": "Kameron Misner",
                "stat_deltas": {"OPS": -0.010, "HR": 1.0, "RBI": 3.0, "R": 2.0, "SB": 1.0},
                "projections": {"OPS": 0.820, "HR": 24, "RBI": 78, "R": 80, "SB": 18},
                "latest_season": {"OPS": 0.830, "HR": 23, "RBI": 75, "R": 78, "SB": 17},
            },
            "player_b": {
                "player": "Stone Garrett",
                "stat_deltas": {"OPS": 0.030, "HR": 2.0, "RBI": 4.0, "R": 1.0, "SB": 0.0},
                "projections": {"OPS": 0.760, "HR": 18, "RBI": 62, "R": 60, "SB": 4},
                "latest_season": {"OPS": 0.730, "HR": 16, "RBI": 58, "R": 57, "SB": 3},
            },
        }
        res = _solve(self.Q, ctx)
        ans = (res.short_answer or "")
        why = (res.why or "")
        # Picks the higher-projection / higher-level player, with numbers, not a tool punt.
        self.assertIn("Kameron Misner", ans)
        self.assertIn("better pick", ans.lower())
        self.assertNotIn("comparison tool", (ans + why).lower())
        self.assertNotIn("open the", (ans + why).lower())
        # References real projected OPS values.
        self.assertTrue("0.82" in ans or "0.83" in ans)


class TestHistoricalAgeComparison(unittest.TestCase):
    Q = "Was Soto a better player than Griffey between ages 19-27?"
    CTX = {
        "source_app": "baseball",
        "source_page": "Comparison Tool",
        "page": "Comparison Tool",
        "player_a": "Soto",
        "player_b": "Griffey",
        "players": ["Soto", "Griffey"],
        "comparison_age_range": "19-27",
        "comparison_constraint_note": "Compare players at ages 19-27 only",
        "historical_comparison": True,
    }

    def test_routes_to_historical(self) -> None:
        route = route_suite_question(self.Q, source_app="baseball", context=self.CTX)
        self.assertEqual(route.problem_type_id, BASEBALL_HISTORICAL)

    def test_restatement_age_aware_not_today(self) -> None:
        route = route_suite_question(self.Q, source_app="baseball", context=self.CTX)
        r = route.intent_restatement.lower()
        self.assertIn("19-27", r)
        self.assertNotIn("better today", r)

    def test_answer_mentions_age_window(self) -> None:
        res = _solve(self.Q, self.CTX)
        self.assertIn("19-27", res.short_answer or "")

    def test_data_driven_verdict_from_significance_tests(self) -> None:
        """With age-filtered significance results attached, give a real category verdict."""
        ctx = dict(self.CTX)
        ctx["significance_tests"] = [
            {"stat": "HR", "winner": "Griffey", "significance": "Significant", "interpretation": ""},
            {"stat": "SLG", "winner": "Griffey", "significance": "Significant", "interpretation": ""},
            {"stat": "RBI", "winner": "Griffey", "significance": "Borderline", "interpretation": ""},
            {"stat": "OBP", "winner": "Soto", "significance": "Significant", "interpretation": ""},
            {"stat": "BB", "winner": "Soto", "significance": "Significant", "interpretation": ""},
            {"stat": "OVERALL", "winner": "Griffey", "significance": "Significant", "interpretation": ""},
        ]
        ctx["significance_overall"] = {"stat": "OVERALL", "winner": "Griffey", "significance": "Significant"}
        res = _solve(self.Q, ctx)
        ans = (res.short_answer or "")
        why = (res.why or "")
        # Names a winner and the categories each player led — not a "filter the explorer" stub.
        self.assertIn("Griffey", ans)
        self.assertIn("Soto", ans)
        self.assertIn("19-27", ans)
        self.assertNotIn("filter the", (ans + why).lower())
        self.assertNotIn("historical explorer", (ans + why).lower())
        # Mentions a real category that one player led.
        self.assertTrue("HR" in ans or "power" in ans.lower())


class TestRosterWeaknessWorkflow(unittest.TestCase):
    Q = "What is Daniel's biggest statistical and position weakness in this draft?"
    CTX = {
        "source_app": "baseball",
        "source_page": "Draft Assistant Simulator",
        "page": "Draft Assistant Simulator",
        "routing_hint": "roster_needs",
        "draft_mode_hint": "roster_needs",
        "draft_review_team": "Daniel",
        "draft_snapshot": {
            "roster": ["Juan Soto", "Elly De La Cruz"],
            "needed_positions": ["C", "1B", "SP"],
            "current_pick": 6,
            "draft_round": 1,
        },
        "category_diagnostics": [
            {"stat": "SB", "roster_mean": 4.0, "pool_mean": 12.0, "gap_vs_pool_pct": -66.7, "status": "weak"},
            {"stat": "HR", "roster_mean": 28.0, "pool_mean": 22.0, "gap_vs_pool_pct": 27.3, "status": "strong"},
            {"stat": "AVG", "roster_mean": 0.255, "pool_mean": 0.270, "gap_vs_pool_pct": -5.6, "status": "average"},
        ],
    }

    def test_routes_to_roster_needs_not_pick_value(self) -> None:
        route = route_suite_question(self.Q, source_app="baseball", context=self.CTX)
        self.assertEqual(route.problem_type, "Roster needs")

    def test_answer_identifies_weakest_category(self) -> None:
        res = _solve(self.Q, self.CTX)
        text = (res.short_answer or "") + " " + (res.why or "")
        # SB is the weakest category (-66.7%) and must be surfaced, not a player pick.
        self.assertIn("SB", text)
        self.assertNotIn("Ichiro", text)

    def test_no_invented_weakness_when_all_categories_positive(self) -> None:
        """If every category is at/above the pool, do not fabricate a statistical weakness."""
        ctx = dict(self.CTX)
        ctx["category_diagnostics"] = [
            {"stat": "SB", "gap_vs_pool_pct": 8.0, "status": "strong"},
            {"stat": "HR", "gap_vs_pool_pct": 27.3, "status": "strong"},
            {"stat": "AVG", "gap_vs_pool_pct": 3.2, "status": "average"},
        ]
        res = _solve(self.Q, ctx)
        text = (res.short_answer or "") + " " + (res.why or "")
        low = text.lower()
        # Must NOT label any of these (positive-gap) categories as the weakest.
        self.assertNotIn("weakest scoring category", low)
        self.assertNotRegex(text, r"-\d+(\.\d+)?%")  # no negative gap percentage printed
        self.assertTrue(
            "no statistical" in low or "no major statistical" in low,
            msg=f"expected a no-weakness statement, got: {text}",
        )
        # Should redirect to positional scarcity.
        self.assertIn("position", low)


class TestComparisonExplanationQuality(unittest.TestCase):
    def test_no_placeholder_stat_label(self) -> None:
        """Unnamed comparison rows must adopt real metric names, never 'stat'."""
        ctx = {
            "player_a": "Griffey",
            "player_b": "Soto",
            "metrics": ["HR", "RBI", "OPS"],
            "comparison_differences": ["120 vs 95", "115 vs 90", "0.91 vs 0.95"],
        }
        rows = _collect_comparison_rows(ctx, "Griffey", "Soto")
        names = [r[0] for r in rows]
        self.assertNotIn("stat", names)
        self.assertEqual(names, ["HR", "RBI", "OPS"])

    def test_why_uses_real_categories(self) -> None:
        ctx = {
            "player_a": "Griffey",
            "player_b": "Soto",
            "metrics": ["HR", "RBI", "OPS"],
            "comparison_differences": ["120 vs 95", "115 vs 90", "0.85 vs 0.95"],
        }
        res = solve_baseball_player_compare(ctx, "Is Griffey better than Soto?")
        why = res.why or ""
        self.assertNotIn("stat (", why)
        # At least one real category name should appear in the reasoning.
        self.assertTrue(any(cat in why for cat in ("HR", "RBI", "OPS")), why)


if __name__ == "__main__":
    unittest.main()
