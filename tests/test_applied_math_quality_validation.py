"""Quality validation pass — context arrival and first-pass answer usage."""

from __future__ import annotations

import unittest

from applied_math_quality_validation import (
    VALIDATION_SCENARIOS,
    run_all_validations,
    run_validation_scenario,
)
from suite_analytical_question import analytical_question_continue_copy, build_question_payload


class TestAppliedMathQualityValidation(unittest.TestCase):
    def test_all_scenarios_context_present(self) -> None:
        for scenario in VALIDATION_SCENARIOS:
            result = run_validation_scenario(scenario)
            with self.subTest(scenario=scenario.name):
                self.assertFalse(
                    result.context_missing,
                    msg=f"Missing {result.context_missing} for {scenario.name}",
                )

    def test_trend_answer_uses_slope_and_r2(self) -> None:
        trend = next(s for s in VALIDATION_SCENARIOS if "Trend" in s.name)
        result = run_validation_scenario(trend)
        self.assertTrue(result.answer_uses_context)
        self.assertGreaterEqual(result.quality_rating, 7)

    def test_command_center_card_stays_clean(self) -> None:
        payload = build_question_payload(
            source_app="baseball",
            source_page="Trend Value",
            question="Is the trend meaningful?",
            context={
                "trend_summary": {"slope": 1.2, "r2": 0.64},
                "player": "Lorenzo Cain",
            },
        )
        title, subtitle, _ = analytical_question_continue_copy(payload)
        self.assertIn("Baseball", title)
        self.assertEqual(subtitle, "Is the trend meaningful?")
        self.assertNotIn("slope", subtitle)
        self.assertNotIn("1.2", subtitle)

    def test_validation_summary_report(self) -> None:
        results = run_all_validations()
        self.assertEqual(len(results), len(VALIDATION_SCENARIOS))
        avg = sum(r.quality_rating for r in results) / len(results)
        self.assertGreaterEqual(avg, 6.0, msg="Average quality below threshold — see validation report")


if __name__ == "__main__":
    unittest.main()
