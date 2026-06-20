"""Tests for AMI cloud sync diagnostics and disk-shell cloud preference."""

from __future__ import annotations

import unittest
from unittest.mock import patch

import applied_intelligence_persistent_state as aips


class _FakeSessionState(dict):
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

    def __setattr__(self, name, value):
        self[name] = value


class _FakeSt:
    def __init__(self) -> None:
        self.session_state = _FakeSessionState()


class TestAmiCloudSync(unittest.TestCase):
    def test_disk_shell_skips_when_cloud_newer(self) -> None:
        st = _FakeSt()
        with patch(
            "suite_cloud_state.load_cloud_full_session",
            return_value=({"view_mode": "Explore a Math Idea", "_ami_ui_state": {"mie_example": "Derivative"}}, "2026-06-20T12:00:00+00:00"),
        ), patch(
            "suite_user_persistence._load_raw",
            return_value=({"view_mode": "Home"}, None, "2026-06-19T12:00:00+00:00"),
        ):
            restored = aips.restore_applied_intelligence_disk_shell(st)
        self.assertFalse(restored)
        self.assertTrue(st.session_state.get("_ami_disk_shell_skipped_for_cloud"))
        self.assertNotIn("view_mode", st.session_state)

    def test_prepare_always_uses_cloud_first(self) -> None:
        st = _FakeSt()
        with patch("applied_intelligence_persistent_state.sync_workspace_protocol") as sync_mock:
            sync_mock.return_value = True
            aips.prepare_applied_intelligence_workspace(st)
        self.assertTrue(sync_mock.call_args.kwargs.get("cloud_first"))

    def test_cloud_sync_snapshot_includes_namespaces(self) -> None:
        from applied_intelligence_cloud_sync_diagnostics import build_ami_cloud_sync_snapshot

        st = _FakeSt()
        with patch("suite_workspace.get_active_workspace_id", return_value="ariel"), patch(
            "suite_workspace.scoped_cloud_app_id",
            side_effect=lambda app, ws=None: f"{app}__{ws or 'ariel'}",
        ), patch("suite_user.get_external_user_id", return_value="suite-test"), patch(
            "suite_user.get_account_user_id",
            return_value="uuid-test",
        ), patch("suite_user.account_mode", return_value="cloud"), patch(
            "suite_cloud_state.load_cloud_full_session",
            return_value=({}, None),
        ), patch("suite_user_persistence._load_raw", return_value=({}, None, None)):
            snap = build_ami_cloud_sync_snapshot(st)
        self.assertEqual(snap["workspace_id"], "ariel")
        self.assertEqual(snap["cloud_write_namespace"], "applied_intelligence__ariel")
        self.assertEqual(snap["suite_user_id"], "suite-test")


if __name__ == "__main__":
    unittest.main()
