"""AMI renders stored Investment canonical insight before re-solving."""

from __future__ import annotations

import unittest
from unittest.mock import MagicMock

from components.applied_math_solver_ui import (
    _load_canonical_instant_insight,
    render_suite_solver_answer,
)


class TestCanonicalInvestmentAmiAnswer(unittest.TestCase):
    def test_load_canonical_from_context(self) -> None:
        st = MagicMock()
        st.session_state = {}
        ctx = {
            "instant_insight": {
                "conclusion": "Top position VOO 40% — moderate concentration.",
                "canonical_instant": True,
            }
        }
        loaded = _load_canonical_instant_insight(st, ctx, source_app="investment")
        self.assertIn("VOO", loaded.get("conclusion", ""))

    def test_render_suite_solver_answer_uses_canonical_for_investment(self) -> None:
        st = MagicMock()
        st.session_state = {}
        st.caption = MagicMock()
        st.markdown = MagicMock()
        ctx = {
            "instant_insight": {
                "conclusion": "Technology proxy weight ≈ 35.0%",
                "method": "Tech ETF weights as exposure proxy.",
                "canonical_instant": True,
                "solver_build_id": "investment-ami-v1-phase1",
            }
        }
        trace = render_suite_solver_answer(
            st,
            question="Am I too exposed to tech?",
            source_app="investment",
            source_page="Portfolio Health",
            context=ctx,
        )
        self.assertEqual(trace.renderer_path, "render_canonical_investment_insight")
        self.assertIn("Technology", trace.conclusion)


if __name__ == "__main__":
    unittest.main()
