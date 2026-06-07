"""Return Insight to Source App — v1 payload and URL tests."""

from __future__ import annotations

import unittest
from unittest.mock import MagicMock

from applied_math_return_insight import (
    AppliedMathInsight,
    build_return_insight_payload,
    build_source_app_return_url,
    metrics_for_source_app_return,
)
from components.applied_math_solvers import SolverResult


class TestReturnInsightPayload(unittest.TestCase):
    def test_build_payload_from_solver_result(self) -> None:
        result = SolverResult(
            question="Is VTI too concentrated?",
            short_answer="Yes — top holding exceeds limit.",
            math_idea="Concentration via HHI",
            assumptions=["Weights from Portfolio Health"],
            confidence_pct=82,
            computed={"hhi": 0.28},
            live_metrics={"Top-1": "45%"},
        )
        insight = build_return_insight_payload(
            question="Is VTI too concentrated?",
            source_app="investment",
            source_page="Portfolio Health",
            question_id="abc123",
            result=result,
        )
        self.assertIsInstance(insight, AppliedMathInsight)
        self.assertEqual(insight.source_app, "investment")
        self.assertIn("exceeds", insight.conclusion.lower())
        self.assertEqual(insight.confidence, "high")
        self.assertTrue(insight.insight_id)

    def test_return_url_includes_insight_param(self) -> None:
        insight = build_return_insight_payload(
            question="Will Soto outscore Judge?",
            source_app="baseball",
            source_page="Comparison Tool",
            question_id="q1",
            result=SolverResult(short_answer="Soto projects ahead.", confidence_pct=70),
        )
        url = build_source_app_return_url(
            insight,
            resume_key="compare:Soto:Judge",
            metrics=metrics_for_source_app_return(insight),
        )
        self.assertIn("suite_ami_insight=", url)
        self.assertIn("baseball", url)

    def test_insight_panel_renders_with_session_data(self) -> None:
        from applied_math_return_insight import render_applied_math_insight_panel

        st = MagicMock()
        st.session_state = {
            "_ami_pending_insight": {
                "question": "Test Q",
                "conclusion": "Test conclusion",
                "method": "Draft value edge",
                "assumptions": ["ADP 18"],
                "confidence": "high",
            }
        }
        st.container.return_value.__enter__ = MagicMock(return_value=None)
        st.container.return_value.__exit__ = MagicMock(return_value=None)
        st.expander.return_value.__enter__ = MagicMock(return_value=None)
        st.expander.return_value.__exit__ = MagicMock(return_value=None)
        st.columns.return_value = [MagicMock(), MagicMock()]
        rendered = render_applied_math_insight_panel(st)
        self.assertTrue(rendered)


if __name__ == "__main__":
    unittest.main()
