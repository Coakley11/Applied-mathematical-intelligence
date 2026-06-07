"""Paraphrase routing — same mathematical intent, different wording."""

from __future__ import annotations

import unittest

from components.applied_math_problem_interpreter import (
    PURPOSE_ATTRIBUTE,
    PURPOSE_FORECAST,
    interpret_suite_question,
)
from components.applied_math_problem_router import (
    BASEBALL_FUTURE_ACCUMULATION,
    BASEBALL_PLAYER_COMPARE,
    BASEBALL_TREND,
    INVESTMENT_DRAWDOWN_ATTRIBUTION,
    INVESTMENT_RISK_RETURN,
    NBA_INVERSE_STAT_CHASE,
    route_suite_question,
)
from components.applied_math_solvers import solve_suite_question

SOTO_JUDGE_CTX = {
    "player_a": "Juan Soto",
    "player_b": "Aaron Judge",
    "_ami_comparison_context": {
        "Runs": "Soto 95 vs Judge 110",
        "Age": "Soto 26 vs Judge 32",
    },
}


class TestParaphraseIntent(unittest.TestCase):
    def test_future_accumulation_paraphrases_same_purpose(self) -> None:
        questions = (
            "Will Soto keep scoring more runs than Judge?",
            "Does Soto project better than Judge over the next decade?",
            "Given the chart, who is more likely to lead in runs going forward?",
            "Do you think Juan Soto will continue to be better in runs scored than Judge over the next 10 seasons?",
        )
        purposes = set()
        for q in questions:
            interp = interpret_suite_question(q, source_app="baseball", context=SOTO_JUDGE_CTX)
            purposes.add(interp.math_purpose)
            self.assertEqual(
                interp.math_purpose,
                PURPOSE_FORECAST,
                msg=f"Expected forecast purpose for: {q}",
            )
        self.assertEqual(len(purposes), 1)

    def test_drawdown_why_paraphrases(self) -> None:
        questions = (
            "Why did VTI create drawdown risk for my portfolio?",
            "Why is VTI exposing me to drawdown?",
            "What would reduce drawdown risk from VTI?",
        )
        for q in questions:
            interp = interpret_suite_question(
                q,
                source_app="investment",
                context={"current_weights": {"VTI": "45%"}},
            )
            self.assertIn(
                interp.math_purpose,
                (PURPOSE_ATTRIBUTE, "explain_why"),
                msg=q,
            )


class TestParaphraseRouting(unittest.TestCase):
    def test_soto_judge_paraphrases_route_future_accumulation(self) -> None:
        paraphrases = (
            "Will Soto keep scoring more runs than Judge?",
            "Does Soto project better than Judge over the next decade?",
            "Given the chart, who is more likely to lead in runs going forward?",
        )
        for q in paraphrases:
            route = route_suite_question(q, source_app="baseball", context=SOTO_JUDGE_CTX)
            self.assertEqual(
                route.problem_type_id,
                BASEBALL_FUTURE_ACCUMULATION,
                msg=f"Wrong route for: {q}",
            )
            self.assertTrue(route.model_name)
            self.assertTrue(route.model_rationale)

    def test_static_compare_not_forecast(self) -> None:
        route = route_suite_question(
            "Was Soto better than Judge last season?",
            source_app="baseball",
            context=SOTO_JUDGE_CTX,
        )
        self.assertEqual(route.problem_type_id, BASEBALL_PLAYER_COMPARE)

    def test_trend_paraphrases(self) -> None:
        ctx = {
            "player": "Lorenzo Cain",
            "trend_summary": {"slope": 0.9, "r2": 0.55},
        }
        for q in (
            "Is Lorenzo Cain's trend meaningful?",
            "Does this player have a real upward trend?",
            "Is this slope significant or just noise?",
        ):
            route = route_suite_question(q, source_app="baseball", context=ctx)
            self.assertEqual(route.problem_type_id, BASEBALL_TREND, msg=q)

    def test_nba_inverse_rate_paraphrase(self) -> None:
        ctx = {
            "stat_gap": {
                "gap": 120,
                "current_value": 880,
                "target_value": 1000,
                "games_remaining": 20,
            },
        }
        for q in (
            "How many games would Brunson need to pass Allan Houston?",
            "How many more games does he need at this pace?",
        ):
            route = route_suite_question(q, source_app="nba", context=ctx)
            self.assertEqual(route.problem_type_id, NBA_INVERSE_STAT_CHASE, msg=q)

    def test_investment_risk_paraphrase(self) -> None:
        ctx = {"expected_return": 9.0, "volatility": 14.0}
        route = route_suite_question(
            "Is this return worth the volatility?",
            source_app="investment",
            context=ctx,
        )
        self.assertEqual(route.problem_type_id, INVESTMENT_RISK_RETURN)


class TestPurposeOverride(unittest.TestCase):
    def test_override_to_comparison(self) -> None:
        q = "Will Soto keep scoring more runs than Judge?"
        route = route_suite_question(
            q,
            source_app="baseball",
            context=SOTO_JUDGE_CTX,
            purpose_override="compare",
        )
        self.assertEqual(route.problem_type_id, BASEBALL_PLAYER_COMPARE)

    def test_override_to_forecast(self) -> None:
        route = route_suite_question(
            "Was Soto better than Judge?",
            source_app="baseball",
            context=SOTO_JUDGE_CTX,
            purpose_override="forecast",
        )
        self.assertEqual(route.problem_type_id, BASEBALL_FUTURE_ACCUMULATION)


class TestGenericInteractiveFallback(unittest.TestCase):
    def test_sparse_context_still_answers(self) -> None:
        _, result = solve_suite_question(
            "Who is more likely to age better?",
            source_app="baseball",
            context={"player_a": "Juan Soto", "player_b": "Aaron Judge"},
        )
        self.assertTrue(result.short_answer)
        self.assertTrue(result.live_metrics)
        self.assertTrue(result.model_name or result.math_purpose)

    def test_interpretation_fields_on_result(self) -> None:
        route, result = solve_suite_question(
            "Will Soto keep scoring more runs than Judge?",
            source_app="baseball",
            context=SOTO_JUDGE_CTX,
        )
        self.assertTrue(result.intent_restatement)
        self.assertTrue(result.model_name)
        self.assertTrue(result.model_rationale)
        self.assertEqual(route.problem_type_id, BASEBALL_FUTURE_ACCUMULATION)


class TestDrawdownAttributionParaphrase(unittest.TestCase):
    def test_vti_why_routes_attribution(self) -> None:
        ctx = {"current_weights": {"VTI": "45%", "BND": "55%"}, "max_drawdown": -18.0}
        route = route_suite_question(
            "Why is this portfolio risky because of VTI?",
            source_app="investment",
            context=ctx,
        )
        self.assertEqual(route.problem_type_id, INVESTMENT_DRAWDOWN_ATTRIBUTION)


if __name__ == "__main__":
    unittest.main()
