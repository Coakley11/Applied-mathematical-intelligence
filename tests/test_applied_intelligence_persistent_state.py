"""Tests for Applied Intelligence suite question persistence."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import applied_intelligence_persistent_state as aips
from suite_user_persistence import save_user_state, state_file_path


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


def test_build_state_persists_suite_ai_question_and_view_mode() -> None:
    st = _FakeSt()
    st.session_state["_suite_ai_question"] = "What is the expected HR rate?"
    st.session_state["_suite_ai_context"] = json.dumps({"player": "Aaron Judge"})
    st.session_state["_suite_ai_source_app"] = "baseball"
    st.session_state["_suite_ai_source_page"] = "Trend Value"
    st.session_state["ps_area_id"] = "sports"

    state = aips.build_applied_intelligence_disk_state(st)

    assert state["view_mode"] == "Solve a Problem"
    assert state["_suite_ai_question"] == "What is the expected HR rate?"
    assert state["_suite_ai_source_app"] == "baseball"
    assert state["ps_library_problem"] == "What is the expected HR rate?"


def test_apply_state_restores_suite_ai_question_and_view_mode() -> None:
    st = _FakeSt()
    saved = {
        "view_mode": "Home",
        "_suite_ai_question": "How volatile is this portfolio?",
        "_suite_ai_context": json.dumps({"tickers": ["SPY", "BND"]}),
        "_suite_ai_source_app": "investment",
        "_suite_ai_source_page": "Portfolio Health",
        "ps_area_id": "finance",
        "ps_library_problem": "How volatile is this portfolio?",
    }

    aips.apply_applied_intelligence_disk_state(st, saved)

    assert st.session_state["view_mode"] == "Solve a Problem"
    assert st.session_state["_suite_ai_question"] == "How volatile is this portfolio?"
    assert st.session_state["_suite_ai_context"] == saved["_suite_ai_context"]
    assert st.session_state["ps_library_problem"] == "How volatile is this portfolio?"


def test_autosave_does_not_skip_when_suite_ai_question_loaded() -> None:
    st = _FakeSt()
    st.session_state["_suite_ai_question"] = "Test question"
    st.session_state["view_mode"] = "Solve a Problem"

    saved: list[dict] = []

    def _fake_autosave(_st, app_id, build_state):
        saved.append(build_state(_st))

    orig = aips.autosave_if_changed
    aips.autosave_if_changed = _fake_autosave
    try:
        aips.autosave_applied_intelligence_state(st)
    finally:
        aips.autosave_if_changed = orig

    assert saved
    assert saved[0]["_suite_ai_question"] == "Test question"
    assert saved[0]["view_mode"] == "Solve a Problem"


def test_reset_clears_suite_ai_question_keys() -> None:
    st = _FakeSt()
    st.session_state.update(
        {
            "view_mode": "Solve a Problem",
            "_suite_ai_question": "Test question",
            "_suite_ai_context": "{}",
            "_suite_ai_source_app": "music",
            "ps_library_problem": "Test question",
            "ps_area_id": "music",
        }
    )

    aips.apply_applied_intelligence_session_defaults(st)

    assert st.session_state.get("view_mode") == "Home"
    assert "_suite_ai_question" not in st.session_state
    assert "ps_library_problem" not in st.session_state


class TestAppliedIntelligenceRefreshRestore(unittest.TestCase):
    def test_refresh_restores_daniel_and_ariel_state_separately(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            data = Path(tmp)
            with patch("suite_workspace.DATA_DIR", data), patch("suite_user_persistence.DATA_DIR", data):
                save_user_state(
                    "applied_intelligence",
                    {
                        "view_mode": "Solve a Problem",
                        "ps_area_id": "finance",
                        "ps_library_problem": "Daniel portfolio volatility question",
                        "_suite_ai_question": "Daniel portfolio volatility question",
                    },
                    workspace_id="daniel",
                )
                save_user_state(
                    "applied_intelligence",
                    {
                        "view_mode": "Solve a Problem",
                        "ps_area_id": "sports",
                        "ps_library_problem": "Ariel sports trend question",
                        "_suite_ai_question": "Ariel sports trend question",
                    },
                    workspace_id="ariel",
                )

                daniel_st = _FakeSt()
                with patch("suite_workspace.resolve_workspace_id", return_value="daniel"):
                    aips.restore_applied_intelligence_disk_shell(daniel_st)
                self.assertEqual(daniel_st.session_state.get("ps_area_id"), "finance")
                self.assertEqual(
                    daniel_st.session_state.get("_suite_ai_question"),
                    "Daniel portfolio volatility question",
                )
                self.assertNotIn("Ariel", json.dumps(dict(daniel_st.session_state)))

                ariel_st = _FakeSt()
                with patch("suite_workspace.resolve_workspace_id", return_value="ariel"):
                    aips.restore_applied_intelligence_disk_shell(ariel_st)
                self.assertEqual(ariel_st.session_state.get("ps_area_id"), "sports")
                self.assertEqual(
                    ariel_st.session_state.get("_suite_ai_question"),
                    "Ariel sports trend question",
                )
                self.assertNotIn("Daniel", json.dumps(dict(ariel_st.session_state)))

    def test_persist_ui_state_writes_workspace_disk(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            data = Path(tmp)
            with patch("suite_workspace.DATA_DIR", data), patch("suite_user_persistence.DATA_DIR", data):
                st = _FakeSt()
                st.session_state["view_mode"] = "Home"
                with patch("suite_workspace.resolve_workspace_id", return_value="daniel"):
                    saved = aips.persist_applied_intelligence_ui_state(
                        st,
                        view_mode="Solve a Problem",
                        ps_area_id="finance",
                        ps_library_problem="What is my portfolio beta?",
                        reason="area_change",
                    )
                self.assertTrue(saved)
                blob = json.loads(
                    state_file_path("applied_intelligence", "daniel").read_text(encoding="utf-8")
                )
                self.assertEqual(blob["state"]["ps_area_id"], "finance")
                self.assertEqual(blob["state"]["view_mode"], "Solve a Problem")
                self.assertEqual(blob["state"]["ps_library_problem"], "What is my portfolio beta?")

    def test_autosave_writes_after_restore_block_cleared(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            data = Path(tmp)
            with patch("suite_workspace.DATA_DIR", data), patch("suite_user_persistence.DATA_DIR", data):
                st = _FakeSt()
                st.session_state["view_mode"] = "Solve a Problem"
                st.session_state["ps_area_id"] = "finance"
                st.session_state["_suite_autosave_blocked::applied_intelligence"] = True
                with patch("suite_workspace.resolve_workspace_id", return_value="daniel"):
                    aips.autosave_applied_intelligence_state(st)
                self.assertFalse(state_file_path("applied_intelligence", "daniel").exists())

                from suite_user_persistence import clear_workspace_autosave_block

                clear_workspace_autosave_block(st, "applied_intelligence")
                with patch("suite_workspace.resolve_workspace_id", return_value="daniel"):
                    aips.autosave_applied_intelligence_state(st)
                blob = json.loads(
                    state_file_path("applied_intelligence", "daniel").read_text(encoding="utf-8")
                )
                self.assertEqual(blob["state"]["ps_area_id"], "finance")


def test_control_state_persisted_and_restored() -> None:
    st = _FakeSt()
    st.session_state["ps_area_id"] = "sports"
    st.session_state["ami_solver_hr_rate_games"] = 12
    st.session_state["ps_sports_a1b2c3d4e5_ppp"] = 42

    state = aips.build_applied_intelligence_disk_state(st)

    assert "_ami_ui_state" in state
    assert "_ami_control_state" in state
    assert state["_ami_ui_state"]["ami_solver_hr_rate_games"] == 12
    assert state["_ami_ui_state"]["ps_sports_a1b2c3d4e5_ppp"] == 42

    fresh = _FakeSt()
    aips.apply_applied_intelligence_disk_state(fresh, state)
    assert fresh.session_state["ami_solver_hr_rate_games"] == 12
    assert fresh.session_state["ps_sports_a1b2c3d4e5_ppp"] == 42


def test_math_idea_explorer_ui_state_persisted_and_restored() -> None:
    st = _FakeSt()
    st.session_state["view_mode"] = "Explore a Math Idea"
    st.session_state["mie_example"] = "Expected value of a bet"
    st.session_state["mie_expected-value_iep"] = 55
    st.session_state["mie_expected-value_iew"] = 300.0

    state = aips.build_applied_intelligence_disk_state(st)

    assert state["view_mode"] == "Explore a Math Idea"
    assert state["ami_last_mie_input"] == "Expected value of a bet"
    assert state["_ami_ui_state"]["mie_example"] == "Expected value of a bet"
    assert state["_ami_ui_state"]["mie_expected-value_iep"] == 55

    fresh = _FakeSt()
    aips.apply_applied_intelligence_disk_state(fresh, state)
    assert fresh.session_state["view_mode"] == "Explore a Math Idea"
    assert fresh.session_state["mie_example"] == "Expected value of a bet"
    assert fresh.session_state["mie_expected-value_iep"] == 55


def test_scan_ami_session_keys_for_diagnostics() -> None:
    st = _FakeSt()
    st.session_state["mie_example"] = "Derivative as slope"
    st.session_state["ps_area_id"] = "finance"
    st.session_state["_suite_ai_question"] = "What is beta?"
    st.session_state["ami_solver_beta_ret"] = 1.2
    st.session_state["_ami_persistence_diag_ui"] = {"hidden": True}

    scan = aips.scan_ami_session_keys_for_diagnostics(st.session_state)

    assert "mie_example" in scan["matched_keys"]
    assert "ps_area_id" in scan["matched_keys"]
    assert "_suite_ai_question" in scan["matched_keys"]
    assert "ami_solver_beta_ret" in scan["persisted_keys"]
    assert "_ami_persistence_diag_ui" not in scan["matched_keys"]


def test_control_state_isolated_per_workspace() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        data = Path(tmp)
        with patch("suite_workspace.DATA_DIR", data), patch("suite_user_persistence.DATA_DIR", data):
            save_user_state(
                "applied_intelligence",
                {
                    "view_mode": "Solve a Problem",
                    "ps_area_id": "finance",
                    "_ami_control_state": {"ami_solver_beta_ret": -5.0},
                },
                workspace_id="daniel",
            )
            save_user_state(
                "applied_intelligence",
                {
                    "view_mode": "Solve a Problem",
                    "ps_area_id": "sports",
                    "_ami_control_state": {"ami_solver_beta_ret": 3.0},
                },
                workspace_id="ariel",
            )

            daniel_st = _FakeSt()
            with patch("suite_workspace.resolve_workspace_id", return_value="daniel"):
                aips.restore_applied_intelligence_disk_shell(daniel_st)
            assert daniel_st.session_state["ami_solver_beta_ret"] == -5.0

            ariel_st = _FakeSt()
            with patch("suite_workspace.resolve_workspace_id", return_value="ariel"):
                aips.restore_applied_intelligence_disk_shell(ariel_st)
            assert ariel_st.session_state["ami_solver_beta_ret"] == 3.0
