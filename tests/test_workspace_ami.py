"""Workspace isolation for AMI cloud persistence (Daniel vs Ariel)."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from suite_account import load_saved_items, remember_saved_item, scoped_storage_app
from suite_user_persistence import load_user_state, save_user_state
from suite_workspace import scoped_cloud_app_id, set_active_workspace_id


class TestAmiScopedCloudKeys(unittest.TestCase):
    def test_daniel_ami_legacy_key(self) -> None:
        with patch("suite_workspace.resolve_workspace_id", return_value="daniel"):
            self.assertEqual(scoped_cloud_app_id("applied_intelligence"), "applied_intelligence")

    def test_ariel_ami_namespaced_key(self) -> None:
        with patch("suite_workspace.resolve_workspace_id", return_value="ariel"):
            self.assertEqual(scoped_cloud_app_id("applied_intelligence"), "applied_intelligence__ariel")


class TestAmiSavedItemsScoping(unittest.TestCase):
    def _mock_storage(self) -> MagicMock:
        storage = MagicMock()
        storage.upsert_saved_item.return_value = {"write_mode": "upsert"}
        storage.load_saved_items.return_value = []
        return storage

    def test_question_blob_scoped_per_workspace(self) -> None:
        storage = self._mock_storage()
        with patch.dict(sys.modules, {"suite_storage": storage}), patch(
            "suite_workspace.resolve_workspace_id", return_value="ariel"
        ):
            remember_saved_item(
                "applied_intelligence",
                "analytical_question_context",
                "q-ariel-1",
                title="Ariel AMI question",
                payload={"question_id": "q-ariel-1", "question": "Test"},
            )
        self.assertEqual(storage.upsert_saved_item.call_args[0][0], "applied_intelligence__ariel")

    def test_ariel_load_uses_namespaced_key_only(self) -> None:
        storage = self._mock_storage()
        with patch.dict(sys.modules, {"suite_storage": storage}), patch(
            "suite_workspace.resolve_workspace_id", return_value="ariel"
        ):
            load_saved_items(app="applied_intelligence", item_type="applied_math_insight", limit=10)
        storage.load_saved_items.assert_called_once_with(
            app="applied_intelligence__ariel", item_type="applied_math_insight", limit=10
        )

    def test_insight_dismissal_scoped(self) -> None:
        storage = self._mock_storage()
        with patch.dict(sys.modules, {"suite_storage": storage}), patch(
            "suite_workspace.resolve_workspace_id", return_value="daniel"
        ):
            remember_saved_item(
                "applied_intelligence",
                "applied_math_insight_dismissal",
                "insight-d1",
                title="Dismissed",
                payload={"insight_id": "insight-d1"},
            )
        self.assertEqual(storage.upsert_saved_item.call_args[0][0], "applied_intelligence")


class TestAmiResumeItemScoping(unittest.TestCase):
    def test_upsert_resume_uses_scoped_app_key(self) -> None:
        with patch("suite_storage_supabase._request") as req_mock, patch(
            "suite_workspace.resolve_workspace_id", return_value="ariel"
        ), patch("suite_storage_supabase._cloud_user_id", return_value="user-1"):
            from suite_storage_supabase import upsert_resume_item

            upsert_resume_item(
                "applied_intelligence",
                "ai:question:q-test",
                title="Continue AMI question",
                subtitle="ctx",
                action_url="https://example.test/ami",
            )
        body = req_mock.call_args.kwargs.get("json_body")
        self.assertEqual(body.get("app"), "applied_intelligence__ariel")

    def test_load_active_resume_items_filters_workspace(self) -> None:
        with patch("suite_storage_supabase._request") as req_mock, patch(
            "suite_workspace.resolve_workspace_id", return_value="ariel"
        ), patch("suite_storage_supabase._scoped_user_id", return_value="user-1"):
            req_mock.return_value = []
            from suite_storage_supabase import load_active_resume_items

            load_active_resume_items(limit=5, app="applied_intelligence")
        params = req_mock.call_args.kwargs.get("params")
        self.assertEqual(params.get("app"), "in.(applied_intelligence__ariel)")


class TestAmiDiskIsolation(unittest.TestCase):
    def test_daniel_and_ariel_ami_disk_separate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            data = Path(tmp)
            with patch("suite_workspace.DATA_DIR", data), patch("suite_user_persistence.DATA_DIR", data):
                with patch("suite_workspace.resolve_workspace_id", return_value="daniel"):
                    save_user_state(
                        "applied_intelligence",
                        {"_suite_ai_question": "Daniel AMI question", "view_mode": "Solve a Problem"},
                    )
                with patch("suite_workspace.resolve_workspace_id", return_value="ariel"):
                    save_user_state(
                        "applied_intelligence",
                        {"_suite_ai_question": "Ariel AMI question", "view_mode": "Solve a Problem"},
                    )
                with patch("suite_workspace.resolve_workspace_id", return_value="daniel"):
                    daniel, _ = load_user_state("applied_intelligence")
                with patch("suite_workspace.resolve_workspace_id", return_value="ariel"):
                    ariel, _ = load_user_state("applied_intelligence")

                self.assertIn("Daniel", json.dumps(daniel))
                self.assertNotIn("Ariel", json.dumps(daniel))
                self.assertIn("Ariel", json.dumps(ariel))
                self.assertNotIn("Daniel", json.dumps(ariel))


class TestWorkspaceSwitchClearsAmiSession(unittest.TestCase):
    def test_switching_workspace_clears_ami_session_keys(self) -> None:
        class FakeState(dict):
            pass

        st = type("St", (), {"session_state": FakeState(), "query_params": {}})()
        set_active_workspace_id(st, "daniel")
        st.session_state["_ami_pending_insight"] = {"question": "Daniel"}
        st.session_state["_suite_ai_question"] = "Daniel Q"
        with patch("suite_workspace.persist_active_workspace_id"), patch(
            "applied_intelligence_persistent_state.restore_applied_intelligence_disk_state_once"
        ) as restore_mock, patch("applied_math_return_insight.sync_dismissed_insights_from_cloud") as dismiss_mock:
            set_active_workspace_id(st, "ariel")
        self.assertNotIn("_ami_pending_insight", st.session_state)
        self.assertNotIn("_suite_ai_question", st.session_state)
        restore_mock.assert_called_once()
        dismiss_mock.assert_called_once()


if __name__ == "__main__":
    unittest.main()
