"""Idempotent suite_saved_items writes (AMI insight store)."""

from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch

from suite_storage_config import SuiteCloudConfig, reset_cloud_config_cache


class TestSuiteStorageSupabaseSavedItems(unittest.TestCase):
    def tearDown(self) -> None:
        reset_cloud_config_cache()

    @patch("suite_storage_supabase._scoped_user_id", return_value="f66b85aa-1192-4f93-a669-d238bcd6858b")
    @patch("suite_storage_supabase._request")
    @patch("suite_storage_config.get_cloud_config")
    def test_upsert_saved_item_uses_on_conflict(
        self,
        mock_cfg: MagicMock,
        mock_req: MagicMock,
        _uid: MagicMock,
    ) -> None:
        mock_cfg.return_value = SuiteCloudConfig(url="https://test.supabase.co", key="secret")
        from suite_storage_supabase import upsert_saved_item

        result = upsert_saved_item(
            "investment",
            "applied_math_insight",
            "edc6ca34de6e4cde",
            title="Applied Investment Insight",
            payload={"insight_id": "edc6ca34de6e4cde"},
        )
        self.assertEqual(result["write_mode"], "upsert")
        self.assertFalse(result["duplicate_handled"])
        mock_req.assert_called_once()
        self.assertEqual(mock_req.call_args.kwargs["params"], {"on_conflict": "user_id,app,item_type,item_key"})

    @patch("suite_storage_supabase._scoped_user_id", return_value="f66b85aa-1192-4f93-a669-d238bcd6858b")
    @patch("suite_storage_supabase._request")
    @patch("suite_storage_config.get_cloud_config")
    def test_upsert_saved_item_recovers_from_duplicate_with_patch(
        self,
        mock_cfg: MagicMock,
        mock_req: MagicMock,
        _uid: MagicMock,
    ) -> None:
        mock_cfg.return_value = SuiteCloudConfig(url="https://test.supabase.co", key="secret")
        mock_req.side_effect = [
            RuntimeError(
                "Supabase POST suite_saved_items failed (409): duplicate key value violates unique constraint"
            ),
            None,
        ]
        from suite_storage_supabase import upsert_saved_item

        result = upsert_saved_item(
            "investment",
            "applied_math_insight",
            "edc6ca34de6e4cde",
            title="Applied Investment Insight",
            payload={"insight_id": "edc6ca34de6e4cde", "source_state": {"source_app": "investment"}},
        )
        self.assertEqual(result["write_mode"], "update")
        self.assertTrue(result["duplicate_handled"])
        self.assertEqual(mock_req.call_count, 2)
        self.assertEqual(mock_req.call_args_list[1][0][0], "PATCH")


if __name__ == "__main__":
    unittest.main()
