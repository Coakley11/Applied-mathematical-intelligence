"""Tests for AMI persistence diagnostics and disk-shell restore safeguards."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import applied_intelligence_persistent_state as aips
from applied_intelligence_persistence_diagnostics import build_ami_persistence_snapshot
from suite_user_persistence import save_user_state, state_file_path


class _FakeSessionState(dict):
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

    def __setattr__(self, name, value):
        self[name] = value

    def keys(self):
        return super().keys()


class _FakeSt:
    def __init__(self) -> None:
        self.session_state = _FakeSessionState()


class TestDiskShellRestoreSafeguards(unittest.TestCase):
    def test_disk_shell_restore_locks_fingerprint_and_blocks_autosave(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            data = Path(tmp)
            with patch("suite_workspace.DATA_DIR", data), patch("suite_user_persistence.DATA_DIR", data):
                save_user_state(
                    "applied_intelligence",
                    {
                        "view_mode": "Solve a Problem",
                        "ps_area_id": "finance",
                        "_ami_control_state": {"ami_solver_beta_ret": -4.0},
                    },
                    workspace_id="daniel",
                )
                st = _FakeSt()
                with patch("suite_workspace.resolve_workspace_id", return_value="daniel"):
                    restored = aips.restore_applied_intelligence_disk_shell(st)
                self.assertTrue(restored)
                self.assertEqual(st.session_state.get("view_mode"), "Solve a Problem")
                self.assertEqual(st.session_state.get("ps_area_id"), "finance")
                self.assertTrue(st.session_state.get("_suite_autosave_blocked::applied_intelligence"))
                self.assertTrue(st.session_state.get("_suite_restored_state_fp::applied_intelligence"))


class TestPersistenceDiagnostics(unittest.TestCase):
    def test_snapshot_reports_disk_path_and_session_values(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            data = Path(tmp)
            with patch("suite_workspace.DATA_DIR", data), patch("suite_user_persistence.DATA_DIR", data):
                save_user_state(
                    "applied_intelligence",
                    {"view_mode": "Solve a Problem", "ps_area_id": "sports"},
                    workspace_id="daniel",
                )
                st = _FakeSt()
                st.session_state["view_mode"] = "Solve a Problem"
                st.session_state["ps_area_id"] = "sports"
                with patch("suite_workspace.resolve_workspace_id", return_value="daniel"):
                    snap = build_ami_persistence_snapshot(st, phase="test")
                self.assertEqual(snap["active_workspace_id"], "daniel")
                self.assertTrue(snap["disk_file_exists"])
                self.assertIn("applied_intelligence_user_state.json", snap["workspace_disk_path"])
                self.assertEqual(snap["session_view_mode"], "Solve a Problem")
                self.assertEqual(snap["disk_ps_area_id"], "sports")
                blob = json.loads(
                    state_file_path("applied_intelligence", "daniel").read_text(encoding="utf-8")
                )
                self.assertEqual(blob["state"]["ps_area_id"], "sports")


if __name__ == "__main__":
    unittest.main()
