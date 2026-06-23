"""Tests for AMI Problem Importer — Phase 0+ screenshot and richer bet formats."""

from __future__ import annotations

import tempfile
import unittest
import unittest.mock
from pathlib import Path

from decision_examples import EXAMPLE_JOB_OFFER
from decision_history import delete_import_entry, list_import_history, save_import_entry
from decision_math import (
    analyze_decimal_odds_bet,
    analyze_job_offer_decision,
    analyze_poker_hand_decision,
    analyze_prediction_market_bet,
    compute_kelly_fraction,
    compute_stake_sizing,
    enrich_bet_fields,
    solve_decision,
)
from decision_ocr import (
    OCR_UNAVAILABLE_USER_MESSAGE,
    extract_text_from_image,
    image_metadata,
    ocr_availability,
    ocr_fallback_message,
    resolve_tesseract_cmd,
)
from decision_parser import (
    apply_field_edits,
    extract_fields,
    parse_job_offer_text,
    parse_poker_hand_text,
    parse_prediction_market_csv,
    parse_prediction_market_text,
)
from decision_router import route_imported_problem
from decision_templates import assess_completeness, clarification_questions


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

CALCI_MATCHUP = """
Chicago Cubs 50%
New York Mets 50%
1.93x
Mets 1.90x
Spread and total: 2 markets
Volume: 128,324
"""

POKER_AK_EXAMPLE = """
Texas Hold'em. Hero has Ah Kh. Board: Qh Jh 2c. Flop.
Pot $100. Villain bets $50. Call $50. Estimate equity 40%.
"""

POKER_USER_EXACT = """Texas Hold'em.

Hero has Ah Kh.
Board: Qh Jh 2c.
Pot: $100.
Villain bets $50.
Amount to call: $50.
Estimated equity: 40%."""

JOB_OFFER_EXAMPLE = EXAMPLE_JOB_OFFER["text"]


class TestDecisionRouter(unittest.TestCase):
    def test_routes_kalshi_text_to_prediction_market(self) -> None:
        route = route_imported_problem(KALSHI_SAMPLE)
        self.assertEqual(route["decision_type"], "prediction_market_bet")
        self.assertGreater(route["confidence"], 0.3)

    def test_routes_matchup_text(self) -> None:
        route = route_imported_problem(CALCI_MATCHUP)
        self.assertEqual(route["decision_type"], "prediction_market_bet")

    def test_routes_poker_hand_text(self) -> None:
        route = route_imported_problem(POKER_AK_EXAMPLE)
        self.assertEqual(route["decision_type"], "poker_hand_decision")
        self.assertGreater(route["confidence"], 0.4)

    def test_routes_exact_user_multiline_poker_text(self) -> None:
        route = route_imported_problem(POKER_USER_EXACT)
        self.assertEqual(route["decision_type"], "poker_hand_decision")
        self.assertGreaterEqual(route["confidence"], 0.45)

    def test_prediction_market_hint_overrides_auto_detect(self) -> None:
        route = route_imported_problem(POKER_USER_EXACT, hint="prediction_market_bet")
        self.assertEqual(route["decision_type"], "prediction_market_bet")

    def test_routes_job_offer_example(self) -> None:
        route = route_imported_problem(JOB_OFFER_EXAMPLE)
        self.assertEqual(route["decision_type"], "job_offer_decision")
        self.assertGreater(route["confidence"], 0.4)


class TestDecisionParserJob(unittest.TestCase):
    def test_parses_job_offer_example(self) -> None:
        fields = parse_job_offer_text(JOB_OFFER_EXAMPLE)
        self.assertAlmostEqual(fields["current_salary"], 95000.0)
        self.assertAlmostEqual(fields["new_salary"], 115000.0)
        self.assertAlmostEqual(fields["new_bonus"], 10000.0)
        self.assertAlmostEqual(fields["current_commute_minutes"], 15.0)
        self.assertAlmostEqual(fields["new_commute_minutes"], 50.0)
        self.assertAlmostEqual(fields["new_remote_days"], 2.0)

    def test_job_offer_analysis_net_positive(self) -> None:
        fields = parse_job_offer_text(JOB_OFFER_EXAMPLE)
        result = analyze_job_offer_decision(fields)
        self.assertGreater(result["salary_delta"], 0)
        self.assertGreater(result["year1_cash_delta"], 0)
        self.assertIn(result["verdict"], ("favorable_new_offer", "marginal_new_offer", "marginal_stay"))


