"""Workspace query param must scope Ariel AMI cloud namespace."""

from __future__ import annotations

import unittest
from unittest.mock import patch

from suite_workspace import SESSION_KEY, init_suite_workspace, scoped_cloud_app_id


class _FakeSessionState(dict):
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

    def __setattr__(self, name, value):
        self[name] = value

    @property
    def query_params(self):
        return self.get("_query_params", {})


class _FakeSt:
    def __init__(self, query: dict | None = None) -> None:
        self.session_state = _FakeSessionState()
        if query:
            self.session_state["_query_params"] = query


class TestArielWorkspaceQueryParam(unittest.TestCase):
    def test_suite_workspace_ariel_scopes_cloud_key(self) -> None:
        st = _FakeSt({"suite_workspace": "ariel"})
        with patch("suite_workspace._qp_get", return_value="ariel"):
            ws = init_suite_workspace(st)
        self.assertEqual(ws, "ariel")
        self.assertEqual(st.session_state[SESSION_KEY], "ariel")
        self.assertEqual(
            scoped_cloud_app_id("applied_intelligence", "ariel"),
            "applied_intelligence__ariel",
        )


if __name__ == "__main__":
    unittest.main()
