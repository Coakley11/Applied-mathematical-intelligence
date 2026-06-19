"""suite_account storage backend resolution for standalone AMI deploys."""

from __future__ import annotations

import sys
import unittest
from unittest.mock import MagicMock, patch


class TestSuiteAccountStorage(unittest.TestCase):
    def test_import_storage_prefers_suite_storage_when_present(self) -> None:
        import suite_account as sa

        fake = MagicMock(name="suite_storage")
        with patch.dict(sys.modules, {"suite_storage": fake}):
            self.assertIs(sa._import_storage(), fake)

    def test_import_storage_falls_back_to_supabase(self) -> None:
        import builtins

        import suite_account as sa

        fake = MagicMock(name="suite_storage_supabase")
        real_import = builtins.__import__

        def custom_import(name, globals=None, locals=None, fromlist=(), level=0):
            if name == "suite_storage_config":
                mod = real_import(name, globals, locals, fromlist, level)
                mod.cloud_storage_enabled = lambda: False
                return mod
            if name == "suite_storage":
                raise ImportError("missing")
            if name == "suite_storage_supabase":
                return fake
            return real_import(name, globals, locals, fromlist, level)

        with patch("builtins.__import__", side_effect=custom_import):
            self.assertIs(sa._import_storage(), fake)

    def test_remember_saved_item_uses_resolved_storage(self) -> None:
        import suite_account as sa

        storage = MagicMock()
        with patch.object(sa, "_import_storage", return_value=storage), patch(
            "suite_workspace.resolve_workspace_id", return_value="daniel"
        ):
            sa.remember_saved_item(
                "investment",
                "applied_math_insight",
                "abc123",
                title="Test insight",
                payload={"insight_id": "abc123"},
            )
        storage.upsert_saved_item.assert_called_once_with(
            "investment",
            "applied_math_insight",
            "abc123",
            title="Test insight",
            payload={"insight_id": "abc123"},
        )

    def test_remember_saved_item_scopes_ariel_workspace(self) -> None:
        import suite_account as sa

        storage = MagicMock()
        with patch.object(sa, "_import_storage", return_value=storage), patch(
            "suite_workspace.resolve_workspace_id", return_value="ariel"
        ):
            sa.remember_saved_item(
                "applied_intelligence",
                "applied_math_insight",
                "abc123",
                title="Test",
                payload={},
            )
        self.assertEqual(storage.upsert_saved_item.call_args[0][0], "applied_intelligence__ariel")

    def test_load_saved_items_uses_resolved_storage(self) -> None:
        import suite_account as sa

        storage = MagicMock()
        storage.load_saved_items.return_value = [{"item_key": "q1", "payload": {}}]
        with patch.object(sa, "_import_storage", return_value=storage), patch(
            "suite_workspace.resolve_workspace_id", return_value="ariel"
        ):
            rows = sa.load_saved_items(app="baseball", item_type="analytical_question_context", limit=5)
        self.assertEqual(len(rows), 1)
        storage.load_saved_items.assert_called_once_with(
            app="baseball__ariel", item_type="analytical_question_context", limit=5
        )

    def test_remember_saved_item_returns_write_result(self) -> None:
        import suite_account as sa

        storage = MagicMock()
        storage.upsert_saved_item.return_value = {
            "write_mode": "upsert",
            "duplicate_handled": False,
        }
        with patch.object(sa, "_import_storage", return_value=storage):
            result = sa.remember_saved_item(
                "investment",
                "applied_math_insight",
                "abc123",
                title="Test",
                payload={},
            )
        self.assertEqual(result["write_mode"], "upsert")


if __name__ == "__main__":
    unittest.main()
