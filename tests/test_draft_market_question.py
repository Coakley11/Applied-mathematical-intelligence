"""Draft-market prediction question detection."""

from __future__ import annotations

import unittest

from components.draft_market_question import (
    extract_draft_position_query,
    is_draft_head_to_head_question,
    is_draft_market_prediction_question,
    is_draft_review_question,
    is_player_explanation_question,
    is_position_best_available_question,
    is_roster_needs_question,
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

    def test_make_it_back_is_timing_not_market(self) -> None:
        from components.draft_market_question import is_draft_timing_question

        q = "Will William Contreras make it back to me?"
        self.assertTrue(is_draft_timing_question(q))
        self.assertFalse(is_draft_market_prediction_question(q))

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

    def test_why_contreras_best_catcher_is_player_explanation_not_market(self) -> None:
        q = "Why is William Contreras the best catcher to draft now?"
        self.assertTrue(is_player_explanation_question(q))
        self.assertFalse(is_draft_market_prediction_question(q))

    def test_why_contreras_draft_next_is_player_explanation(self) -> None:
        q = "Why is William Contreras the best catcher to draft next?"
        self.assertTrue(is_player_explanation_question(q))
        self.assertFalse(is_draft_market_prediction_question(q))

    def test_next_best_catcher_is_position_best_not_market(self) -> None:
        q = "Who is the next best catcher?"
        self.assertTrue(is_position_best_available_question(q))
        self.assertFalse(is_draft_market_prediction_question(q))

    def test_best_available_catcher_restatement(self) -> None:
        from components.draft_market_question import draft_question_restatement

        rest = draft_question_restatement("Who is the best available catcher?")
        self.assertIn("available", rest.lower())
        self.assertIn("catcher", rest.lower())
        self.assertNotIn("player b", rest.lower())

    def test_draft_review_detection(self) -> None:
        self.assertTrue(is_draft_review_question("How would you rate my picks so far?"))
        self.assertTrue(is_draft_review_question("Grade my draft"))
        self.assertFalse(is_draft_review_question("Should I draft William Contreras or Jose Ramirez?"))

    def test_roster_needs_detection(self) -> None:
        self.assertTrue(is_roster_needs_question("Which positions left are needed for me to pick?"))
        self.assertTrue(is_roster_needs_question("What positions should I target next?"))
        self.assertFalse(is_roster_needs_question("Is Corbin Carroll worth a Round 2 pick?"))

    def test_draft_timing_detection(self) -> None:
        from components.draft_market_question import is_draft_timing_question

        self.assertTrue(
            is_draft_timing_question(
                "Should I select William Contreras as a catcher now or wait for a later round?"
            )
        )
        self.assertTrue(is_draft_timing_question("Will William Contreras make it back to me?"))
        self.assertFalse(is_draft_timing_question("Why is William Contreras the best catcher to draft?"))

    def test_contreras_now_or_later_timing_not_compare(self) -> None:
        from components.draft_market_question import is_draft_timing_question

        q = "Should I draft William Contreras now or later?"
        self.assertTrue(is_draft_timing_question(q))
        self.assertFalse(is_draft_head_to_head_question(q))

    def test_contreras_at_catcher_now_or_later_round_timing(self) -> None:
        from components.draft_market_question import is_draft_timing_question

        q = "Should I draft William Contreras at Catcher now or a later round?"
        self.assertTrue(is_draft_timing_question(q))
        self.assertFalse(is_draft_head_to_head_question(q))

    def test_extract_position_from_at_c_for_pick(self) -> None:
        from components.draft_market_question import extract_draft_position_query

        q = "Should I draft William Contreras at C for pick 8 or wait for a later round?"
        self.assertEqual(extract_draft_position_query(q), "catcher")

    def test_extract_draft_team_query_team_number(self) -> None:
        from components.draft_market_question import extract_draft_team_query

        team = extract_draft_team_query(
            "How would you rate Team 2's picks so far?",
            my_team="Daniel",
            team_names=["Daniel", "Team 2", "Team 3"],
        )
        self.assertEqual(team, "Team 2")


if __name__ == "__main__":
    unittest.main()
