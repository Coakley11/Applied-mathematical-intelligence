"""Practice Log analysis handoff — AMI title, routing, and store import smoke."""

from __future__ import annotations

import importlib
import unittest
from unittest.mock import patch

from components.applied_math_problem_router import MUSIC_PRACTICE_LOG_ANALYSIS, _route_music
from components.music_ami_solvers import _practice_log_analysis_result


class TestPracticeLogAmiHandoff(unittest.TestCase):
    def test_persist_suite_return_insight_import(self) -> None:
        mod = importlib.import_module("applied_math_return_insight")
        self.assertTrue(hasattr(mod, "AMI_INSIGHT_STORE_VERSION"))
        self.assertTrue(hasattr(mod, "persist_suite_return_insight"))
        self.assertTrue(callable(mod.persist_suite_return_insight))

    def test_source_question_card_title_for_practice_log(self) -> None:
        from suite_analytical_question import (
            PRACTICE_LOG_ANALYSIS_TITLE,
            is_practice_log_analysis_context,
            source_question_card_title,
        )

        ctx = {
            "handoff_kind": "practice_log_analysis",
            "display_category": "analysis_handoff",
            "user_request": "analyze_practice",
            "intent": "practice_history_analysis",
        }
        self.assertTrue(is_practice_log_analysis_context(ctx))
        self.assertEqual(source_question_card_title("music", ctx), PRACTICE_LOG_ANALYSIS_TITLE)

    def test_continue_copy_for_practice_log(self) -> None:
        from suite_analytical_question import PRACTICE_LOG_ANALYSIS_TITLE, analytical_question_continue_copy

        payload = {
            "source_app": "music",
            "question": "Analyze my practice history.",
            "context": {
                "handoff_kind": "practice_log_analysis",
                "practice_log_summary": {"session_count": 3, "total_minutes": 75},
            },
        }
        title, subtitle, button = analytical_question_continue_copy(payload)
        self.assertEqual(title, PRACTICE_LOG_ANALYSIS_TITLE)
        self.assertIn("3 session", subtitle)
        self.assertIn("Practice Log Analysis", button)

    def test_route_music_practice_log_analysis(self) -> None:
        route = _route_music(
            "Analyze my practice history.",
            {
                "handoff_kind": "practice_log_analysis",
                "practice_log_summary": {"session_count": 2, "total_minutes": 40},
                "recent_practice_history": [{"active_song": "Autumn Leaves", "duration_minutes": 20}],
            },
        )
        self.assertEqual(route.problem_type_id, MUSIC_PRACTICE_LOG_ANALYSIS)
        self.assertIn("practice history", route.intent_restatement.lower())

    def test_practice_log_solver_uses_logged_sessions(self) -> None:
        result = _practice_log_analysis_result(
            "Analyze my practice history.",
            {
                "practice_log_summary": {
                    "session_count": 2,
                    "total_minutes": 45,
                    "most_practiced_songs": ["Blue Bossa", "Autumn Leaves"],
                    "most_common_focus_areas": ["tone/sound", "timing/rhythm"],
                    "repeated_challenges": ["rush at bar 8"],
                    "suggested_next_focus": "groove",
                    "top_song": "Blue Bossa",
                    "top_focus": "timing/rhythm",
                    "repeated_challenge": "rush at bar 8",
                },
                "recent_practice_history": [
                    {
                        "active_song": "Blue Bossa",
                        "duration_minutes": 25,
                        "focus_area": "tone/sound",
                        "instrument": "Tenor Saxophone",
                        "what_was_hard": "rush at bar 8",
                    },
                    {
                        "active_song": "Autumn Leaves",
                        "duration_minutes": 20,
                        "focus_area": "timing/rhythm",
                        "instrument": "Tenor Saxophone",
                        "what_was_hard": "bridge",
                    },
                ],
            },
        )
        body = result.short_answer or ""
        self.assertIn("practice history", body.lower())
        self.assertIn("practice history", result.intent_restatement.lower())
        self.assertIn("2", body)
        self.assertIn("Blue Bossa", body)
        self.assertIn("Tenor Saxophone", body)
        self.assertIn("tone/sound", body)
        self.assertIn("rush at bar 8", body)
        self.assertIn("Next 30-minute session plan", body)
        self.assertIn("warmup", body.lower())
        self.assertIn("run-through", body.lower())
        self.assertIn("Confidence is moderate", body)
        self.assertNotIn("use the plan below", body.lower())
        self.assertNotEqual(body.strip(), "Review your practice patterns and use the next-session plan below.")

    def test_practice_log_solver_payload_shape_from_music(self) -> None:
        """Matches fields emitted by Music build_practice_log_ami_payload."""
        result = _practice_log_analysis_result(
            "Analyze my practice history.",
            {
                "practice_log_ami_payload": {
                    "practice_log_summary": {
                        "session_count": 2,
                        "total_minutes": 60,
                        "most_practiced_songs": ["Say"],
                        "most_common_focus_areas": ["tone/sound"],
                        "repeated_challenges": ["written-key transitions"],
                        "suggested_next_focus": "tone/sound",
                        "last_session_summary": {
                            "active_song": "Say",
                            "instrument": "Tenor Saxophone",
                            "bpm": 92,
                            "section_practiced": "chorus",
                        },
                    },
                    "recent_sessions": [
                        {
                            "active_song": "Say",
                            "duration_minutes": 30,
                            "instrument": "Tenor Saxophone",
                            "focus_area": "tone/sound",
                            "what_was_hard": "written-key transitions",
                            "next_step": "slow chorus loop",
                        },
                        {
                            "active_song": "Say",
                            "duration_minutes": 30,
                            "instrument": "Tenor Saxophone",
                            "focus_area": "tone/sound",
                        },
                    ],
                },
            },
        )
        body = result.short_answer or ""
        self.assertIn("Say", body)
        self.assertIn("2", body)
        self.assertIn("60", body)
        self.assertIn("written-key transitions", body)
        self.assertIn("warmup", body.lower())
        self.assertIn("notes + next step", body.lower())
        self.assertGreaterEqual(body.lower().count(" min"), 5)
        self.assertIn("Confidence is moderate", body)

    def test_persist_suite_return_insight_does_not_raise(self) -> None:
        from applied_math_return_insight import persist_suite_return_insight

        class _FakeSessionState(dict):
            def __getattr__(self, name):
                return self[name]

            def __setattr__(self, name, value):
                self[name] = value

        class _FakeSt:
            def __init__(self) -> None:
                self.session_state = _FakeSessionState()

        st = _FakeSt()
        st.session_state["_suite_ai_question_id"] = "q-practice-log"
        with patch("applied_math_return_insight.store_applied_math_insight", return_value="ins-1") as store_mock:
            trace = persist_suite_return_insight(
                st,
                question="Analyze my practice history.",
                source_app="music",
                source_page="log",
                context={"handoff_kind": "practice_log_analysis"},
                route=None,
                result=None,
            )
        self.assertTrue(store_mock.called)
        self.assertIsInstance(trace, dict)


if __name__ == "__main__":
    unittest.main()
