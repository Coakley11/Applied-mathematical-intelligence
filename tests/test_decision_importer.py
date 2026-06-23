"""Tests for AMI Problem Importer — Phase 0 prediction market bets."""

from __future__ import annotations

import tempfile
import unittest
import unittest.mock
from pathlib import Path

from decision_history import delete_import_entry, list_import_history, save_import_entry
from decision_math import analyze_prediction_market_bet, enrich_bet_fields, solve_decision
from decision_parser import extract_fields, parse_prediction_market_csv, parse_prediction_market_text
from decision_router import route_imported_problem
from decision_templates import assess_completeness


KALSHI_SAMPLE = """
Will the Knicks make the 2026 NBA playoffs?
Yes: 42¢
No: 58¢
Expires: April 15, 2026
Rules: Resolves Yes if Knicks clinch a playoff berth.
"""

CSV_SAMPLE = """title,side,price,stake,user_probability
Knicks playoffs,Yes,42,100,55
"""


class TestDecisionRouter(unittest.TestCase):
    def test_routes_kalshi_text_to_prediction_market(self) -> None:
        route = route_imported_problem(KALSHI_SAMPLE)
        self.assertEqual(route["decision_type"], "prediction_market_bet")
        self.assertGreater(route["confidence"], 0.3)

    def test_empty_defaults_to_prediction_market_phase0(self) -> None:
        route = route_imported_problem("")
        self.assertEqual(route["decision_type"], "prediction_market_bet")


class TestDecisionParser(unittest.TestCase):
    def test_parses_title_and_yes_price(self) -> None:
        fields = parse_prediction_market_text(KALSHI_SAMPLE)
        self.assertIn("Knicks", fields["title"])
        self.assertEqual(fields["yes_price"], 42.0)
        self.assertEqual(fields["contract_side"], "Yes")
        self.assertEqual(fields["price"], 42.0)
        self.assertIn("April", fields["expiration"])

    def test_parses_csv_row(self) -> None:
        fields = parse_prediction_market_csv(CSV_SAMPLE)
        self.assertEqual(fields["title"], "Knicks playoffs")
        self.assertEqual(fields["contract_side"], "Yes")
        self.assertEqual(fields["price"], 42.0)
        self.assertEqual(fields["stake"], 100.0)
        self.assertAlmostEqual(fields["user_probability"], 0.55)

    def test_enrich_derives_implied_probability(self) -> None:
        enriched = enrich_bet_fields({"price": 42, "contract_side": "Yes"})
        self.assertAlmostEqual(enriched["implied_probability"], 0.42)
        self.assertAlmostEqual(enriched["cost"], 0.42)


class TestDecisionCompleteness(unittest.TestCase):
    def test_missing_stake_and_user_prob_blocks_solve(self) -> None:
        fields = parse_prediction_market_text(KALSHI_SAMPLE)
        assessment = assess_completeness("prediction_market_bet", fields)
        self.assertIn("stake", assessment["missing"])
        self.assertIn("user_probability", assessment["missing"])
        self.assertFalse(assessment["can_solve"])

    def test_complete_fields_allow_solve(self) -> None:
        fields = parse_prediction_market_csv(CSV_SAMPLE)
        assessment = assess_completeness("prediction_market_bet", fields)
        self.assertTrue(assessment["can_solve"])
        self.assertGreaterEqual(assessment["completeness_pct"], 100.0)


class TestDecisionMath(unittest.TestCase):
    def test_ev_break_even_and_sensitivity(self) -> None:
        fields = parse_prediction_market_csv(CSV_SAMPLE)
        result = analyze_prediction_market_bet(fields)
        self.assertAlmostEqual(result["implied_probability"], 0.42)
        self.assertAlmostEqual(result["break_even_probability"], 0.42)
        self.assertGreater(result["ev_per_contract"], 0)
        self.assertEqual(result["verdict"], "mathematically_favorable")
        self.assertGreater(len(result["sensitivity"]), 5)
        self.assertIn("disclaimer", result)

    def test_solve_decision_dispatches(self) -> None:
        fields = extract_fields(CSV_SAMPLE, "prediction_market_bet", source_type="csv")
        result = solve_decision("prediction_market_bet", fields)
        self.assertIn("ev_per_contract", result)


class TestBetVisuals(unittest.TestCase):
    @unittest.mock.patch("simulations.thinking_plots.plot_ev_bars")
    @unittest.mock.patch("simulations.thinking_plots.plot_probability_tree")
    @unittest.mock.patch("components.importer_ui.st")
    def test_render_bet_visuals_defines_columns_before_use(
        self,
        mock_st: unittest.mock.MagicMock,
        mock_tree: unittest.mock.MagicMock,
        mock_bars: unittest.mock.MagicMock,
    ) -> None:
        col1 = unittest.mock.MagicMock()
        col2 = unittest.mock.MagicMock()
        col1.__enter__ = unittest.mock.Mock(return_value=col1)
        col1.__exit__ = unittest.mock.Mock(return_value=False)
        col2.__enter__ = unittest.mock.Mock(return_value=col2)
        col2.__exit__ = unittest.mock.Mock(return_value=False)
        mock_st.columns.return_value = (col1, col2)

        from components.importer_ui import _render_bet_visuals

        fields = {"user_probability": 0.55, "stake": 100, "cost": 0.42}
        analysis = {"profit_if_win": 0.58, "implied_probability": 0.42}

        _render_bet_visuals(fields, analysis)

        mock_st.columns.assert_called_once_with(2)
        mock_tree.assert_called_once_with(0.55, 0.42, 0.58)
        mock_bars.assert_called_once_with(0.55, 0.58, 0.42)


class TestDecisionHistory(unittest.TestCase):
    def test_save_list_delete_roundtrip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ws = "test_importer"
            ws_dir = Path(tmp) / "workspaces" / ws
            ws_dir.mkdir(parents=True)

            with unittest.mock.patch("suite_workspace.workspace_dir", return_value=ws_dir):
                with unittest.mock.patch("suite_workspace.resolve_workspace_id", return_value=ws):
                    entry = save_import_entry(
                        source_type="text",
                        decision_type="prediction_market_bet",
                        raw_input=KALSHI_SAMPLE,
                        fields={"title": "Knicks playoffs", "price": 42},
                        workspace_id=ws,
                    )
                    self.assertTrue(entry["id"])
                    entries = list_import_history(ws)
                    self.assertEqual(len(entries), 1)
                    self.assertTrue(delete_import_entry(entry["id"], ws))
                    self.assertEqual(len(list_import_history(ws)), 0)


if __name__ == "__main__":
    unittest.main()