class TestDecisionParserPoker(unittest.TestCase):
    def test_parses_ak_qj_example(self) -> None:
        fields = parse_poker_hand_text(POKER_AK_EXAMPLE)
        self.assertEqual(fields["game_type"], "texas_holdem")
        self.assertEqual(fields["street"], "flop")
        self.assertIn("Ah", fields["hero_hand"])
        self.assertIn("Kh", fields["hero_hand"])
        self.assertIn("Qh", fields["board"])
        self.assertAlmostEqual(fields["pot_size"], 100.0)
        self.assertAlmostEqual(fields["amount_to_call"], 50.0)
        self.assertAlmostEqual(fields["hero_equity"], 0.40, places=2)

    def test_parses_exact_user_multiline_example(self) -> None:
        fields = parse_poker_hand_text(POKER_USER_EXACT)
        self.assertEqual(fields["game_type"], "texas_holdem")
        self.assertEqual(fields["hero_hand"], "Ah Kh")
        self.assertEqual(fields["board"], "Qh Jh 2c")
        self.assertAlmostEqual(fields["pot_size"], 100.0)
        self.assertAlmostEqual(fields["villain_bet_size"], 50.0)
        self.assertAlmostEqual(fields["amount_to_call"], 50.0)
        self.assertAlmostEqual(fields["hero_equity"], 0.40, places=2)

    def test_exact_user_example_end_to_end(self) -> None:
        route = route_imported_problem(POKER_USER_EXACT)
        self.assertEqual(route["decision_type"], "poker_hand_decision")
        fields = extract_fields(POKER_USER_EXACT, route["decision_type"])
        result = solve_decision("poker_hand_decision", fields)
        self.assertAlmostEqual(result["pot_after_call"], 150.0)
        self.assertAlmostEqual(result["break_even_equity"], 1 / 3, places=2)
        self.assertAlmostEqual(result["ev_call"], 10.0, places=1)
        self.assertEqual(result["recommendation"], "call")

    def test_parses_curly_apostrophe_holdem(self) -> None:
        text = POKER_USER_EXACT.replace("Hold'em", "Hold\u2019em")
        fields = parse_poker_hand_text(text)
        self.assertEqual(fields["game_type"], "texas_holdem")

    def test_poker_completeness_requires_equity(self) -> None:
        fields = parse_poker_hand_text("Pot $80. Villain bets $40.")
        assessment = assess_completeness("poker_hand_decision", fields)
        self.assertIn("hero_equity", assessment["missing_required"])
        self.assertFalse(assessment["can_solve"])


class TestDecisionMathPoker(unittest.TestCase):
    def test_poker_pot_odds_ev_call(self) -> None:
        fields = parse_poker_hand_text(POKER_AK_EXAMPLE)
        result = analyze_poker_hand_decision(fields)
        self.assertAlmostEqual(result["break_even_equity"], 1 / 3, places=2)
        self.assertAlmostEqual(result["ev_call"], 10.0, places=1)
        self.assertEqual(result["recommendation"], "call")
        self.assertEqual(result["verdict"], "call_favorable")

    def test_poker_solve_decision_dispatch(self) -> None:
        fields = extract_fields(POKER_AK_EXAMPLE, "poker_hand_decision")
        result = solve_decision("poker_hand_decision", fields)
        self.assertAlmostEqual(result["ev_call"], 10.0, places=1)
        self.assertGreater(len(result.get("sensitivity") or []), 5)

    def test_poker_fold_when_equity_low(self) -> None:
        fields = parse_poker_hand_text(POKER_AK_EXAMPLE)
        fields["hero_equity"] = 0.25
        result = analyze_poker_hand_decision(fields)
        self.assertLess(result["ev_call"], 0)
        self.assertEqual(result["recommendation"], "fold")


