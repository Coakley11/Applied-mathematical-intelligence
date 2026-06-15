"""Command Center Continue must target Applied Intelligence with question_id."""

from __future__ import annotations

import unittest
from unittest.mock import patch

from suite_analytical_question import submit_analytical_question


class TestAnalyticalQuestionContinueUrl(unittest.TestCase):
    @patch("suite_activity_client.record_activity")
    @patch("suite_analytical_question._upsert_applied_intelligence_resume")
    def test_record_activity_gets_ami_action_url(self, _upsert, record_mock) -> None:
        submit_analytical_question(
            source_app="baseball",
            source_page="Draft Assistant Simulator",
            question="Who should I draft next?",
            context={"current_pick": 8},
            session_state={},
        )
        record_mock.assert_called_once()
        url = str(record_mock.call_args.kwargs.get("action_url") or "")
        self.assertIn("applied-mathematical-intelligence", url)
        self.assertIn("suite_ai_question_id=", url)
        self.assertIn("suite_page=Solve", url.replace("+", " "))


if __name__ == "__main__":
    unittest.main()
