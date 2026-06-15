"""Resume launch must hydrate when only suite_ai_question_id is in the URL."""

from __future__ import annotations

import unittest
from unittest.mock import patch

from suite_resume_launch import apply_suite_resume_launch, hydrate_applied_intelligence_from_url


class _FakeSessionState(dict):
    def __getattr__(self, name: str):
        return self.get(name)

    def __setattr__(self, name: str, value):
        self[name] = value


class _FakeSt:
    def __init__(self, params: dict[str, str]):
        self.query_params = params
        self.session_state = _FakeSessionState()


class TestAppliedIntelligenceQuestionIdDeepLink(unittest.TestCase):
    def test_apply_suite_resume_launch_accepts_question_id_only(self) -> None:
        st = _FakeSt({"suite_ai_question_id": "0fb8a8a81eab", "suite_ai_question": "Who should I draft next?"})
        with patch("suite_resume_launch._apply_applied_intelligence") as apply_fn:
            self.assertTrue(apply_suite_resume_launch(st, "applied_intelligence"))
            apply_fn.assert_called_once()

    def test_hydrate_from_url_calls_hydrate_session(self) -> None:
        st = _FakeSt({"suite_ai_question_id": "abc123"})
        with patch("suite_analytical_question.hydrate_applied_intelligence_session") as hydrate_fn:
            self.assertTrue(hydrate_applied_intelligence_from_url(st))
            hydrate_fn.assert_called_once_with(st)


if __name__ == "__main__":
    unittest.main()