class TestDecisionParser(unittest.TestCase):
    def test_parses_title_and_yes_price(self) -> None:
        fields = parse_prediction_market_text(KALSHI_SAMPLE)
        self.assertIn("Knicks", fields["title"])
        self.assertEqual(fields["yes_price"], 42.0)
        self.assertEqual(fields["contract_side"], "Yes")
        self.assertEqual(fields["price"], 42.0)
        self.assertIn("April", fields["expiration"])
        self.assertEqual(fields["bet_format"], "prediction_market")

    def test_parses_calci_matchup(self) -> None:
        fields = parse_prediction_market_text(CALCI_MATCHUP)
        self.assertIn("Cubs", fields["title"])
        self.assertIn("Mets", fields["title"])
        self.assertEqual(len(fields["team_options"]), 2)
        self.assertAlmostEqual(fields["team_options"][0]["implied_pct"], 50.0)
        self.assertEqual(fields["volume"], 128324.0)
        self.assertEqual(fields["spread_total_markets"], 2)
        self.assertIn(fields["bet_format"], ("moneyline_matchup", "decimal_multiplier", "percentage_implied"))
        self.assertIsNotNone(fields.get("multiplier"))

    def test_parses_csv_row(self) -> None:
        fields = parse_prediction_market_csv(CSV_SAMPLE)
        self.assertEqual(fields["title"], "Knicks playoffs")
        self.assertEqual(fields["contract_side"], "Yes")
        self.assertEqual(fields["price"], 42.0)
        self.assertEqual(fields["stake"], 100.0)
        self.assertAlmostEqual(fields["user_probability"], 0.55)

    def test_apply_field_edits_reenriches(self) -> None:
        base = parse_prediction_market_text(KALSHI_SAMPLE)
        edited = apply_field_edits(base, {"stake": 50, "user_probability": 0.6, "price": 42})
        self.assertEqual(edited["stake"], 50)
        self.assertAlmostEqual(edited["user_probability"], 0.6)
        self.assertTrue(edited.get("ocr_corrected"))

    def test_apply_field_edits_clears_uncertain_flags(self) -> None:
        base = parse_prediction_market_text(CALCI_MATCHUP)
        self.assertIn("contract_side", base.get("uncertain_fields", []))
        edited = apply_field_edits(
            base,
            {
                "contract_side": "New York Mets",
                "multiplier": 1.90,
                "stake": 100,
                "user_probability": 0.55,
                "bet_format": "moneyline_matchup",
            },
        )
        self.assertEqual(edited["contract_side"], "New York Mets")
        self.assertAlmostEqual(edited["multiplier"], 1.90)
        self.assertNotIn("contract_side", edited.get("uncertain_fields", []))
        assessment = assess_completeness("prediction_market_bet", edited)
        self.assertTrue(assessment["can_solve"])
        self.assertNotIn("contract_side", assessment["missing_required"])
        self.assertNotIn("multiplier", assessment["missing_required"])


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

    def test_matchup_flags_uncertain_fields(self) -> None:
        fields = parse_prediction_market_text(CALCI_MATCHUP)
        assessment = assess_completeness("prediction_market_bet", fields)
        self.assertTrue(assessment.get("uncertain") or assessment.get("missing"))


