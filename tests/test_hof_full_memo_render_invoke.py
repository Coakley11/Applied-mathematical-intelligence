"""Prove AMI invokes render_hof_case_full_analysis when HOF renderer is selected."""

from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch

from suite_analytical_question import (
    render_applied_intelligence_solve_problem_content,
    render_hof_case_solve_problem_handoff,
    should_render_hof_full_memo_content,
)


class HofFullMemoRenderInvokeTests(unittest.TestCase):
    def _sample_packet(self) -> dict:
        return {
            "target_player": "Freddie Freeman",
            "hof_case_summary": (
                "Hall of Fame statistical case for Freddie Freeman · cohort 43/87 HOF (49.4%) "
                "· #56 in cohort by HR · primary position 1B"
            ),
            "hall_of_famers_returned": 43,
            "total_players_returned": 87,
            "hall_of_fame_rate_pct": 49.4,
            "target_rank": 56,
            "sort_stat": "HR",
            "primary_position": "1B",
            "mode": "hall_of_fame_case",
        }

    def test_should_render_hof_full_memo_content_from_selected_renderer(self) -> None:
        st = MagicMock()
        st.session_state = {"_suite_ai_selected_renderer": "render_hof_case_full_analysis"}
        self.assertTrue(should_render_hof_full_memo_content(st))

    def test_handoff_invokes_full_renderer_and_records_entered(self) -> None:
        st = MagicMock()
        st.session_state = {
            "_suite_hof_case": True,
            "_hof_case_packet": self._sample_packet(),
            "_hof_case_verdict": {},
            "_suite_ai_selected_renderer": "render_hof_case_full_analysis",
        }
        st.markdown = MagicMock()
        st.caption = MagicMock()

        full_memo = (
            "### Verdict: Borderline\n\n"
            "Freddie Freeman's statistical Hall of Fame case is **Borderline** — evaluated at 1B.\n\n"
            "#### Statistical case\n"
            "**Strongest evidence**\n"
            "- Elite on-base profile within this cohort.\n"
            "- Sustained run production relative to inducted first basemen.\n\n"
            "**Weakest evidence / cautions**\n"
            "- Limited relative value by home runs — #56 of 87 in cohort by home runs.\n\n"
            "**Position & era context**\n"
            "- First base is offense-first — inducted 1Bs typically combine sustained power and/or elite on-base value.\n\n"
            "**Comparison notes**\n"
            "- Compare to inducted peers and non-inducted comps for context.\n\n"
            "#### Final takeaway\n"
            "**Borderline** on the Hall of Fame Statistical Case Score — not induction odds.\n\n"
            "*Statistical Hall of Fame case analysis only — not true Hall of Fame induction odds.*"
        )

        def _fake_render(_st, packet, *, verdict=None):
            _st.session_state["_hof_case_memo_render_diag"] = {
                "render_hof_case_full_analysis_entered": True,
                "case_memo_present": True,
                "case_memo_len": len(full_memo),
                "memo_is_full": True,
                "fallback_reason": "",
            }
            _st.markdown(full_memo)
            return True

        with patch("hof_case_analysis.render_hof_case_full_analysis", side_effect=_fake_render):
            ok = render_hof_case_solve_problem_handoff(st)

        self.assertTrue(ok)
        diag = st.session_state["_suite_ai_hydrate_diag"]
        self.assertEqual(diag.get("selected_renderer"), "render_hof_case_full_analysis")
        self.assertTrue(diag.get("render_hof_case_full_analysis_entered"))
        self.assertTrue(diag.get("case_memo_present"))
        self.assertGreater(int(diag.get("case_memo_len") or 0), 500)
        self.assertTrue(diag.get("memo_is_full"))
        self.assertEqual(diag.get("fallback_reason"), "")

    def test_solve_problem_content_routes_selected_renderer_to_full_memo(self) -> None:
        st = MagicMock()
        st.session_state = {
            "_suite_hof_case": True,
            "_hof_case_packet": self._sample_packet(),
            "_suite_ai_selected_renderer": "render_hof_case_full_analysis",
        }
        st.markdown = MagicMock()
        st.caption = MagicMock()

        with patch("hof_case_analysis.render_hof_case_full_analysis", return_value=True) as mock_full:
            ok = render_applied_intelligence_solve_problem_content(st)

        self.assertTrue(ok)
        mock_full.assert_called_once()

    def test_hof_case_analysis_imports_without_hall_of_fame_data(self) -> None:
        import importlib
        import pathlib
        import sys

        root = pathlib.Path(__file__).resolve().parents[1]
        source = (root / "hof_case_analysis.py").read_text(encoding="utf-8")
        self.assertNotIn("from hall_of_fame_data import", source)
        self.assertNotIn("import hall_of_fame_data", source)

        sys.modules.pop("hof_case_analysis", None)
        mod = importlib.import_module("hof_case_analysis")
        self.assertEqual(mod.CASE_SCORE_LABEL, "Hall of Fame Statistical Case Score")
        self.assertEqual(mod.CASE_SCORE_BUCKETS, ("Weak", "Borderline", "Solid", "Strong", "Very Strong"))
        self.assertEqual(mod.MEMO_QUALITY_VERSION, "hof_memo_quality_v2")
        self.assertTrue(callable(mod.render_hof_case_full_analysis))
        self.assertTrue(callable(mod.compose_hof_statistical_case))
        self.assertNotIn("hall_of_fame_data", sys.modules.get("hof_case_analysis").__dict__)

    def test_render_hof_case_full_analysis_runs_without_hall_of_fame_data(self) -> None:
        import importlib

        mod = importlib.import_module("hof_case_analysis")
        st = MagicMock()
        st.session_state = {}
        st.markdown = MagicMock()
        st.caption = MagicMock()
        packet = {
            **self._sample_packet(),
            "target_career_stats": {"HR": 569, "H": 3020, "RBI": 1834, "2B": 585, "G": 2831, "R": 1663},
            "cohort_strength_stats": ["HR", "H", "RBI"],
            "target_cohort_ranks": {"HR": {"rank": 10, "of": 87, "value": 569, "percentile_top": 90, "tier": "top 10%"}},
        }
        ok = mod.render_hof_case_full_analysis(st, packet)
        self.assertTrue(ok)
        st.markdown.assert_called()
        rendered = " ".join(str(c.args[0]) for c in st.markdown.call_args_list if c.args)
        self.assertIn("569", rendered)
        self.assertIn("Verdict", rendered)
        analysis = mod.compose_hof_statistical_case(packet)
        self.assertEqual(
            (analysis.get("case_memo") or {}).get("memo_quality_version"),
            mod.MEMO_QUALITY_VERSION,
        )


if __name__ == "__main__":
    unittest.main()
