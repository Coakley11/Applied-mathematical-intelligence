"""AMI normal mode — hide workspace/account diagnostics on Practice Log report."""

from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch


class TestPracticeLogAmiNormalMode(unittest.TestCase):
    def test_suite_question_view_skips_homepage_header_for_practice_log(self) -> None:
        st = MagicMock()
        st.session_state = {"_suite_ai_selected_renderer": "render_practice_log_full_report"}
        with patch("components.problem_solving.st", st):
            with patch(
                "components.problem_solving._load_suite_context",
                return_value=("Analyze my practice history.", "music", "log", {}),
            ):
                with patch(
                    "suite_analytical_question.should_render_practice_log_full_report",
                    return_value=True,
                ):
                    with patch("components.applied_math_suite_page.render_suite_question_page_header") as header:
                        from components.problem_solving import _render_suite_question_view

                        _render_suite_question_view()
                        header.assert_not_called()

    def test_practice_log_handoff_skips_dev_diagnostics_in_normal_mode(self) -> None:
        st = MagicMock()
        st.session_state = {
            "_suite_ai_context": (
                '{"progress_report":{"executive_summary":"You logged 2 sessions."},'
                '"report_generated_at":"2026-06-29T13:35:00+00:00"}'
            ),
        }
        with patch("suite_analytical_question._developer_tools_enabled", return_value=False):
            with patch("components.applied_math_context_diagnostics.render_practice_log_restore_diagnostics") as diag:
                with patch("practice_progress_report_render.render_progress_report_ui") as render_ui:
                    from suite_analytical_question import render_practice_log_solve_problem_handoff

                    self.assertTrue(render_practice_log_solve_problem_handoff(st))
                    diag.assert_not_called()
                    render_ui.assert_called_once()
                    self.assertFalse(render_ui.call_args.kwargs.get("dev_mode"))


if __name__ == "__main__":
    unittest.main()
