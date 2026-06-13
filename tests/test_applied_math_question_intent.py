"""Tests for question-intent classification and intent-aware routing."""

from __future__ import annotations

import unittest

from components.applied_math_problem_router import (
    BASEBALL_DRAFT,
    BASEBALL_FUTURE_ACCUMULATION,
    BASEBALL_PLAYER_COMPARE,
    INVESTMENT_DRAWDOWN_ATTRIBUTION,
    INVESTMENT_MACRO,
    route_suite_question,
)
from components.applied_math_question_intent import (
    INTENT_WHY,
    INTENT_WILL_HAPPEN,
    INTENT_WHO_IS_BETTER,
    INTENT_WHAT_IF,
    classify_question_intent,
)
from components.applied_math_solvers import (
    solve_baseball_future_accumulation,
    solve_investment_drawdown_attribution,
    solve_suite_question,
)


class TestQuestionIntent(unittest.TestCase):
    def test_soto_runs_forecast_intent(self) -> None:
        q = (
            "Do you think Juan Soto will continue to be better in runs scored "
            "than Judge over the next 10 seasons based on this chart?"
        )
        intent = classify_question_intent(q)
        self.assertEqual(intent.intent_id, INTENT_WILL_HAPPEN)
        self.assertIn("10", intent.horizon)

    def test_vti_drawdown_why_intent(self) -> None:
        intent = classify_question_intent("Why did VTI create drawdown risk for my portfolio?")
        self.assertEqual(intent.intent_id, INTENT_WHY)

    def test_recession_what_if_intent(self) -> None:
        intent = classify_question_intent("How sensitive is this portfolio to recession assumptions?")
        self.assertEqual(intent.intent_id, INTENT_WHAT_IF)

    def test_concentrated_not_macro_topic(self) -> None:
        from components.applied_math_problem_router import _topics

        self.assertNotIn("macro", _topics("Is the portfolio too concentrated?"))


class TestIntentRouting(unittest.TestCase):
    def test_soto_judge_routes_future_not_compare(self) -> None:
        q = (
            "Do you think Juan Soto will continue to be better in runs scored "
            "than Judge over the next 10 seasons?"
        )
        route = route_suite_question(
            q,
            source_app="baseball",
            context={
                "player_a": "Juan Soto",
                "player_b": "Aaron Judge",
                "_ami_comparison_context": {
                    "Runs": "Soto 95 vs Judge 110",
                    "Age": "Soto 26 vs Judge 32",
                },
            },
        )
        self.assertEqual(route.problem_type_id, BASEBALL_FUTURE_ACCUMULATION)
        self.assertEqual(route.question_intent, INTENT_WILL_HAPPEN)

    def test_next_catcher_routes_draft_despite_likely_intent(self) -> None:
        q = "Who is likely to be the next catcher picked in this draft?"
        ctx = {
            "draft_snapshot": {
                "current_pick": 7,
                "available_players": [
                    {"player": "Cal Raleigh", "Primary Position": "C", "Market Rank": 35},
                    {"player": "William Contreras", "Primary Position": "C", "Market Rank": 40},
                ],
                "canonical_drafted_players": ["Cal Raleigh"],
            },
            "player_a": "Julio Rodriguez",
            "player_b": "Aaron Judge",
            "_ami_comparison_context": {"HR": "Julio 30 vs Judge 40"},
        }
        intent = classify_question_intent(q)
        self.assertEqual(intent.intent_id, INTENT_WILL_HAPPEN)
        route = route_suite_question(q, source_app="baseball", context=ctx)
        self.assertEqual(route.problem_type_id, BASEBALL_DRAFT)
        self.assertNotEqual(route.problem_type_id, BASEBALL_FUTURE_ACCUMULATION)

    def test_static_compare_still_routes_compare(self) -> None:
        route = route_suite_question(
            "Was Soto better than Judge?",
            source_app="baseball",
            context={"player_a": "Juan Soto", "player_b": "Aaron Judge"},
        )
        self.assertEqual(route.problem_type_id, BASEBALL_PLAYER_COMPARE)
        self.assertEqual(route.question_intent, INTENT_WHO_IS_BETTER)

    def test_vti_drawdown_routes_attribution(self) -> None:
        route = route_suite_question(
            "Why did VTI create drawdown risk for my portfolio?",
            source_app="investment",
            context={"current_weights": {"VTI": "45%", "BND": "55%"}, "max_drawdown": -18.0},
        )
        self.assertEqual(route.problem_type_id, INVESTMENT_DRAWDOWN_ATTRIBUTION)
        self.assertEqual(route.question_intent, INTENT_WHY)

    def test_recession_routes_macro_not_attribution(self) -> None:
        route = route_suite_question(
            "How sensitive is this portfolio to recession assumptions?",
            source_app="investment",
            context={"expected_return": 8.0, "volatility": 12.0},
        )
        self.assertEqual(route.problem_type_id, INVESTMENT_MACRO)


class TestIntentSolvers(unittest.TestCase):
    def test_future_accumulation_younger_can_win(self) -> None:
        result = solve_baseball_future_accumulation(
            {
                "player_a": "Juan Soto",
                "player_b": "Aaron Judge",
                "_ami_comparison_context": {
                    "Runs": "Soto 95 vs Judge 110",
                    "Age": "Soto 26 vs Judge 32",
                },
            },
            "Will Soto score more runs over the next 10 seasons?",
            seasons_a=10,
            seasons_b=7,
        )
        self.assertIn("projects", result.short_answer.lower())
        self.assertTrue(result.live_metrics)
        self.assertIn("accumulation", result.math_idea.lower())

    def test_drawdown_attribution_cause_first(self) -> None:
        result = solve_investment_drawdown_attribution(
            {"current_weights": {"VTI": "45%", "BND": "55%"}, "max_drawdown": -18.0},
            "Why did VTI create drawdown risk for my portfolio?",
        )
        self.assertIn("VTI", result.short_answer)
        self.assertIn("45", result.short_answer)
        self.assertIn("attribution", result.math_idea.lower())
        self.assertIn("what-if", result.calculation.lower())

    def test_suite_soto_question_end_to_end(self) -> None:
        _, result = solve_suite_question(
            "Do you think Juan Soto will continue to be better in runs scored than Judge over the next 10 seasons?",
            source_app="baseball",
            context={
                "player_a": "Juan Soto",
                "player_b": "Aaron Judge",
                "_ami_comparison_context": {"Runs": "Soto 95 vs Judge 110", "Age": "Soto 26 vs Judge 32"},
            },
        )
        self.assertTrue(result.intent_restatement)
        self.assertNotIn("weighted comparison", result.math_idea.lower())


if __name__ == "__main__":
    unittest.main()