class TestDecisionMath(unittest.TestCase):
    def test_ev_binary_prediction_market(self) -> None:
        fields = parse_prediction_market_csv(CSV_SAMPLE)
        result = analyze_prediction_market_bet(fields)
        self.assertAlmostEqual(result["implied_probability"], 0.42)
        self.assertAlmostEqual(result["break_even_probability"], 0.42)
        self.assertGreater(result["ev_per_contract"], 0)
        self.assertEqual(result["bet_format"], "prediction_market")

    def test_ev_decimal_multiplier(self) -> None:
        fields = enrich_bet_fields({
            "bet_format": "decimal_multiplier",
            "multiplier": 1.90,
            "stake": 100,
            "user_probability": 0.58,
            "contract_side": "Mets",
            "title": "Mets moneyline",
        })
        result = analyze_decimal_odds_bet(fields)
        self.assertAlmostEqual(result["break_even_probability"], 1 / 1.90, places=3)
        self.assertAlmostEqual(result["implied_probability"], 1 / 1.90, places=3)
        self.assertGreater(result["ev_total"], 0)
        self.assertAlmostEqual(result["profit_if_win"], 90.0, places=1)

    def test_mets_190_multiplier_with_team_percent_implied(self) -> None:
        """Cubs/Mets case: team % + decimal multiplier must use multiplier payout math."""
        fields = {
            "bet_format": "percentage_implied",
            "contract_side": "New York Mets",
            "multiplier": 1.90,
            "implied_probability": 0.50,
            "stake": 100,
            "user_probability": 0.55,
            "title": "Cubs vs Mets",
        }
        result = analyze_prediction_market_bet(fields)
        self.assertAlmostEqual(result["profit_if_win"], 90.0)
        self.assertAlmostEqual(result["ev_total"], 4.5, places=1)
        self.assertAlmostEqual(result["expected_roi"], 0.045, places=3)
        self.assertAlmostEqual(result["implied_probability"], 0.50)
        self.assertAlmostEqual(result["break_even_probability"], 1 / 1.90, places=3)
        self.assertAlmostEqual(result["loss_if_lose"], 100.0)

    def test_mets_case_through_solve_decision(self) -> None:
        fields = enrich_bet_fields({
            "bet_format": "percentage_implied",
            "contract_side": "New York Mets",
            "multiplier": 1.90,
            "implied_probability": 0.50,
            "stake": 100,
            "user_probability": 0.55,
            "title": "Cubs vs Mets",
        })
        result = solve_decision("prediction_market_bet", fields)
        self.assertAlmostEqual(result["profit_if_win"], 90.0)
        self.assertAlmostEqual(result["ev_total"], 4.5, places=1)
        self.assertAlmostEqual(result["expected_roi"], 0.045, places=3)

    def test_multiplier_materially_changes_ev(self) -> None:
        base = {
            "bet_format": "percentage_implied",
            "contract_side": "New York Mets",
            "implied_probability": 0.50,
            "stake": 100,
            "user_probability": 0.55,
        }
        ev_low = analyze_prediction_market_bet({**base, "multiplier": 1.90})["ev_total"]
        ev_high = analyze_prediction_market_bet({**base, "multiplier": 3.00})["ev_total"]
        self.assertAlmostEqual(ev_low, 4.5, places=1)
        self.assertAlmostEqual(ev_high, 65.0, places=1)
        self.assertGreater(ev_high, ev_low)

    def test_kelly_fraction_mets_case(self) -> None:
        net_odds = 90.0 / 100.0
        self.assertAlmostEqual(compute_kelly_fraction(0.55, net_odds), 0.05, places=3)

    def test_bankroll_stake_sizing_flags_oversized_bet(self) -> None:
        fields = {
            "bet_format": "percentage_implied",
            "contract_side": "New York Mets",
            "multiplier": 1.90,
            "implied_probability": 0.50,
            "stake": 120,
            "bankroll": 1000,
            "user_probability": 0.55,
            "risk_tolerance": "moderate",
            "title": "Cubs vs Mets",
        }
        result = analyze_prediction_market_bet(fields)
        sizing = result["stake_sizing"]
        self.assertAlmostEqual(sizing["kelly_fraction"], 0.05, places=3)
        self.assertAlmostEqual(sizing["kelly_stake"], 50.0, places=1)
        self.assertAlmostEqual(sizing["half_kelly_stake"], 25.0, places=1)
        self.assertAlmostEqual(sizing["quarter_kelly_stake"], 12.5, places=1)
        self.assertAlmostEqual(sizing["stake_pct_of_bankroll"], 0.12, places=3)
        self.assertEqual(sizing["stake_assessment"], "too_large")
        self.assertTrue(sizing["stake_warning"])
        self.assertIn("aggressive", sizing["stake_warning_message"].lower())

    def test_bankroll_stake_sizing_reasonable_bet(self) -> None:
        fields = {
            "bet_format": "decimal_multiplier",
            "multiplier": 1.90,
            "stake": 25,
            "bankroll": 1000,
            "user_probability": 0.55,
            "implied_probability": 0.50,
            "risk_tolerance": "moderate",
        }
        result = analyze_decimal_odds_bet(fields)
        sizing = result["stake_sizing"]
        self.assertEqual(sizing["stake_assessment"], "reasonable")
        self.assertFalse(sizing["stake_warning"])

    def test_stake_sizing_without_bankroll_shows_kelly_pct_only(self) -> None:
        sizing = compute_stake_sizing(
            fields={"risk_tolerance": "moderate"},
            p_user=0.55,
            edge=0.05,
            ev_total=4.5,
            profit_if_win=90.0,
            loss_if_lose=100.0,
            stake=100.0,
        )
        self.assertFalse(sizing["has_bankroll"])
        self.assertIsNone(sizing["kelly_stake"])
        self.assertAlmostEqual(sizing["kelly_fraction"], 0.05, places=3)
        self.assertIn("bankroll", sizing["sizing_explanation"].lower())

    def test_parse_bankroll_from_text(self) -> None:
        text = "Mets 1.90x\nstake: $100\nbankroll: $1000\nmy estimate: 55%"
        fields = parse_prediction_market_text(text)
        self.assertAlmostEqual(fields.get("bankroll"), 1000.0)
        self.assertAlmostEqual(fields.get("stake"), 100.0)

    def test_solve_decision_dispatches(self) -> None:
        fields = extract_fields(CSV_SAMPLE, "prediction_market_bet", source_type="csv")
        result = solve_decision("prediction_market_bet", fields)
        self.assertIn("ev_per_contract", result)


