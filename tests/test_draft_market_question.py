"""Draft-market prediction question detection."""

from __future__ import annotations

import unittest

from components.draft_market_question import (
    extract_draft_position_query,
    is_draft_head_to_head_question,
    is_draft_market_prediction_question,
    position_matches_row,
)


class TestDraftMarketQuestionDetection(unittest.TestCase):
    def test_next_catcher_is_draft_market(self) -> None:
        q = "Who is likely to be the next catcher picked in this draft?"
        self.assertTrue(is_draft_market_prediction_question(q))
        self.assertEqual(extract_draft_position_query(q), "catcher")

    def test_position_run_is_draft_market(self) -> None:
        q = "Which position is likely to run next?"
        self.assertTrue(is_draft_market_prediction_question(q))
        self.assertEqual(extract_draft_position_query(q), "")

    def test_make_it_back_is_draft_market(self) -> None:
        q = "Will William Contreras make it back to me?"
        self.assertTrue(is_draft_market_prediction_question(q))

    def test_catcher_run_is_draft_market(self) -> None:
        q = "Is a catcher run coming?"
        self.assertTrue(is_draft_market_prediction_question(q))

    def test_safest_upside_is_not_draft_compare(self) -> None:
        self.assertFalse(is_draft_head_to_head_question("Who is safest vs highest upside?"))

    def test_career_projection_is_not_draft_market(self) -> None:
        q = "Will Julio Rodriguez score more runs than Aaron Judge over the next 10 seasons?"
        self.assertFalse(is_draft_market_prediction_question(q))

    def test_position_matches_catcher_row(self) -> None:
        self.assertTrue(position_matches_row("catcher", "C"))
        self.assertTrue(position_matches_row("catcher", "C/1B"))


if __name__ == "__main__":
    unittest.main()
