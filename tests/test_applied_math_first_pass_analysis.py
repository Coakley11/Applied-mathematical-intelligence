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
        self.assertIn("trend", analysis.answer.lower())

    def test_nba_stat_gap_uses_structured_context(self) -> None:
        analysis = analyze_suite_question(
            "Will Jalen Brunson pass Allan Houston in playoff rebounds?",
            source_app="nba",
            context={
                "stat_gap": {
                    "player": "Jalen Brunson",
                    "comparison": "Allan Houston",
                    "stat": "rebounds",
                    "current_value": 8,
                    "target_value": 20,
                    "gap": 12,
                    "games_remaining": 4,
                    "rate_needed": "3.0 RPG",
                    "summary": "Gap: 12 rebounds; Brunson 8, Houston 20",
                },
            },
        )
        self.assertIn("4", analysis.answer)
        self.assertIn("3.0", analysis.answer)
        self.assertIn("12", analysis.answer)

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
        self.assertIn("recession", analysis.assumptions[0].lower())
        self.assertTrue(analysis.answer)

    def test_historical_snapshot_used_in_first_pass(self) -> None:
        analysis = analyze_suite_question(
            "Is Mike Trout's 2019 season an outlier?",
            source_app="baseball",
            context={
                "player": "Mike Trout",
                "page": "Historical Explorer",
                "historical_snapshot": {
                    "sort_stat": "HR",
                    "year_range": "2015-2019",
                    "top_rows": [{"player": "Mike Trout", "year": 2019, "HR": 45}],
                },
            },
        )
        self.assertIn("45", analysis.answer)
        self.assertIn("Mike Trout", analysis.answer)

    def test_nba_matchup_uses_advantages(self) -> None:
        analysis = analyze_suite_question(
            "Who wins the series?",
            source_app="nba",
            context={
                "team": "New York Knicks",
                "opponent": "Boston Celtics",
                "workflow": "Matchup intelligence",
                "matchup_advantages": ["Knicks control offensive rebounds"],
                "injury_summary": "Anunoby questionable",
            },
        )
        self.assertIn("edge", analysis.answer.lower())
        self.assertIn("knicks", analysis.answer.lower())

    def test_rebalance_drift_referenced(self) -> None:
        analysis = analyze_suite_question(
            "Should I rebalance?",
            source_app="investment",
            context={
                "rebalance_drift": {"VTI": "+5.0pp"},
                "rebalance_recommendation": ["Trim VTI"],
                "health_score": 70,
            },
        )
        self.assertIn("VTI", analysis.answer)
        self.assertIn("5.0pp", analysis.answer)


if __name__ == "__main__":
    unittest.main()
