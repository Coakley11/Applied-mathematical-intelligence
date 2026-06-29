"""Practice Log Analysis — AMI must restore by analysis_run_id, not stale session."""

from __future__ import annotations

import json
import unittest
from unittest.mock import MagicMock, patch

from applied_math_return_insight import SESSION_PENDING_KEY, apply_ami_insight_from_query, hydrate_applied_math_insight_for_session
from components.problem_solving import _load_suite_context
from suite_analytical_question import (
    PRACTICE_LOG_FULL_REPORT_RENDERER,
    hydrate_applied_intelligence_session,
    load_analytical_question_payload,
    should_render_practice_log_full_report,
)


class _St:
    def __init__(self, params: dict | None = None):
        self.session_state: dict = {}
        self.query_params = dict(params or {})


class TestPracticeLogAmiRestore(unittest.TestCase):
    def test_load_payload_prefers_analysis_run_id(self) -> None:
        run_blob = {
            "context": {
                "user_request": "analyze_practice",
                "handoff_kind": "practice_log_analysis",
                "analysis_run_id": "run-b",
                "report_generated_at": "2026-06-29T01:42:00+00:00",
                "progress_report": {"executive_summary": "run B"},
            },
            "question_id": "q-stable",
        }
        with patch("suite_account.fetch_saved_item", return_value={"payload": run_blob}):
            with patch("suite_analytical_question._CONTEXT_SEARCH_APPS", ["applied_intelligence"]):
                payload = load_analytical_question_payload("q-stable", analysis_run_id="run-b")
        self.assertEqual(payload.get("analysis_run_id"), "run-b")
        self.assertEqual(
            (payload.get("context") or {}).get("progress_report", {}).get("executive_summary"),
            "run B",
        )

    def test_hydrate_session_prefers_run_id_blob(self) -> None:
        st = _St({"suite_practice_analysis_run_id": "run-b", "suite_ami_insight": "pa:run-b"})
        fresh_ctx = {
            "user_request": "analyze_practice",
            "handoff_kind": "practice_log_analysis",
            "analysis_run_id": "run-b",
            "progress_report": {"executive_summary": "run B"},
        }
        with patch(
            "suite_analytical_question.load_analytical_question_payload",
            side_effect=lambda qid, **kw: (
                {"context": fresh_ctx, "question_id": "q1", "source_app": "music"}
                if kw.get("analysis_run_id") == "run-b"
                else {"context": {"progress_report": {"executive_summary": "run A"}}}
            ),
        ):
            hydrate_applied_intelligence_session(st)
        loaded = json.loads(st.session_state["_suite_ai_context"])
        self.assertEqual(loaded.get("progress_report", {}).get("executive_summary"), "run B")
        self.assertEqual(st.session_state.get("_suite_practice_analysis_run_id"), "run-b")

    def test_apply_insight_from_run_id_clears_stale_pending(self) -> None:
        st = _St({"suite_practice_analysis_run_id": "run-b"})
        st.session_state[SESSION_PENDING_KEY] = {
            "insight_id": "pa:run-a",
            "conclusion": "yesterday",
            "context_snapshot": {"analysis_run_id": "run-a"},
        }
        st.session_state["_ami_hydrated_insight_id"] = "pa:run-a"
        with patch(
            "applied_math_return_insight.load_applied_math_insight",
            return_value={
                "insight_id": "pa:run-b",
                "conclusion": "today",
                "context_snapshot": {"analysis_run_id": "run-b", "report_generated_at": "2026-06-29T01:42:00+00:00"},
            },
        ):
            ok = apply_ami_insight_from_query(st, "applied_intelligence")
        self.assertTrue(ok)
        self.assertEqual(st.session_state[SESSION_PENDING_KEY]["insight_id"], "pa:run-b")
        self.assertEqual(st.session_state.get("_ami_practice_log_stale_fallback_blocked"), True)

    def test_hydrate_blocks_session_fallback_when_run_id_present(self) -> None:
        st = _St({"suite_practice_analysis_run_id": "run-b"})
        st.session_state[SESSION_PENDING_KEY] = {"insight_id": "pa:run-a", "conclusion": "stale"}
        with patch("applied_math_return_insight.load_applied_math_insight", return_value={}):
            ok = hydrate_applied_math_insight_for_session(st, "applied_intelligence")
        self.assertFalse(ok)
        self.assertEqual(st.session_state.get("_ami_insight_hydrate_source"), "practice_analysis_run_id_missing")

    def test_hydrate_selects_practice_log_renderer_and_stages_insight(self) -> None:
        st = _St(
            {
                "suite_practice_analysis_run_id": "run-b",
                "suite_ami_insight": "pa:run-b",
            }
        )
        st.session_state[SESSION_PENDING_KEY] = {
            "insight_id": "pa:run-a",
            "conclusion": "yesterday",
        }
        fresh_ctx = {
            "routing_hint": "practice_history_analysis",
            "handoff_kind": "practice_log_analysis",
            "analysis_run_id": "run-b",
            "report_generated_at": "2026-06-29T13:28:00+00:00",
            "progress_report": {
                "title": "Analyze My Practice — Progress Report",
                "executive_summary": "run B executive",
            },
        }
        with patch(
            "suite_analytical_question.load_analytical_question_payload",
            return_value={"context": fresh_ctx, "question_id": "q1", "source_app": "music"},
        ):
            hydrate_applied_intelligence_session(st)
        self.assertEqual(st.session_state.get("_suite_ai_selected_renderer"), PRACTICE_LOG_FULL_REPORT_RENDERER)
        self.assertEqual(st.session_state[SESSION_PENDING_KEY]["insight_id"], "pa:run-b")
        self.assertIn("run B executive", st.session_state[SESSION_PENDING_KEY]["conclusion"])
        self.assertTrue(should_render_practice_log_full_report(st))

    def test_ami_insight_only_url_derives_run_id(self) -> None:
        st = _St({"suite_ami_insight": "pa:run-b"})
        with patch(
            "applied_math_return_insight.load_applied_math_insight",
            return_value={
                "insight_id": "pa:run-b",
                "conclusion": "today",
                "context_snapshot": {"analysis_run_id": "run-b"},
            },
        ):
            ok = apply_ami_insight_from_query(st, "applied_intelligence")
        self.assertTrue(ok)
        self.assertEqual(st.session_state.get("_suite_practice_analysis_run_id"), "run-b")
        self.assertTrue(st.session_state.get("_ami_practice_log_stale_fallback_blocked"))

    def test_hydrate_from_url_reapplies_insight_when_resume_flag_set(self) -> None:
        from suite_resume_launch import hydrate_applied_intelligence_from_url

        st = _St(
            {
                "suite_resume": "ai:practice_log_analysis:q-stable",
                "suite_practice_analysis_run_id": "run-b",
                "suite_ami_insight": "pa:run-b",
            }
        )
        st.session_state["_suite_resume_launch_applied_intelligence"] = True
        st.session_state[SESSION_PENDING_KEY] = {
            "insight_id": "pa:run-a",
            "conclusion": "yesterday",
            "context_snapshot": {"analysis_run_id": "run-a"},
        }
        st.session_state["_ami_hydrated_insight_id"] = "pa:run-a"
        with patch("suite_analytical_question.hydrate_applied_intelligence_session"):
            with patch(
                "applied_math_return_insight.load_applied_math_insight",
                return_value={
                    "insight_id": "pa:run-b",
                    "conclusion": "today",
                    "context_snapshot": {"analysis_run_id": "run-b"},
                },
            ):
                self.assertTrue(hydrate_applied_intelligence_from_url(st))
        self.assertEqual(st.session_state[SESSION_PENDING_KEY]["insight_id"], "pa:run-b")
        self.assertEqual(st.session_state.get("_ami_hydrated_insight_id"), "pa:run-b")

    def test_load_suite_context_uses_run_id_not_question_id(self) -> None:
        st = _St({"suite_practice_analysis_run_id": "run-b"})
        st.session_state["_suite_ai_question_id"] = "q-stable"
        st.session_state["_suite_ai_context"] = json.dumps(
            {"progress_report": {"executive_summary": "stale session"}}
        )
        fresh_ctx = {
            "user_request": "analyze_practice",
            "handoff_kind": "practice_log_analysis",
            "analysis_run_id": "run-b",
            "report_generated_at": "2026-06-29T01:42:00+00:00",
            "progress_report": {"executive_summary": "run B"},
        }
        with patch("components.problem_solving.st", st):
            with patch(
                "suite_analytical_question.load_analytical_question_payload",
                return_value={"context": fresh_ctx, "question_id": "q-stable", "source_app": "music"},
            ):
                preloaded, _source, _page, ctx = _load_suite_context()
        self.assertIn("Music Practice Log Analysis", preloaded)
        self.assertEqual(ctx.get("progress_report", {}).get("executive_summary"), "run B")


if __name__ == "__main__":
    unittest.main()
