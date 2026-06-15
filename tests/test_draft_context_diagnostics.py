"""Tests for draft context hydration vs solver bundle diagnostics."""

from __future__ import annotations

import unittest

from components.applied_math_context_diagnostics import classify_ami_hydration_status
from components.draft_context_diagnostics import build_draft_context_diagnostics, build_solver_bundle_diagnostics


class TestAmiHydrationClassification(unittest.TestCase):
    def test_missing_url_question_id(self) -> None:
        level, msg = classify_ami_hydration_status({"url_question_id": None, "hydrate_attempted": True})
        self.assertEqual(level, "error")
        self.assertIn("URL question_id missing", msg)

    def test_blob_load_failed_with_qid(self) -> None:
        level, msg = classify_ami_hydration_status(
            {
                "url_question_id": "abc123",
                "hydrate_attempted": True,
                "session_hydrate_source": "none",
                "blob_load_error": "no_blob_context_for_question_id",
            }
        )
        self.assertEqual(level, "error")
        self.assertIn("Blob load failed", msg)


class TestDraftContextDiagnostics(unittest.TestCase):
    def test_hydrated_counts_from_snapshot(self) -> None:
        ctx = {
            "draft_snapshot": {
                "available_players": [
                    {"player": "Cal Raleigh", "Primary Position": "C"},
                    {"player": "Kyle Tucker", "Primary Position": "OF"},
                ],
                "current_pick": 8,
            },
            "player_pool_diagnostics": {"player_pool_source": "position_representative_v1"},
        }
        diag = build_draft_context_diagnostics(ctx, hydrate_source="question_id_blob")
        self.assertEqual(diag["available_players_count_hydrated"], 2)
        self.assertEqual(diag["catchers_in_hydrated_available"], 1)
        self.assertEqual(diag["draft_context_source"], "question_id_blob")
        self.assertEqual(diag["hydrate_source"], "question_id_blob")

    def test_solver_bundle_reads_hydrated_pool(self) -> None:
        ctx = {
            "_debug_question": "Who is the best player available?",
            "available_players": [{"player": "Kyle Tucker", "Primary Position": "OF", "Market Rank": 8}],
            "current_pick": 8,
            "draft_round": 4,
        }
        bundle = build_solver_bundle_diagnostics(ctx)
        self.assertEqual(bundle["bundle_available_count"], 1)
        self.assertEqual(bundle["bundle_pick"], 8)

    def test_sparse_context_empty_bundle(self) -> None:
        ctx = {"workflow": "Fantasy draft", "current_pick": 1, "_debug_question": "Who is the best player available?"}
        hydrated = build_draft_context_diagnostics(ctx, hydrate_source="url_query")
        bundle = build_solver_bundle_diagnostics(ctx)
        self.assertEqual(hydrated["available_players_count_hydrated"], 0)
        self.assertEqual(bundle["bundle_available_count"], 0)
        self.assertEqual(bundle["bundle_pick"], 1)


if __name__ == "__main__":
    unittest.main()
