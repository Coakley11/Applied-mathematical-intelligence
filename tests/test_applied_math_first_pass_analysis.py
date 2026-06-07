"""Tests for rule-based first-pass Applied Math analysis."""

from __future__ import annotations

import unittest

from components.applied_math_first_pass_analysis import analyze_suite_question


class TestAppliedMathFirstPassAnalysis(unittest.TestCase):
    def test_trend_uses_slope_and_r2_from_context(self) -> None:
        analysis = analyze_suite_question(
            "Is this trend meaningful?",
            source_app="baseball",
            context={
                "player": "Lorenzo Cain",
                "metrics": ["HR"],
                "trend_summary": {"direction": "up", "slope": 1.2, "r2": 0.64},
            },
        )
        self.assertIn("1.2", analysis.answer)
        self.assertIn("0.64", analysis.answer)
        self.assertEqual(analysis.data_needed, [])

    def test_trend_notes_missing_data(self) -> None:
        analysis = analyze_suite_question(
            "Is this trend meaningful?",
            source_app="baseball",
            context={"player": "Lorenzo Cain", "metrics": ["HR"]},
        )
        self.assertTrue(analysis.data_needed)
        self.assertIn("season-by-season", analysis.answer.lower())

    def test_nba_stat_gap_uses_structured_context(self) -> None:
        analysis = analyze_suite_question(
            "Will Jalen Brunson pass Allan Houston in playoff rebounds?",
            source_app="nba",
            context={
                "stat_gap": {
                    "player": "Jalen Brunson",
                    "comparison": "Allan Houston",
                    "summary": "Gap: 12 rebounds; Brunson 8, Houston 20",
                },
                "games_remaining": 4,
                "rate_needed": "3.0 RPG",
            },
        )
        self.assertIn("4", analysis.answer)
        self.assertIn("3.0 RPG", analysis.answer)
        self.assertIn("Gap: 12", analysis.answer)

    def test_investment_macro_forward_note(self) -> None:
        analysis = analyze_suite_question(
            "How risky is my portfolio given macro?",
            source_app="investment",
            context={
                "health_score": 75,
                "holdings": ["VTI", "BND"],
                "macro_outlook": "Recession 30%",
                "context_note_forward": "macro affects forward only",
                "context_note_historical": "return/vol are historical",
            },
        )
        self.assertIn("forward", analysis.assumptions[0].lower())
        self.assertIn("historical", analysis.answer.lower())


if __name__ == "__main__":
    unittest.main()
