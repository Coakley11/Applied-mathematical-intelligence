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
        import suite_account as sa

        fake = MagicMock(name="suite_storage_supabase")

        def _import(name, *args, **kwargs):
            if name == "suite_storage":
                raise ImportError("missing")
            if name == "suite_storage_supabase":
                return fake
            return __import__(name, *args, **kwargs)

        with patch("builtins.__import__", side_effect=_import):
            self.assertIs(sa._import_storage(), fake)

    def test_remember_saved_item_uses_resolved_storage(self) -> None:
        import suite_account as sa

        storage = MagicMock()
        with patch.object(sa, "_import_storage", return_value=storage):
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
