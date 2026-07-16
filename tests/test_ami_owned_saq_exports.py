"""Regression: AMI-owned SAQ Solve Problem / HOF / practice-log helpers survive sync."""

from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch


class TestAmiOwnedSaqExports(unittest.TestCase):
    def test_required_exports_present(self) -> None:
        from suite_analytical_question import (
            render_applied_intelligence_solve_problem_content,
            should_render_hof_full_memo_content,
            should_render_practice_log_full_report,
        )

        self.assertTrue(callable(render_applied_intelligence_solve_problem_content))
        self.assertTrue(callable(should_render_hof_full_memo_content))
        self.assertTrue(callable(should_render_practice_log_full_report))

    def test_practice_log_report_gate_false_by_default(self) -> None:
        from suite_analytical_question import should_render_practice_log_full_report

        st = MagicMock()
        st.session_state = {}
        self.assertFalse(should_render_practice_log_full_report(st))

    def test_hof_full_memo_gate_false_by_default(self) -> None:
        from suite_analytical_question import should_render_hof_full_memo_content

        st = MagicMock()
        st.session_state = {}
        self.assertFalse(should_render_hof_full_memo_content(st))

    def test_solve_problem_content_returns_bool(self) -> None:
        from suite_analytical_question import render_applied_intelligence_solve_problem_content

        st = MagicMock()
        st.session_state = {}
        with patch(
            "suite_analytical_question.should_render_hof_full_memo_content",
            return_value=False,
        ), patch(
            "suite_analytical_question.should_render_practice_log_full_report",
            return_value=False,
        ):
            result = render_applied_intelligence_solve_problem_content(st)
        self.assertIsInstance(result, bool)


if __name__ == "__main__":
    unittest.main()
