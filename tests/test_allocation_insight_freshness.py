"""Canonical insight freshness — slider-refreshed allocation beats stale phase2g blobs."""

from __future__ import annotations

import unittest

from applied_math_return_insight import (
    _insight_blob_restore_score,
    _pick_freshest_canonical_insight,
)


class TestAllocationInsightFreshness(unittest.TestCase):
    def test_refreshed_phase2j_beats_stale_phase2g_with_portfolio_sections(self) -> None:
        stale = {
            "conclusion": "Old allocation answer.",
            "solver_build_id": "investment-ami-v2-phase2g-allocation-inflation1",
            "canonical_instant": True,
            "analyst_sections": {
                "proposed_portfolio": "| VNQ | 50% |",
                "portfolio_comparison": "| VNQ | 10% | 50% |",
            },
            "scenario_params": {
                "allocation_overrides": {"BND": 40.0},
                "allocation_reallocations": [{"from_ticker": "VTI", "amount_pct": 40.0, "to_ticker": "VNQ"}],
            },
        }
        refreshed = {
            "conclusion": "Refreshed allocation answer.",
            "solver_build_id": "investment-ami-v2-phase2j-allocation-diag1",
            "canonical_instant": True,
            "scenario_refreshed_at": "2026-06-18T12:00:00+00:00",
            "allocation_engine_diag": {"module_build_id": "investment-ami-v2-phase2j-allocation-diag1"},
            "analyst_sections": {
                "proposed_portfolio": "| BND | 40% |",
                "portfolio_comparison": "| BND | 30% | 40% |",
            },
            "scenario_params": {
                "allocation_overrides": {"BND": 40.0},
                "allocation_increase_funding": [{"to_ticker": "BND", "from_ticker": "VNQ", "amount_pct": 10.0}],
                "allocation_reallocations": [],
            },
        }
        self.assertGreater(_insight_blob_restore_score(refreshed), _insight_blob_restore_score(stale))
        picked = _pick_freshest_canonical_insight([stale, refreshed])
        self.assertEqual(picked.get("solver_build_id"), refreshed["solver_build_id"])


if __name__ == "__main__":
    unittest.main()
