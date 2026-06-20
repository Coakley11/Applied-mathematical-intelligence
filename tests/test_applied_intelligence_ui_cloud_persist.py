"""Regression: Daniel AMI _ami_ui_state must reach cloud full_session."""

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


class TestAppliedIntelligenceUiCloudPersist(unittest.TestCase):
    def test_apply_stashes_restored_ui_blob(self) -> None:
        st = _FakeSt()
        saved = {
            "view_mode": "Explore a Math Idea",
            "_ami_ui_state": {"mie_example": "Derivative as slope", "mie_derivative_ida": 2.0},
        }
        aips.apply_applied_intelligence_disk_state(st, saved)
        self.assertEqual(st.session_state["mie_example"], "Derivative as slope")
        self.assertEqual(st.session_state["mie_derivative_ida"], 2.0)
        self.assertIn("mie_example", st.session_state[aips._RESTORED_UI_BLOB_KEY])

    def test_reapply_before_render_restores_widget_keys(self) -> None:
        st = _FakeSt()
        st.session_state[aips._RESTORED_UI_BLOB_KEY] = {
            "mie_example": "Expected value of a bet",
            "mie_expected-value_iep": 55,
        }
        st.session_state.pop("mie_example", None)
        aips.reapply_restored_ami_ui_state_before_render(st)
        self.assertEqual(st.session_state["mie_example"], "Expected value of a bet")
        self.assertEqual(st.session_state["mie_expected-value_iep"], 55)
        self.assertNotIn(aips._RESTORED_UI_BLOB_KEY, st.session_state)

    def test_reapply_does_not_clobber_user_widget_changes_on_later_rerun(self) -> None:
        st = _FakeSt()
        st.session_state[aips._RESTORED_UI_BLOB_KEY] = {"mie_expected-value_iep": 55}
        aips.reapply_restored_ami_ui_state_before_render(st)
        self.assertEqual(st.session_state["mie_expected-value_iep"], 55)

        st.session_state["mie_expected-value_iep"] = 70
        aips.reapply_restored_ami_ui_state_before_render(st)
        self.assertEqual(st.session_state["mie_expected-value_iep"], 70)

    def test_force_autosave_writes_ami_ui_state_to_cloud(self) -> None:
        st = _FakeSt()
        st.session_state["view_mode"] = "Explore a Math Idea"
        st.session_state["mie_example"] = "Derivative as slope"
        st.session_state["mie_derivative_ida"] = 3.0
        cloud_payloads: list[dict] = []

        def _capture_cloud(_app: str, state: dict, **_: object) -> bool:
            cloud_payloads.append(state)
            return True

        with patch("suite_workspace.resolve_workspace_id", return_value="daniel"), patch(
            "suite_user_persistence.save_user_state",
            return_value=True,
        ), patch("suite_cloud_state.save_cloud_full_session", side_effect=_capture_cloud), patch(
            "suite_cloud_state.load_cloud_full_session",
            return_value=({}, None),
        ), patch(
            "suite_cloud_state.session_page_summary",
            return_value=("Explore a Math Idea", "Derivative as slope"),
        ):
            saved = aips.persist_applied_intelligence_ui_state(st, reason="ui_change")

        self.assertTrue(saved)
        self.assertTrue(cloud_payloads)
        blob = cloud_payloads[0]
        self.assertIn("_ami_ui_state", blob)
        self.assertGreater(len(blob["_ami_ui_state"]), 0)
        self.assertEqual(blob["_ami_ui_state"]["mie_example"], "Derivative as slope")

    def test_maybe_persist_triggers_on_ui_signature_change(self) -> None:
        st = _FakeSt()
        st.session_state["view_mode"] = "Explore a Math Idea"
        st.session_state["mie_example"] = "Bayes rule"

        with patch(
            "applied_intelligence_persistent_state.persist_applied_intelligence_ui_state",
            return_value=True,
        ) as persist_mock:
            first = aips.maybe_persist_applied_intelligence_ui_changes(st)
            st.session_state["mie_custom"] = "P(A|B) example"
            second = aips.maybe_persist_applied_intelligence_ui_changes(st)

        self.assertTrue(first)
        persist_mock.assert_called()
        self.assertTrue(second)
        self.assertEqual(persist_mock.call_count, 2)


if __name__ == "__main__":
    unittest.main()
