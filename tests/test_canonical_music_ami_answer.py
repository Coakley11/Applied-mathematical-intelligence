"""AMI renders stored Music canonical insight before re-solving."""

from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch

from components.applied_math_solver_ui import _load_canonical_music_insight, render_suite_solver_answer


class TestCanonicalMusicAmiAnswer(unittest.TestCase):
    def test_load_canonical_from_context_instant_insight(self) -> None:
        st = MagicMock()
        st.session_state = {}
        ctx = {
            "instant_insight": {
                "conclusion": "Songs similar to Perfect...",
                "canonical_instant": True,
            }
        }
        loaded = _load_canonical_music_insight(st, ctx)
        self.assertEqual(loaded.get("conclusion"), "Songs similar to Perfect...")

    def test_render_suite_solver_answer_uses_canonical_for_music(self) -> None:
        st = MagicMock()
        st.session_state = {}
        st.caption = MagicMock()
        st.markdown = MagicMock()
        ctx = {
            "instant_insight": {
                "conclusion": "15-minute practice split",
                "method": "Time-boxed blocks",
                "canonical_instant": True,
                "solver_build_id": "music-ami-v5-canonical-insight",
            }
        }
        trace = render_suite_solver_answer(
            st,
            question="I have 15 minutes to practice",
            source_app="music",
            source_page="practice",
            context=ctx,
        )
        self.assertEqual(trace.renderer_path, "render_canonical_music_insight")
        self.assertIn("15-minute", trace.conclusion)


if __name__ == "__main__":
    unittest.main()
