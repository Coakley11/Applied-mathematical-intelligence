"""AMI Practice Log report rendering polish tests."""

from __future__ import annotations

import unittest

from practice_progress_report_render import format_progress_report_markdown, render_progress_report_ui


class _FakeSt:
    def __init__(self) -> None:
        self.containers = 0
        self.markdown_calls: list[str] = []
        self.expanders: list[tuple[str, bool]] = []

    def markdown(self, text: str, *args, **kwargs) -> None:
        self.markdown_calls.append(str(text))

    def caption(self, text: str) -> None:
        self.markdown_calls.append(str(text))

    def container(self, *, border: bool = False):
        self.containers += 1
        return self

    def expander(self, label, *, expanded=False):
        self.expanders.append((str(label), expanded))
        return self

    def json(self, *_args, **_kwargs) -> None:
        pass

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

    def test_render_ui_shows_coach_summary_and_chips(self) -> None:
        st = _FakeSt()
        render_progress_report_ui(
            st,
            {
                "title": "Analyze My Practice — Progress Report",
                "executive_summary": "You logged 2 sessions totaling 60 minutes.",
                "evidence_used": (
                    "Evidence used: **2** practice logs, **4** saved upload analyses, "
                    "**2** tone takes, **1** saved export(s), **0** linked analyzed export(s). "
                    "Date range: **Jun 22–Jun 29, 2026**."
                ),
            },
            updated_at="2026-06-29T13:35:00+00:00",
        )
        joined = " ".join(st.markdown_calls)
        self.assertIn("Coach summary", joined)
        self.assertIn("You logged 2 sessions", joined)
        self.assertGreaterEqual(st.containers, 2)

    def test_data_safety_collapsed_in_normal_mode(self) -> None:
        st = _FakeSt()
        render_progress_report_ui(
            st,
            {
                "executive_summary": "Summary.",
                "data_safety_confirmation": {
                    "raw_audio_excluded": True,
                    "base64_excluded": True,
                    "deleted_items_excluded": True,
                },
            },
            dev_mode=False,
        )
        self.assertEqual(len(st.expanders), 1)
        self.assertIn("Data safety", st.expanders[0][0])
        self.assertFalse(st.expanders[0][1])

    def test_eastern_time_in_updated_caption(self) -> None:
        st = _FakeSt()
        render_progress_report_ui(
            st,
            {"executive_summary": "Summary."},
            updated_at="2026-06-29T13:35:00+00:00",
        )
        joined = " ".join(st.markdown_calls)
        self.assertIn("Updated", joined)
        self.assertIn("ET", joined)


if __name__ == "__main__":
    unittest.main()
