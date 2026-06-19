"""Regression: developer UI only on Daniel workspace with dev mode enabled."""

from __future__ import annotations

import unittest

from suite_workspace import can_show_developer_tools, set_active_workspace_id


class _FakeSt:
    def __init__(self, workspace: str, *, dev_query: bool = False) -> None:
        self.session_state: dict = {}
        self.query_params = {"dev": "1"} if dev_query else {}
        set_active_workspace_id(self, workspace)  # type: ignore[arg-type]


class TestDeveloperWorkspaceGating(unittest.TestCase):
    def test_applied_math_developer_mode_ariel_blocked(self) -> None:
        from components.applied_math_context_diagnostics import applied_math_developer_mode_enabled

        st = _FakeSt("ariel", dev_query=True)
        st.session_state["app_developer_mode"] = True
        self.assertFalse(applied_math_developer_mode_enabled(st))  # type: ignore[arg-type]

    def test_applied_math_developer_mode_daniel_dev(self) -> None:
        from components.applied_math_context_diagnostics import applied_math_developer_mode_enabled

        st = _FakeSt("daniel", dev_query=True)
        self.assertTrue(applied_math_developer_mode_enabled(st))  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