class TestImporterHistoryPanel(unittest.TestCase):
    @unittest.mock.patch("components.importer_ui.st")
    @unittest.mock.patch("components.importer_ui.list_import_history", return_value=[])
    def test_render_history_panel_empty_no_crash(
        self,
        _list_mock: unittest.mock.MagicMock,
        mock_st: unittest.mock.MagicMock,
    ) -> None:
        from components.importer_ui import _render_history_panel

        _render_history_panel()
        mock_st.info.assert_called_once()
        _list_mock.assert_called_once()

    @unittest.mock.patch("components.importer_ui.st")
    @unittest.mock.patch("components.importer_ui.list_import_history")
    def test_render_history_panel_with_entries(
        self,
        list_mock: unittest.mock.MagicMock,
        mock_st: unittest.mock.MagicMock,
    ) -> None:
        from components.importer_ui import _render_history_panel

        list_mock.return_value = [
            {
                "id": "abc-123",
                "timestamp": "2026-06-23T12:00:00+00:00",
                "decision_type": "prediction_market_bet",
                "source_type": "text",
                "fields": {"title": "Knicks playoffs"},
                "analysis": {"verdict_label": "Favorable"},
            }
        ]
        _render_history_panel()
        list_mock.assert_called_once()
        mock_st.expander.assert_called()


