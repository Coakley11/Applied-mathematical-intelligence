"""Integration tests — return insight hydration, page gating, state preservation."""

from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch

from applied_math_return_insight import (
    SESSION_PENDING_KEY,
    apply_ami_insight_from_query,
    build_return_insight_payload,
    build_source_app_return_url,
    should_render_insight_on_page,
    store_applied_math_insight,
)
from components.applied_math_solvers import SolverResult


class _FakeSessionState(dict):
    def get(self, key, default=None):
        return super().get(key, default)


class TestInsightPageGating(unittest.TestCase):
    def test_shows_on_matching_baseball_page(self) -> None:
        insight = {"source_app": "baseball", "source_page": "Comparison Tool", "conclusion": "Yes"}
        self.assertTrue(
            should_render_insight_on_page("baseball", "Comparison Tool", insight)
        )

    def test_hides_on_unrelated_page(self) -> None:
        insight = {"source_app": "baseball", "source_page": "Comparison Tool", "conclusion": "Yes"}
        self.assertFalse(
            should_render_insight_on_page("baseball", "Leaderboards", insight)
        )

    def test_nba_live_game_center_normalized(self) -> None:
        insight = {"source_app": "nba", "source_page": "Live Game Center", "conclusion": "Edge"}
        self.assertTrue(
            should_render_insight_on_page("nba", "🔴 Live Game Center", insight)
        )


class TestInsightHydration(unittest.TestCase):
    def test_apply_from_query_loads_pending_insight(self) -> None:
        st = MagicMock()
        st.session_state = _FakeSessionState()
        st.query_params = {"suite_ami_insight": "abc123def", "suite_page": "Comparison Tool"}

        sample = {
            "insight_id": "abc123def",
            "question": "Will Soto outscore Judge?",
            "conclusion": "Soto projects ahead.",
            "source_page": "Comparison Tool",
        }
        with patch(
            "applied_math_return_insight.load_applied_math_insight",
            return_value=sample,
        ):
            applied = apply_ami_insight_from_query(st, "baseball")

        self.assertTrue(applied)
        self.assertEqual(st.session_state[SESSION_PENDING_KEY]["insight_id"], "abc123def")

    def test_apply_does_not_run_twice(self) -> None:
        st = MagicMock()
        st.session_state = _FakeSessionState({"_ami_insight_applied_baseball": True})
        st.query_params = {"suite_ami_insight": "x"}
        self.assertFalse(apply_ami_insight_from_query(st, "baseball"))


class TestReturnUrlAndPayload(unittest.TestCase):
    def test_return_url_has_insight_param(self) -> None:
        insight = build_return_insight_payload(
            question="Should I rebalance?",
            source_app="investment",
            source_page="Portfolio Health",
            question_id="q1",
            result=SolverResult(short_answer="Hold for now.", confidence_pct=65),
        )
        url = build_source_app_return_url(insight, resume_key="portfolio:health")
        self.assertIn("suite_ami_insight=", url)
        self.assertIn("investment", url)

    def test_store_returns_insight_id(self) -> None:
        insight = build_return_insight_payload(
            question="Test",
            source_app="investment",
            source_page="Portfolio Health",
            result=SolverResult(short_answer="OK"),
        )
        with patch("suite_account.remember_saved_item") as mock_save:
            with patch("suite_activity_client.record_activity"):
                iid = store_applied_math_insight(insight)
        self.assertTrue(iid)
        self.assertGreaterEqual(mock_save.call_count, 1)
        self.assertEqual(mock_save.call_args.kwargs.get("payload", {}).get("insight_id"), iid)


class TestResumeLaunchPreservesState(unittest.TestCase):
    def test_baseball_resume_sets_players_not_insight_clear(self) -> None:
        st = MagicMock()
        st.session_state = _FakeSessionState(
            {
                "sig_player_a_clean": "Existing",
                "_ami_pending_insight": {"conclusion": "keep me until page render"},
            }
        )
        st.query_params = {
            "suite_resume": "compare:Judge:Soto",
            "suite_page": "Comparison Tool",
            "suite_player_a": "Aaron Judge",
            "suite_player_b": "Juan Soto",
        }

        from suite_resume_launch import apply_suite_resume_launch

        apply_suite_resume_launch(st, "baseball")
        self.assertEqual(st.session_state.get("pending_sig_player_a"), "Aaron Judge")
        self.assertIn("_ami_pending_insight", st.session_state)


if __name__ == "__main__":
    unittest.main()
