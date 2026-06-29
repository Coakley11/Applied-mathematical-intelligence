"""AMI Practice Log report rendering polish tests."""

from __future__ import annotations

import unittest

from practice_progress_report_render import format_progress_report_markdown, render_progress_report_ui


class _FakeSt:
    def __init__(self) -> None:
        self.containers = 0
        self.markdown_calls: list[str] = []

    def markdown(self, text: str, *args, **kwargs) -> None:
        self.markdown_calls.append(str(text))

    def caption(self, text: str) -> None:
        self.markdown_calls.append(str(text))

    def container(self, *, border: bool = False):
        self.containers += 1
        return self

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


class TestPracticeProgressReportRender(unittest.TestCase):
    def test_orphan_tone_filtered_from_markdown(self) -> None:
        md = format_progress_report_markdown(
            {
                "title": "Analyze My Practice — Progress Report",
                "executive_summary": "Summary line.",
                "recommended_next_practice_plan": ["tone", "Record one short pass of Say."],
                "evidence_used": "Evidence used: 2 practice logs.",
            }
        )
        self.assertNotIn("\ntone\n", f"\n{md}\n")
        self.assertNotIn("- tone", md)
        self.assertIn("Record one short pass", md)

    def test_render_ui_uses_bordered_sections(self) -> None:
        st = _FakeSt()
        render_progress_report_ui(
            st,
            {
                "title": "Analyze My Practice — Progress Report",
                "executive_summary": "Summary line.",
                "practice_activity": ["Logged 2 sessions."],
                "evidence_used": "Evidence used: 2 practice logs.",
            },
        )
        self.assertGreaterEqual(st.containers, 2)
        self.assertTrue(any("Summary line." in call for call in st.markdown_calls))


if __name__ == "__main__":
    unittest.main()