class TestDecisionOCR(unittest.TestCase):
    def test_ocr_availability_returns_dict(self) -> None:
        info = ocr_availability()
        self.assertIn("available", info)
        self.assertIn("ready", info)
        self.assertIn("pytesseract_installed", info)
        self.assertIn("tesseract_available", info)
        self.assertIn("engines", info)

    def test_extract_text_empty_bytes_no_crash(self) -> None:
        result = extract_text_from_image(b"")
        self.assertIsInstance(result, dict)
        self.assertFalse(result["success"])
        self.assertIn("error", result)
        self.assertIn("Screenshot received", result["error"])

    def test_ocr_graceful_failure_without_tesseract_binary(self) -> None:
        with unittest.mock.patch("decision_ocr.resolve_tesseract_cmd", return_value=None):
            with unittest.mock.patch("decision_ocr._pytesseract_installed", return_value=True):
                with unittest.mock.patch("decision_ocr._pillow_installed", return_value=True):
                    result = extract_text_from_image(b"\x89PNG\r\n\x1a\n")
        self.assertFalse(result["success"])
        self.assertIn(OCR_UNAVAILABLE_USER_MESSAGE, result["error"])

    def test_ocr_fallback_message(self) -> None:
        msg = ocr_fallback_message({"success": False, "error": "something"})
        self.assertIn(OCR_UNAVAILABLE_USER_MESSAGE, msg)
        self.assertEqual(ocr_fallback_message({"success": True}), "")

    def test_resolve_tesseract_cmd_env(self) -> None:
        with unittest.mock.patch.dict("os.environ", {"TESSERACT_CMD": "C:\\fake\\tesseract.exe"}):
            with unittest.mock.patch("os.path.isfile", return_value=True):
                self.assertEqual(resolve_tesseract_cmd(), "C:\\fake\\tesseract.exe")

    def test_image_metadata(self) -> None:
        data = b"not-an-image"
        meta = image_metadata(data, filename="test.png")
        self.assertEqual(meta["filename"], "test.png")
        self.assertEqual(meta["size_bytes"], len(data))


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

        fields = {"user_probability": 0.55, "stake": 100, "cost": 0.42, "bet_format": "prediction_market"}
        analysis = {"profit_if_win": 0.58, "implied_probability": 0.42, "bet_format": "prediction_market"}

        _render_bet_visuals(fields, analysis)

        mock_st.columns.assert_called_once_with(2)
        mock_tree.assert_called_once()
        mock_bars.assert_called_once()

    @unittest.mock.patch("simulations.thinking_plots.plot_ev_bars")
    @unittest.mock.patch("simulations.thinking_plots.plot_probability_tree")
    @unittest.mock.patch("components.importer_ui.st")
    def test_render_bet_visuals_decimal_odds_no_crash(
        self,
        mock_st: unittest.mock.MagicMock,
        _mock_tree: unittest.mock.MagicMock,
        _mock_bars: unittest.mock.MagicMock,
    ) -> None:
        col1 = unittest.mock.MagicMock()
        col2 = unittest.mock.MagicMock()
        col1.__enter__ = unittest.mock.Mock(return_value=col1)
        col1.__exit__ = unittest.mock.Mock(return_value=False)
        col2.__enter__ = unittest.mock.Mock(return_value=col2)
        col2.__exit__ = unittest.mock.Mock(return_value=False)
        mock_st.columns.return_value = (col1, col2)

        from components.importer_ui import _render_bet_visuals

        fields = {"user_probability": 0.55, "stake": 100, "multiplier": 1.9, "bet_format": "decimal_multiplier"}
        analysis = {"profit_if_win": 90, "implied_probability": 0.526, "bet_format": "decimal_multiplier"}

        _render_bet_visuals(fields, analysis)


class TestClarificationQuestions(unittest.TestCase):
    def test_questions_for_incomplete_matchup(self) -> None:
        fields = parse_prediction_market_text(CALCI_MATCHUP)
        qs = clarification_questions(fields)
        ids = {q["id"] for q in qs}
        self.assertTrue("stake" in ids or "user_probability" in ids or "contract_side" in ids)


class TestDecisionHistory(unittest.TestCase):
    def test_save_with_image_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ws = "test_importer"
            ws_dir = Path(tmp) / "workspaces" / ws
            ws_dir.mkdir(parents=True)

            with unittest.mock.patch("suite_workspace.workspace_dir", return_value=ws_dir):
                with unittest.mock.patch("suite_workspace.resolve_workspace_id", return_value=ws):
                    entry = save_import_entry(
                        source_type="image",
                        decision_type="prediction_market_bet",
                        raw_input=CALCI_MATCHUP,
                        fields={"title": "Cubs vs Mets"},
                        image_meta={"filename": "screen.png", "size_bytes": 12345},
                        ocr_text="Cubs 50%",
                        corrected_fields={"stake": 100},
                        workspace_id=ws,
                    )
                    self.assertEqual(entry["image_meta"]["filename"], "screen.png")
                    self.assertEqual(entry["ocr_text"], "Cubs 50%")
                    self.assertTrue(delete_import_entry(entry["id"], ws))


if __name__ == "__main__":
    unittest.main()
